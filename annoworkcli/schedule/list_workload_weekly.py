import argparse
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.common.date_range import add_date_arguments, resolve_start_date
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_workload_daily import ParentJobAssignment, WorkloadMember, summarize_workloads
from annoworkcli.schedule.list_workload_weekly_by_user import ListWorkloadWeeklyByUser, WorkloadWeekly, get_week_end, get_week_start
from annoworkcli.schedule.workload_csv import get_parent_job_columns

logger = logging.getLogger(__name__)

CSV_COLUMNS = ["start_date", "end_date", "expected_working_hours", "assigned_working_hours", "remaining_working_hours"]
"""週別集計CSVの固定列。後ろに親ジョブ名の列を追加する。"""


@dataclass
class WorkloadWeeklySummary:
    start_date: str
    end_date: str
    expected_working_hours: float
    assigned_working_hours: float
    remaining_working_hours: float
    members: list[WorkloadMember]
    assignments: list[ParentJobAssignment]


def create_workload_csv(workloads: list[WorkloadWeeklySummary]) -> pandas.DataFrame:
    """親ジョブ名を列名とする、1週1行の比較表を作成する。"""
    jobs = get_parent_job_columns(
        ((assignment.parent_job_id, assignment.parent_job_name) for row in workloads for assignment in row.assignments), CSV_COLUMNS
    )
    rows = []
    for workload in workloads:
        row: list[str | float | None] = [
            workload.start_date,
            workload.end_date,
            workload.expected_working_hours,
            workload.assigned_working_hours,
            workload.remaining_working_hours,
        ]
        hours_by_job = {assignment.parent_job_id: assignment.assigned_working_hours for assignment in workload.assignments}
        row.extend(hours_by_job.get(job_id, 0.0) for job_id in jobs)
        rows.append(row)
    return pandas.DataFrame(rows, columns=[*CSV_COLUMNS, *jobs.values()])


class ListWorkloadWeekly:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.by_user = ListWorkloadWeeklyByUser(annowork_service, workspace_id)

    def get_workloads(self, *, start_date: str | None = None, end_date: str | None = None) -> list[WorkloadWeeklySummary]:
        """全ユーザーの時間を週別に集計し、データのない週も出力する。"""
        start_date = resolve_start_date(start_date, end_date)
        weekly: dict[str, list[WorkloadWeekly]] = defaultdict(list)
        for row in self.by_user.get_workloads(start_date=start_date, end_date=end_date):
            weekly[row.start_date].append(row)
        if end_date is None:
            if not weekly:
                return []
            end_date = max(weekly)
        result = []
        week = date.fromisoformat(get_week_start(start_date))
        last_week = date.fromisoformat(get_week_start(end_date))
        while week <= last_week:
            start = week.isoformat()
            summary = summarize_workloads(start, weekly[start])
            result.append(
                WorkloadWeeklySummary(
                    start,
                    get_week_end(start),
                    summary.expected_working_hours,
                    summary.assigned_working_hours,
                    summary.remaining_working_hours,
                    summary.members,
                    summary.assignments,
                )
            )
            week += timedelta(days=7)
        return result

    def main(self, *, start_date: str | None = None, end_date: str | None = None, output: Path | None, output_format: OutputFormat) -> None:
        logger.info(f"全ユーザーの週別アサイン状況を集計します。 :: {start_date=}, {end_date=}")
        result = self.get_workloads(start_date=start_date, end_date=end_date)
        if output_format == OutputFormat.JSON:
            print_json([asdict(row) for row in result], is_pretty=True, output=output)
        else:
            print_csv(create_workload_csv(result), output=output)
        logger.info(f"{len(result)} 件の週別アサイン状況を出力しました。")


def main(args: argparse.Namespace) -> None:
    ListWorkloadWeekly(build_annoworkapi(args), annoworkcli.common.cli.resolve_required_workspace_id(args)).main(
        start_date=resolve_start_date(args.start_date, args.end_date),
        end_date=args.end_date,
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = annoworkcli.common.cli.add_parser(
        subparsers, "list_workload_weekly", "全ユーザーの週別予定稼働時間と親ジョブ別アサイン時間を出力します。"
    )
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)
    add_date_arguments(parser)
    parser.add_argument("-o", "--output", type=Path, help="出力先。省略時は標準出力")
    parser.add_argument("-f", "--format", choices=[item.value for item in OutputFormat], default=OutputFormat.CSV.value, help="出力先のフォーマット")
    parser.set_defaults(subcommand_func=main)
    return parser

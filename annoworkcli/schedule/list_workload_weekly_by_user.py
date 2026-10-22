import argparse
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.date_range import add_date_arguments, resolve_start_date
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_workload_daily import summarize_workloads
from annoworkcli.schedule.list_workload_daily_by_user import Assignment, ListWorkloadDailyByUser, WorkloadDaily
from annoworkcli.schedule.workload_csv import get_parent_job_columns

logger = logging.getLogger(__name__)

CSV_COLUMNS = [
    "start_date",
    "end_date",
    "workspace_member_id",
    "user_id",
    "username",
    "expected_working_hours",
    "assigned_working_hours",
    "remaining_working_hours",
]
"""ユーザー別週次集計CSVの固定列。後ろに親ジョブ名の列を追加する。"""


@dataclass
class WorkloadWeekly:
    start_date: str
    end_date: str
    workspace_member_id: str
    user_id: str | None
    username: str | None
    expected_working_hours: float
    assigned_working_hours: float
    remaining_working_hours: float
    assignments: list[Assignment]


def get_week_start(value: str) -> str:
    """日付が属する週の日曜日を返す。"""
    day = date.fromisoformat(value)
    return (day - timedelta(days=(day.weekday() + 1) % 7)).isoformat()


def get_week_end(start_date: str) -> str:
    """週の開始日から土曜日を返す。"""
    return (date.fromisoformat(start_date) + timedelta(days=6)).isoformat()


def aggregate_workloads(daily: list[WorkloadDaily]) -> list[WorkloadWeekly]:
    """日別の換算済み時間を週・メンバー・親ジョブごとに合計する。"""
    groups: dict[tuple[str, str], list[WorkloadDaily]] = defaultdict(list)
    for row in daily:
        groups[get_week_start(row.date), row.workspace_member_id].append(row)
    result = []
    for (start, member_id), rows in sorted(groups.items()):
        summary = summarize_workloads(start, rows)
        member = rows[0]
        result.append(
            WorkloadWeekly(
                start,
                get_week_end(start),
                member_id,
                member.user_id,
                member.username,
                summary.expected_working_hours,
                summary.assigned_working_hours,
                summary.remaining_working_hours,
                [Assignment(item.parent_job_id, item.parent_job_name, item.assigned_working_hours) for item in summary.assignments],
            )
        )
    return result


def create_workload_csv(workloads: list[WorkloadWeekly]) -> pandas.DataFrame:
    """親ジョブ名を列名とする、週・メンバーごとの比較表を作成する。"""
    jobs = get_parent_job_columns(
        ((assignment.parent_job_id, assignment.parent_job_name) for row in workloads for assignment in row.assignments), CSV_COLUMNS
    )
    rows = []
    for workload in workloads:
        row: list[str | float | None] = [
            workload.start_date,
            workload.end_date,
            workload.workspace_member_id,
            workload.user_id,
            workload.username,
            workload.expected_working_hours,
            workload.assigned_working_hours,
            workload.remaining_working_hours,
        ]
        hours_by_job = {assignment.parent_job_id: assignment.assigned_working_hours for assignment in workload.assignments}
        row.extend(hours_by_job.get(job_id, 0.0) for job_id in jobs)
        rows.append(row)
    return pandas.DataFrame(rows, columns=[*CSV_COLUMNS, *jobs.values()])


class ListWorkloadWeeklyByUser:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def get_workloads(self, *, start_date: str | None = None, end_date: str | None = None, user_ids: list[str] | None = None) -> list[WorkloadWeekly]:
        """指定期間内の日次データを日曜始まりの週ごとに集計する。"""
        daily = ListWorkloadDailyByUser(self.annowork_service, self.workspace_id).get_workloads(
            start_date=start_date, end_date=end_date, user_ids=user_ids
        )
        return aggregate_workloads(daily)

    def main(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        user_ids: list[str] | None,
        output: Path | None,
        output_format: OutputFormat,
    ) -> None:
        rows = self.get_workloads(start_date=start_date, end_date=end_date, user_ids=user_ids)
        logger.info(f"{len(rows)} 件の週ごとのアサイン状況を出力します。")
        if output_format == OutputFormat.JSON:
            print_json([asdict(row) for row in rows], is_pretty=True, output=output)
        else:
            print_csv(create_workload_csv(rows), output=output)


def main(args: argparse.Namespace) -> None:
    ListWorkloadWeeklyByUser(build_annoworkapi(args), annoworkcli.common.cli.resolve_required_workspace_id(args)).main(
        start_date=resolve_start_date(args.start_date, args.end_date),
        end_date=args.end_date,
        user_ids=get_list_from_args(args.user_id),
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = annoworkcli.common.cli.add_parser(
        subparsers, "list_workload_weekly_by_user", "週・ユーザーごとのアサイン状況と親ジョブ別の内訳を出力します。"
    )
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)
    add_date_arguments(parser)
    parser.add_argument("-u", "--user_id", nargs="+", help="集計対象のユーザID")
    parser.add_argument("-o", "--output", type=Path, help="出力先。省略時は標準出力")
    parser.add_argument("-f", "--format", choices=[item.value for item in OutputFormat], default=OutputFormat.CSV.value, help="出力先のフォーマット")
    parser.set_defaults(subcommand_func=main)
    return parser

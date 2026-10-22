import argparse
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.common.date_range import add_date_arguments, resolve_start_date
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_workload_daily_by_user import ListWorkloadDailyByUser, WorkloadDaily, get_status
from annoworkcli.schedule.workload_csv import get_parent_job_columns

logger = logging.getLogger(__name__)

CSV_COLUMNS = ["date", "expected_working_hours", "assigned_working_hours", "remaining_working_hours"]
"""日別集計CSVの固定列。後ろに親ジョブ名の列を追加する。"""


@dataclass
class WorkloadMember:
    workspace_member_id: str
    user_id: str | None
    username: str | None
    expected_working_hours: float | None
    assigned_working_hours: float
    remaining_working_hours: float | None
    status: str


@dataclass
class AssignmentMember:
    workspace_member_id: str
    user_id: str | None
    username: str | None
    assigned_working_hours: float


@dataclass
class ParentJobAssignment:
    parent_job_id: str
    parent_job_name: str | None
    assigned_working_hours: float
    members: list[AssignmentMember]


@dataclass
class WorkloadDailySummary:
    date: str
    expected_working_hours: float
    assigned_working_hours: float
    remaining_working_hours: float
    members: list[WorkloadMember]
    assignments: list[ParentJobAssignment]


def summarize_workloads(date: str, workloads: list[WorkloadDaily]) -> WorkloadDailySummary:
    """ユーザー別の時間を日別・親ジョブ別に集計する。"""
    members = []
    job_members: dict[str, list[AssignmentMember]] = defaultdict(list)
    job_names: dict[str, str | None] = {}
    for row in sorted(workloads, key=lambda row: row.workspace_member_id):
        members.append(
            WorkloadMember(
                row.workspace_member_id,
                row.user_id,
                row.username,
                row.expected_working_hours,
                row.assigned_working_hours,
                row.remaining_working_hours,
                row.status,
            )
        )
        for assignment in row.assignments:
            job_names[assignment.parent_job_id] = assignment.parent_job_name
            job_members[assignment.parent_job_id].append(
                AssignmentMember(row.workspace_member_id, row.user_id, row.username, assignment.assigned_working_hours)
            )
    assignments = [
        ParentJobAssignment(job_id, job_names[job_id], sum(member.assigned_working_hours for member in details), details)
        for job_id, details in sorted(job_members.items())
    ]
    expected = sum(row.expected_working_hours for row in workloads if row.expected_working_hours is not None)
    assigned = sum(assignment.assigned_working_hours for assignment in assignments)
    remaining = 0.0 if get_status(expected, assigned) == "full" else expected - assigned
    return WorkloadDailySummary(date, expected, assigned, remaining, members, assignments)


def create_workload_csv(workloads: list[WorkloadDailySummary]) -> pandas.DataFrame:
    """親ジョブ名を列名とする、1日1行の比較表を作成する。"""
    jobs = get_parent_job_columns(
        ((assignment.parent_job_id, assignment.parent_job_name) for row in workloads for assignment in row.assignments), CSV_COLUMNS
    )
    rows = []
    for workload in workloads:
        row: dict[str, str | float | None] = {
            "date": workload.date,
            "expected_working_hours": workload.expected_working_hours,
            "assigned_working_hours": workload.assigned_working_hours,
            "remaining_working_hours": workload.remaining_working_hours,
        }
        hours_by_job = {assignment.parent_job_id: assignment.assigned_working_hours for assignment in workload.assignments}
        row.update({name: hours_by_job.get(job_id, 0.0) for job_id, name in jobs.items()})
        rows.append(row)
    return pandas.DataFrame(rows, columns=[*CSV_COLUMNS, *jobs.values()])


class ListWorkloadDaily:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.by_user = ListWorkloadDailyByUser(annowork_service, workspace_id)

    def get_workloads(self, *, start_date: str | None = None, end_date: str | None = None) -> list[WorkloadDailySummary]:
        """全ユーザーの時間を集計する。終了日省略時はデータの最終日まで返す。"""
        start_date = resolve_start_date(start_date, end_date)
        daily: dict[str, list[WorkloadDaily]] = defaultdict(list)
        for row in self.by_user.get_workloads(start_date=start_date, end_date=end_date):
            daily[row.date].append(row)
        if end_date is None:
            if not daily:
                return []
            end_date = max(daily)
        return [summarize_workloads(str(date.date()), daily[str(date.date())]) for date in pandas.date_range(start_date, end_date)]

    def main(self, *, start_date: str | None = None, end_date: str | None = None, output: Path | None, output_format: OutputFormat) -> None:
        logger.info(f"全ユーザーの日別アサイン状況を集計します。 :: {start_date=}, {end_date=}")
        result = self.get_workloads(start_date=start_date, end_date=end_date)
        if output_format == OutputFormat.JSON:
            print_json([asdict(row) for row in result], is_pretty=True, output=output)
        else:
            print_csv(create_workload_csv(result), output=output)
        logger.info(f"{len(result)} 件の日別アサイン状況を出力しました。")


def main(args: argparse.Namespace) -> None:
    ListWorkloadDaily(build_annoworkapi(args), annoworkcli.common.cli.resolve_required_workspace_id(args)).main(
        start_date=resolve_start_date(args.start_date, args.end_date),
        end_date=args.end_date,
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = annoworkcli.common.cli.add_parser(
        subparsers, "list_workload_daily", "全ユーザーの日別予定稼働時間と親ジョブ別アサイン時間を出力します。"
    )
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)
    add_date_arguments(parser)
    parser.add_argument("-o", "--output", type=Path, help="出力先。省略時は標準出力")
    parser.add_argument("-f", "--format", choices=[item.value for item in OutputFormat], default=OutputFormat.CSV.value, help="出力先のフォーマット")
    parser.set_defaults(subcommand_func=main)
    return parser

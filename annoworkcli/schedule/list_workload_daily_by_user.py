import argparse
import logging
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.date_range import add_date_arguments, resolve_start_date
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_schedule import ListSchedule, create_assigned_hours_dict
from annoworkcli.schedule.workload_csv import get_parent_job_columns

logger = logging.getLogger(__name__)

STATUSES = ["overloaded", "under_assigned", "unassigned", "full"]
"""予定稼働時間に対するアサイン状況。"""

CSV_COLUMNS = [
    "date",
    "workspace_member_id",
    "user_id",
    "username",
    "expected_working_hours",
    "assigned_working_hours",
    "remaining_working_hours",
    "status",
]
"""ユーザー別集計CSVの固定列。後ろに親ジョブ名の列を追加する。"""


@dataclass
class Assignment:
    parent_job_id: str
    parent_job_name: str | None
    assigned_working_hours: float


@dataclass
class WorkloadDaily:
    date: str
    workspace_member_id: str
    user_id: str | None
    username: str | None
    expected_working_hours: float
    assigned_working_hours: float
    remaining_working_hours: float
    status: str
    assignments: list[Assignment]


def create_workload_csv(workloads: list[WorkloadDaily]) -> pandas.DataFrame:
    """親ジョブ名を列名とする、日付・メンバーごとの比較表を作成する。"""
    jobs = get_parent_job_columns(
        ((assignment.parent_job_id, assignment.parent_job_name) for row in workloads for assignment in row.assignments), CSV_COLUMNS
    )
    rows = []
    for workload in workloads:
        row: dict[str, str | float | None] = {
            "date": workload.date,
            "workspace_member_id": workload.workspace_member_id,
            "user_id": workload.user_id,
            "username": workload.username,
            "expected_working_hours": workload.expected_working_hours,
            "assigned_working_hours": workload.assigned_working_hours,
            "remaining_working_hours": workload.remaining_working_hours,
            "status": workload.status,
        }
        hours_by_job = {assignment.parent_job_id: assignment.assigned_working_hours for assignment in workload.assignments}
        row.update({name: hours_by_job.get(job_id, 0.0) for job_id, name in jobs.items()})
        rows.append(row)
    return pandas.DataFrame(rows, columns=[*CSV_COLUMNS, *jobs.values()])


def get_status(expected: float, assigned: float) -> str:
    """予定稼働時間とアサイン時間から過不足を判定する。"""
    if math.isclose(assigned, expected, rel_tol=0, abs_tol=1e-9):
        return "full"
    if assigned > expected:
        return "overloaded"
    return "unassigned" if assigned == 0 else "under_assigned"


class ListWorkloadDailyByUser:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def get_workloads(self, *, start_date: str | None = None, end_date: str | None = None, user_ids: list[str] | None = None) -> list[WorkloadDaily]:
        """日付・メンバーごとの過不足と、全親ジョブのアサイン内訳を取得する。

        Args:
            start_date: 集計開始日。Noneならローカル日付の今日。
            end_date: 集計終了日。Noneなら終了日の制限なし。
            user_ids: 対象ユーザーID。Noneなら全ユーザー。
        """
        start_date = resolve_start_date(start_date, end_date)
        schedules = ListSchedule(self.annowork_service, self.workspace_id)
        members = {member["workspace_member_id"]: member for member in schedules.workspace_members}
        selected_members = None if user_ids is None else set(schedules.get_workspace_member_id_list_from_user_id(user_ids))
        expected_times = self.annowork_service.api.get_expected_working_times(
            self.workspace_id, query_params={"term_start": start_date, "term_end": end_date}
        )
        expected = {
            (entry["date"], entry["workspace_member_id"]): entry["expected_working_hours"]
            for entry in expected_times
            if entry["date"] >= start_date
            and (end_date is None or entry["date"] <= end_date)
            and (selected_members is None or entry["workspace_member_id"] in selected_members)
        }
        jobs = {job["job_id"]: job["job_name"] for job in self.annowork_service.api.get_jobs(self.workspace_id)}
        assignments: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
        for schedule in schedules.get_schedules(start_date=start_date, end_date=end_date, user_ids=user_ids):
            member_id = schedule["workspace_member_id"]
            parent_job_id = schedule["parent_job_id"]
            clipped_schedule = {
                **schedule,
                "start_date": max(start_date, schedule["start_date"]),
                "end_date": min(end_date, schedule["end_date"]) if end_date is not None else schedule["end_date"],
            }
            for date, hours in create_assigned_hours_dict(clipped_schedule, expected).items():
                if date < start_date or (end_date is not None and date > end_date):
                    continue
                key = (date, member_id)
                previous = assignments[key].get(parent_job_id, 0.0)
                assignments[key][parent_job_id] = previous + hours

        result = []
        for date, member_id in sorted(expected.keys() | assignments.keys()):
            key = (date, member_id)
            details = [Assignment(job_id, jobs.get(job_id), hours) for job_id, hours in sorted(assignments.get(key, {}).items())]
            expected_hours = expected.get(key, 0.0)
            assigned = sum(item.assigned_working_hours for item in details)
            status = get_status(expected_hours, assigned)
            remaining = 0.0 if status == "full" else expected_hours - assigned
            member = members.get(member_id, {})
            result.append(
                WorkloadDaily(
                    date,
                    member_id,
                    member.get("user_id"),
                    member.get("username"),
                    expected_hours,
                    assigned,
                    remaining,
                    status,
                    details,
                )
            )
        return result

    def main(
        self,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        user_ids: list[str] | None,
        statuses: list[str] | None,
        output: Path | None,
        output_format: OutputFormat,
    ) -> None:
        result = self.get_workloads(start_date=start_date, end_date=end_date, user_ids=user_ids)
        rows = [row for row in result if statuses is None or row.status in statuses]
        logger.info(f"{len(rows)} 件の日ごとのアサイン状況を出力します。")
        if output_format == OutputFormat.JSON:
            print_json([asdict(row) for row in rows], is_pretty=True, output=output)
        else:
            print_csv(create_workload_csv(rows), output=output)


def main(args: argparse.Namespace) -> None:
    ListWorkloadDailyByUser(build_annoworkapi(args), annoworkcli.common.cli.resolve_required_workspace_id(args)).main(
        start_date=resolve_start_date(args.start_date, args.end_date),
        end_date=args.end_date,
        user_ids=get_list_from_args(args.user_id),
        statuses=args.status,
        output=args.output,
        output_format=OutputFormat(args.format),
    )


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = annoworkcli.common.cli.add_parser(
        subparsers, "list_workload_daily_by_user", "日付・ユーザーごとのアサイン状況と親ジョブ別の内訳を出力します。"
    )
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)
    add_date_arguments(parser)
    parser.add_argument("-u", "--user_id", nargs="+", help="集計対象のユーザID")
    parser.add_argument("--status", nargs="+", choices=STATUSES, help="出力対象のアサイン状況")
    parser.add_argument("-o", "--output", type=Path, help="出力先。省略時は標準出力")
    parser.add_argument("-f", "--format", choices=[item.value for item in OutputFormat], default=OutputFormat.CSV.value, help="出力先のフォーマット")
    parser.set_defaults(subcommand_func=main)
    return parser

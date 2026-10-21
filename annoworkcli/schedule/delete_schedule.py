"""親ジョブ・ユーザー・開始日で選んだ作業計画を削除する。"""

import argparse
import datetime
import logging
from collections.abc import Collection

from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.delete_common import add_delete_arguments, delete_schedules
from annoworkcli.schedule.list_schedule import ListSchedule
from annoworkcli.schedule.write_common import WriteResult, validate_dates

logger = logging.getLogger(__name__)


def validate_options(from_start_date: str | None, to_start_date: str | None) -> None:
    for date in [from_start_date, to_start_date]:
        if date is not None:
            validate_dates(date, date)
    if from_start_date is not None and to_start_date is not None:
        validate_dates(from_start_date, to_start_date)


class DeleteSchedule:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str, *, all_yes: bool = False) -> None:
        self.service = annowork_service
        self.workspace_id = workspace_id
        self.all_yes = all_yes

    def main(
        self,
        *,
        parent_job_id: str,
        user_ids: Collection[str] | None = None,
        from_start_date: str | None = None,
        to_start_date: str | None = None,
        dry_run: bool = False,
    ) -> None:
        validate_options(from_start_date, to_start_date)
        today = datetime.datetime.now().astimezone().date().isoformat()
        logger.info(f"削除条件: {parent_job_id=}, {user_ids=}, {from_start_date=}, {to_start_date=}, 終了日が{today}以降")
        reader = ListSchedule(self.service, self.workspace_id)
        # APIは期間の重なり検索。今日以前に開始して継続中の計画も取得する。
        schedules = reader.get_schedules(start_date=today, parent_job_ids=[parent_job_id], user_ids=user_ids)
        schedules = [
            schedule
            for schedule in schedules
            if schedule["parent_job_id"] == parent_job_id
            and schedule["end_date"] >= today
            and (from_start_date is None or schedule["start_date"] >= from_start_date)
            and (to_start_date is None or schedule["start_date"] <= to_start_date)
        ]
        members = {member["workspace_member_id"]: member["user_id"] for member in reader.workspace_members}
        for schedule in schedules:
            schedule["user_id"] = members.get(schedule["workspace_member_id"])
        delete_schedules(self.service, self.workspace_id, schedules, all_yes=self.all_yes, dry_run=dry_run, result=WriteResult())


def main(args: argparse.Namespace) -> None:
    validate_options(args.from_start_date, args.to_start_date)
    workspace_id = cli.resolve_required_workspace_id(args)
    user_ids = cli.get_list_from_args(args.user_id)
    DeleteSchedule(cli.build_annoworkapi(args), workspace_id, all_yes=args.yes).main(
        parent_job_id=args.parent_job_id,
        user_ids=user_ids,
        from_start_date=args.from_start_date,
        to_start_date=args.to_start_date,
        dry_run=args.dry_run,
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    add_delete_arguments(parser)
    parser.add_argument("-pj", "--parent_job_id", required=True, help="削除対象のアサイン先の親ジョブID（1個）")
    parser.add_argument("-u", "--user_id", nargs="+", help="対象ユーザーID。複数指定、file://による一覧ファイルの指定が可能です。")
    parser.add_argument("--from_start_date", help="開始日の下限（YYYY-MM-DD、当日を含む）")
    parser.add_argument("--to_start_date", help="開始日の上限（YYYY-MM-DD、当日を含む）")
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = cli.add_parser(
        subparsers,
        "delete",
        "親ジョブ・ユーザー・開始日で選んだ作業計画を削除します。",
        description="終了日が実行環境のローカル日付で今日以降の作業計画全体を削除します。絞り込み条件はすべてANDです。",
    )
    parse_args(parser)
    return parser

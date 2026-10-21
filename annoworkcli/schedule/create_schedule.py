import argparse
import datetime
import logging
import uuid
from collections.abc import Collection

import requests
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.write_common import WriteResult, add_write_arguments, validate_assignment, validate_dates

logger = logging.getLogger(__name__)


class CreateSchedule:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str, *, all_yes: bool = False) -> None:
        self.service = annowork_service
        self.workspace_id = workspace_id
        self.all_yes = all_yes

    def main(
        self,
        *,
        parent_job_id: str,
        user_ids: Collection[str],
        end_date: str,
        start_date: str | None = None,
        hours: float | None = None,
        percentage: float | None = None,
    ) -> None:
        validate_assignment(hours, percentage)
        start_date = start_date if start_date is not None else datetime.datetime.now().astimezone().date().isoformat()
        validate_dates(start_date, end_date)
        user_ids = list(dict.fromkeys(user_ids))
        if not user_ids:
            raise ValueError("作成対象のuser_idを1件以上指定してください。")
        schedule_type = "hours" if hours is not None else "percentage"
        value = hours if hours is not None else (percentage if percentage is not None else 100)
        members = self.service.api.get_workspace_members(self.workspace_id)
        member_ids = {member["user_id"]: member["workspace_member_id"] for member in members}
        logger.info(f"{len(user_ids)} 人の作業計画を作成します。 :: {parent_job_id=}, {start_date=}, {end_date=}, {schedule_type=}, {value=}")
        result = WriteResult()
        if not self.all_yes and not cli.prompt_yesno(
            f"{len(user_ids)} 人の作業計画を作成しますか？ :: {parent_job_id=}, {user_ids=}, {start_date=}, {end_date=}, {schedule_type=}, {value=}"
        ):
            result.skipped = len(user_ids)
            result.finish()
            return
        for index, user_id in enumerate(user_ids, 1):
            result.log_progress(index, len(user_ids))
            member_id = member_ids.get(user_id)
            if member_id is None:
                logger.warning(f"{index} 件目: {user_id=} のワークスペースメンバーが存在しません。")
                result.failed += 1
                continue
            request_body = {
                # APIのjob_idには、アサイン先自身の親ジョブIDを渡す。
                "job_id": parent_job_id,
                "workspace_member_id": member_id,
                "start_date": start_date,
                "end_date": end_date,
                "type": schedule_type,
                "value": value,
            }
            message = f"{index} 件目: {user_id=}, {parent_job_id=}, {start_date=}, {end_date=}, {schedule_type=}, {value=}"
            schedule_id = str(uuid.uuid4())
            try:
                self.service.api.put_schedule(self.workspace_id, schedule_id, request_body=request_body)
            except requests.exceptions.RequestException:
                logger.warning(f"作業計画の作成に失敗しました。 :: {message}, {schedule_id=}", exc_info=True)
                result.failed += 1
                continue
            logger.info(f"作業計画を作成しました。 :: {message}, {schedule_id=}")
            result.success += 1
        result.finish()


def main(args: argparse.Namespace) -> None:
    validate_assignment(args.hours, args.percentage)
    start_date = args.start_date if args.start_date is not None else datetime.datetime.now().astimezone().date().isoformat()
    validate_dates(start_date, args.end_date)
    workspace_id = cli.resolve_required_workspace_id(args)
    user_ids = cli.get_list_from_args(args.user_id)
    assert user_ids is not None
    CreateSchedule(cli.build_annoworkapi(args), workspace_id, all_yes=args.yes).main(
        parent_job_id=args.parent_job_id,
        user_ids=user_ids,
        start_date=start_date,
        end_date=args.end_date,
        hours=args.hours,
        percentage=args.percentage,
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    cli.add_workspace_id_argument_with_env_fallback(parser)
    parser.add_argument("-pj", "--parent_job_id", required=True, help="アサイン先の親ジョブID（1個）。指定したIDをそのまま使用します。")
    parser.add_argument(
        "-u", "--user_id", nargs="+", required=True, help="作成対象のユーザーID。複数指定、file://による一覧ファイルの指定が可能です。"
    )
    parser.add_argument("--start_date", help="開始日（YYYY-MM-DD）。省略時は実行環境のローカル日付の今日です。")
    parser.add_argument("--end_date", required=True, help="終了日（YYYY-MM-DD、当日を含む）")
    add_write_arguments(parser)
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = cli.add_parser(
        subparsers,
        "create",
        "作業計画をユーザーごとに作成します。",
        description="作業計画をユーザーごとに作成します。割当量を省略すると予定稼働時間の100%を割り当てます。予定稼働時間が未登録の日の割当時間は0時間です。",
    )
    parse_args(parser)
    return parser

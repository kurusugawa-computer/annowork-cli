"""IDを指定して作業計画を削除する。"""

import argparse
import datetime
import logging
from collections.abc import Collection

import requests
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.delete_common import add_delete_arguments, delete_schedules
from annoworkcli.schedule.write_common import WriteResult

logger = logging.getLogger(__name__)


class DeleteScheduleByScheduleId:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str, *, all_yes: bool = False) -> None:
        self.service = annowork_service
        self.workspace_id = workspace_id
        self.all_yes = all_yes

    def main(self, schedule_ids: Collection[str], *, allow_past_end_date: bool = False, dry_run: bool = False) -> None:
        today = datetime.datetime.now().astimezone().date().isoformat()
        result = WriteResult()
        schedules = []
        logger.info(f"削除条件: {allow_past_end_date=}, ローカル日付の今日={today}")
        for index, schedule_id in enumerate(dict.fromkeys(schedule_ids), 1):
            result.log_progress(index, len(schedule_ids))
            try:
                schedule = self.service.api.get_schedule(self.workspace_id, schedule_id)
            except requests.exceptions.RequestException as error:
                if (
                    isinstance(error, requests.exceptions.HTTPError)
                    and error.response is not None
                    and error.response.status_code == requests.codes.not_found
                ):
                    logger.warning(f"{index} 件目: 作業計画が存在しないためスキップします。 :: {schedule_id=}", exc_info=True)
                    result.skipped += 1
                else:
                    logger.warning(f"{index} 件目: 作業計画の取得に失敗しました。 :: {schedule_id=}", exc_info=True)
                    result.failed += 1
                continue
            if not allow_past_end_date and schedule["end_date"] < today:
                logger.info(
                    f"{index} 件目: 終了日が昨日以前のためスキップします。 :: {schedule_id=}。削除する場合は--allow_past_end_dateを指定してください。"
                )
                result.skipped += 1
                continue
            schedules.append({**schedule, "schedule_id": schedule_id})
        delete_schedules(self.service, self.workspace_id, schedules, all_yes=self.all_yes, dry_run=dry_run, result=result)


def main(args: argparse.Namespace) -> None:
    workspace_id = cli.resolve_required_workspace_id(args)
    schedule_ids = cli.get_list_from_args(args.schedule_id)
    assert schedule_ids is not None
    DeleteScheduleByScheduleId(cli.build_annoworkapi(args), workspace_id, all_yes=args.yes).main(
        schedule_ids, allow_past_end_date=args.allow_past_end_date, dry_run=args.dry_run
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    add_delete_arguments(parser)
    parser.add_argument("--schedule_id", nargs="+", required=True, help="削除対象の作業計画ID。複数指定、file://による一覧ファイルの指定が可能です。")
    parser.add_argument("--allow_past_end_date", action="store_true", help="終了日が昨日以前の作業計画の削除も許可します。")
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = cli.add_parser(
        subparsers,
        "delete_by_schedule_id",
        "IDを指定して作業計画を削除します。",
        description="指定した作業計画全体を削除します。終了日が昨日以前の判定には実行環境のローカル日付を使用します。",
    )
    parse_args(parser)
    return parser

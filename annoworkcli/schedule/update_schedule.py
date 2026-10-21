import argparse
import logging
from collections.abc import Collection
from typing import Any

import requests
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.write_common import WriteResult, add_write_arguments, validate_assignment, validate_dates

logger = logging.getLogger(__name__)


def validate_update(start_date: str | None, end_date: str | None, hours: float | None, percentage: float | None) -> None:
    validate_assignment(hours, percentage)
    if all(value is None for value in [start_date, end_date, hours, percentage]):
        raise ValueError("更新する項目を1つ以上指定してください。")
    for date in [start_date, end_date]:
        if date is not None:
            validate_dates(date, date)
    if start_date is not None and end_date is not None:
        validate_dates(start_date, end_date)


class UpdateSchedule:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str, *, all_yes: bool = False) -> None:
        self.service = annowork_service
        self.workspace_id = workspace_id
        self.all_yes = all_yes

    def main(
        self,
        *,
        schedule_ids: Collection[str],
        start_date: str | None = None,
        end_date: str | None = None,
        hours: float | None = None,
        percentage: float | None = None,
    ) -> None:
        validate_update(start_date, end_date, hours, percentage)
        schedule_ids = list(dict.fromkeys(schedule_ids))
        if not schedule_ids:
            raise ValueError("更新対象のschedule_idを1件以上指定してください。")
        logger.info(f"{len(schedule_ids)} 件の作業計画を更新します。")
        result = WriteResult()
        if not self.all_yes and not cli.prompt_yesno(
            f"{len(schedule_ids)} 件の作業計画を更新しますか？ :: {schedule_ids=}, {start_date=}, {end_date=}, {hours=}, {percentage=}"
        ):
            result.skipped = len(schedule_ids)
            result.finish()
            return
        for index, schedule_id in enumerate(schedule_ids, 1):
            result.log_progress(index, len(schedule_ids))
            try:
                old = self.service.api.get_schedule(self.workspace_id, schedule_id)
                # APIで必要な項目のみ送信し、担当者とアサイン先は維持する。
                body: dict[str, Any] = {key: old[key] for key in ["job_id", "workspace_member_id", "start_date", "end_date", "type", "value"]}
                if start_date is not None:
                    body["start_date"] = start_date
                if end_date is not None:
                    body["end_date"] = end_date
                if hours is not None:
                    body.update(type="hours", value=hours)
                if percentage is not None:
                    body.update(type="percentage", value=percentage)
                validate_dates(body["start_date"], body["end_date"])
                changes = {key: {"before": old[key], "after": value} for key, value in body.items() if old[key] != value}
                if not changes:
                    logger.debug(f"{index} 件目: 変更がないためスキップします。 :: {schedule_id=}")
                    result.skipped += 1
                    continue
                message = (
                    f"{index} 件目: {schedule_id=}, parent_job_id='{old['job_id']}', workspace_member_id='{old['workspace_member_id']}', {changes=}"
                )
                body["last_updated_datetime"] = old["updated_datetime"]
                self.service.api.put_schedule(self.workspace_id, schedule_id, request_body=body)
            except (requests.exceptions.RequestException, ValueError):
                logger.warning(f"{index} 件目: 作業計画の更新に失敗しました。 :: {schedule_id=}", exc_info=True)
                result.failed += 1
                continue
            logger.debug(f"作業計画を更新しました。 :: {message}")
            result.success += 1
        result.finish()


def main(args: argparse.Namespace) -> None:
    validate_update(args.start_date, args.end_date, args.hours, args.percentage)
    workspace_id = cli.resolve_required_workspace_id(args)
    schedule_ids = cli.get_list_from_args(args.schedule_id)
    assert schedule_ids is not None
    UpdateSchedule(cli.build_annoworkapi(args), workspace_id, all_yes=args.yes).main(
        schedule_ids=schedule_ids, start_date=args.start_date, end_date=args.end_date, hours=args.hours, percentage=args.percentage
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    cli.add_workspace_id_argument_with_env_fallback(parser)
    parser.add_argument("--schedule_id", nargs="+", required=True, help="更新対象の作業計画ID。複数指定、file://による一覧ファイルの指定が可能です。")
    parser.add_argument("--start_date", help="変更後の開始日（YYYY-MM-DD）")
    parser.add_argument("--end_date", help="変更後の終了日（YYYY-MM-DD、当日を含む）")
    add_write_arguments(parser)
    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    parser = cli.add_parser(
        subparsers,
        "update",
        "作業計画の期間・割当量を更新します。",
        description="作業計画の期間・割当量を更新します。指定した項目のみ更新し、未指定の項目は維持します。",
    )
    parse_args(parser)
    return parser

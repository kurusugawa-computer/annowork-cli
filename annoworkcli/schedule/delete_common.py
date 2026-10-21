"""作業計画の削除に共通する確認・実行処理。"""

import argparse
import logging
from typing import Any

import requests
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.common import cli
from annoworkcli.schedule.write_common import WriteResult

logger = logging.getLogger(__name__)


def delete_schedules(
    service: AnnoworkResource,
    workspace_id: str,
    schedules: list[dict[str, Any]],
    *,
    all_yes: bool,
    dry_run: bool,
    result: WriteResult,
) -> None:
    """対象を表示し、一括確認後に作業計画全体を削除する。"""
    logger.info(f"削除対象: {len(schedules)} 件")
    for index, schedule in enumerate(schedules, 1):
        logger.info(f"{index} 件目: {schedule}")
    if not schedules:
        logger.info("削除する作業計画はありません。")
    elif dry_run:
        logger.info(f"dry_run: {len(schedules)} 件を削除予定です。")
        result.skipped += len(schedules)
    elif not all_yes and not cli.prompt_yesno(f"{len(schedules)} 件の作業計画全体を削除しますか？"):
        result.skipped += len(schedules)
    else:
        for index, schedule in enumerate(schedules, 1):
            result.log_progress(index, len(schedules))
            schedule_id = schedule["schedule_id"]
            try:
                service.api.delete_schedule(workspace_id, schedule_id)
            except requests.exceptions.RequestException:
                logger.warning(f"{index} 件目: 作業計画の削除に失敗しました。 :: {schedule_id=}", exc_info=True)
                result.failed += 1
                continue
            logger.debug(f"{index} 件目: 作業計画を削除しました。 :: {schedule_id=}")
            result.success += 1
    result.finish()


def add_delete_arguments(parser: argparse.ArgumentParser) -> None:
    cli.add_workspace_id_argument_with_env_fallback(parser)
    parser.add_argument("--dry_run", action="store_true", help="削除対象一覧と件数を表示して終了し、削除しません。")
    parser.add_argument("-y", "--yes", action="store_true", help="削除確認を省略します。")

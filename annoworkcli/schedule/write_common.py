"""作業計画の作成・更新で共通の入力検証と処理結果。"""

import argparse
import datetime
import logging
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def validate_assignment(hours: float | None, percentage: float | None) -> None:
    if hours is not None and percentage is not None:
        raise ValueError("hoursとpercentageは同時に指定できません。")
    for name, value, maximum in [("hours", hours, 24), ("percentage", percentage, 100)]:
        if value is not None and (not math.isfinite(value) or not 0.01 <= value <= maximum):
            raise ValueError(f"{name}は0.01以上{maximum}以下の有限の数値を指定してください。")


def validate_dates(start_date: str, end_date: str) -> None:
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    if start.isoformat() != start_date or end.isoformat() != end_date:
        raise ValueError("日付はYYYY-MM-DD形式で指定してください。")
    if start > end:
        raise ValueError("開始日は終了日以前にしてください。")


def add_write_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--hours", type=float, help="1人あたり・1日あたりの割当時間（0.01〜24時間）")
    group.add_argument("--percentage", type=float, help="各人の予定稼働時間に対する割当割合（0.01〜100%%）")
    parser.add_argument("-y", "--yes", action="store_true", help="すべての確認に自動的にyesと答えます。")


@dataclass
class WriteResult:
    """一括処理の結果。"""

    success: int = 0
    """書き込みに成功した件数。"""
    skipped: int = 0
    """確認で拒否した、または変更が不要だった件数。"""
    failed: int = 0
    """存在しない対象、不正な入力、APIエラーで失敗した件数。"""

    def log_progress(self, index: int, total: int) -> None:
        if index % 100 == 0:
            logger.info(f"{index} / {total} 件目を処理しています。")

    def finish(self) -> None:
        logger.info(f"成功: {self.success} 件、スキップ: {self.skipped} 件、失敗: {self.failed} 件")
        if self.failed:
            raise RuntimeError(f"{self.failed} 件の作業計画の処理に失敗しました。")

"""作業計画の一覧・集計コマンドで使う日付引数。"""

import argparse
import datetime

from annoworkcli.schedule.write_common import validate_dates


def resolve_start_date(start_date: str | None, end_date: str | None) -> str:
    """開始日の省略をローカル日付の今日で補い、指定期間を検証する。"""
    start_date = start_date if start_date is not None else datetime.datetime.now().astimezone().date().isoformat()
    validate_dates(start_date, end_date if end_date is not None else start_date)
    return start_date


def add_date_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start_date", default=resolve_start_date(None, None), help="取得・集計する範囲の開始日（YYYY-MM-DD、当日を含む）")
    parser.add_argument("--end_date", help="取得・集計する範囲の終了日（YYYY-MM-DD、当日を含む）")

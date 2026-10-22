"""一覧・集計コマンドで使う日付引数と期間検証。"""

import argparse
import datetime


def resolve_start_date(start_date: str | None, end_date: str | None) -> str:
    """開始日の省略をローカル日付の今日で補い、指定期間を検証する。"""
    start_date = start_date if start_date is not None else datetime.datetime.now().astimezone().date().isoformat()
    validate_dates(start_date, end_date if end_date is not None else start_date)
    return start_date


def add_date_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start_date", default=resolve_start_date(None, None), help="取得・集計する範囲の開始日（YYYY-MM-DD、当日を含む）")
    parser.add_argument("--end_date", help="取得・集計する範囲の終了日（YYYY-MM-DD、当日を含む）")


def validate_dates(start_date: str, end_date: str) -> None:
    start = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    if start.isoformat() != start_date or end.isoformat() != end_date:
        raise ValueError("日付はYYYY-MM-DD形式で指定してください。")
    if start > end:
        raise ValueError("開始日は終了日以前にしてください。")

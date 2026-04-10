import argparse
import logging
from pathlib import Path
from typing import Any

import pandas

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import create_actual_working_hours_daily_list, filter_actual_daily_list
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.type_util import assert_noreturn
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


def get_daily_total_actual_working_hours_df(actual_working_hours_daily_list: list[dict[str, Any]]) -> pandas.DataFrame:
    df = pandas.DataFrame(actual_working_hours_daily_list)
    if len(df) == 0:
        return pandas.DataFrame(columns=["date", "actual_working_hours"])

    df_total = (
        df.groupby("date", as_index=False)
        .agg({"actual_working_hours": "sum"})
        .query("actual_working_hours > 0")
        .sort_values("date")
    )

    return df_total[["date", "actual_working_hours"]]


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    if all(v is None for v in [job_id_list, parent_job_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。"
            "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    list_actual_working_time_obj = ListActualWorkingTime(
        annowork_service=annowork_service,
        workspace_id=args.workspace_id,
        timezone_offset_hours=args.timezone_offset,
    )
    actual_working_time_list = list_actual_working_time_obj.get_actual_working_times(
        job_ids=job_id_list,
        parent_job_ids=parent_job_id_list,
        user_ids=None,
        start_date=start_date,
        end_date=end_date,
        is_set_additional_info=False,
    )
    list_actual_working_time_obj.set_additional_info_to_actual_working_time(actual_working_time_list)

    logger.debug(f"{len(actual_working_time_list)} 件の実績作業時間情報を日ごとに集約します。")
    actual_daily_list = create_actual_working_hours_daily_list(
        actual_working_time_list,
        timezone_offset_hours=args.timezone_offset,
        show_notes=False,
    )
    actual_daily_list = filter_actual_daily_list(actual_daily_list, start_date=start_date, end_date=end_date)

    df = get_daily_total_actual_working_hours_df([e.to_dict() for e in actual_daily_list])

    logger.info(f"{len(df)} 件の日ごとの実績作業時間情報（合計）を出力します。")

    match OutputFormat(args.format):
        case OutputFormat.CSV:
            print_csv(df, output=args.output)
        case OutputFormat.JSON:
            print_json(df.to_dict("records"), is_pretty=True, output=args.output)
        case _ as unreachable:
            assert_noreturn(unreachable)


def parse_args(parser: argparse.ArgumentParser) -> None:
    required_group = parser.add_mutually_exclusive_group(required=True)

    required_group.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        help="対象のワークスペースID",
    )
    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="絞り込み対象のジョブID")
    job_id_group.add_argument("-pj", "--parent_job_id", type=str, nargs="+", required=False, help="絞り込み対象の親のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    parser.add_argument(
        "--timezone_offset",
        type=float,
        help="日付に対するタイムゾーンのオフセット時間。例えばJSTなら '9' です。指定しない場合はローカルのタイムゾーンを参照します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=[e.value for e in OutputFormat],
        help="出力先のフォーマット",
        default=OutputFormat.CSV.value,
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "list_daily_total"
    subcommand_help = "実績作業時間を日ごとに合計した情報を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

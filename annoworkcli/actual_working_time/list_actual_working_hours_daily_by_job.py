import argparse
import logging
from pathlib import Path
from typing import Any

import pandas
from annoworkapi.job import get_parent_job_id_from_job_tree

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import create_actual_working_hours_daily_list, filter_actual_daily_list
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.type_util import assert_noreturn
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


def get_daily_actual_working_hours_by_job_df(
    actual_working_hours_daily_list: list[dict[str, Any]],
    all_jobs: list[dict[str, Any]],
) -> pandas.DataFrame:
    required_columns = [
        "date",
        "parent_job_id",
        "parent_job_name",
        "job_id",
        "job_name",
        "actual_working_hours",
        "active_user_count",
    ]

    df = pandas.DataFrame(actual_working_hours_daily_list)
    if len(df) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_positive = df.query("actual_working_hours > 0")
    if len(df_positive) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_hours = (
        df_positive.groupby(["date", "job_id"], as_index=False)
        .agg({"actual_working_hours": "sum", "job_name": "first"})
        .sort_values(["date", "job_id"])
    )
    df_active_user = (
        df_positive.groupby(["date", "job_id"], as_index=False)
        .agg({"workspace_member_id": "nunique"})
        .rename(columns={"workspace_member_id": "active_user_count"})
    )
    df_total = df_hours.merge(df_active_user, on=["date", "job_id"], how="inner")

    all_job_dict = {e["job_id"]: e for e in all_jobs}

    def get_parent_job_id(job_id: str) -> str | None:
        job = all_job_dict.get(job_id)
        if job is None:
            return None
        return get_parent_job_id_from_job_tree(job["job_tree"])

    def get_parent_job_name(parent_job_id: str | None) -> str | None:
        if parent_job_id is None:
            return None
        parent_job = all_job_dict.get(parent_job_id)
        return parent_job["job_name"] if parent_job is not None else None

    df_total["parent_job_id"] = df_total["job_id"].map(get_parent_job_id)
    df_total["parent_job_name"] = df_total["parent_job_id"].map(get_parent_job_name)

    return df_total[required_columns]


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

    logger.debug(f"{len(actual_working_time_list)} 件の実績作業時間情報を日ごと・ジョブごとに集約します。")
    actual_daily_list = create_actual_working_hours_daily_list(
        actual_working_time_list,
        timezone_offset_hours=args.timezone_offset,
        show_notes=False,
    )
    actual_daily_list = filter_actual_daily_list(actual_daily_list, start_date=start_date, end_date=end_date)

    all_jobs = annowork_service.api.get_jobs(args.workspace_id)
    df = get_daily_actual_working_hours_by_job_df([e.to_dict() for e in actual_daily_list], all_jobs)

    logger.info(f"{len(df)} 件の日ごとの実績作業時間情報（ジョブごと）を出力します。")

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
    subcommand_name = "list_daily_by_job"
    subcommand_help = "実績作業時間を日ごと・ジョブごとに集計して出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

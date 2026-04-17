import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import pandas

import annoworkcli
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.type_util import assert_noreturn
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily

logger = logging.getLogger(__name__)


def get_daily_assigned_hours_by_job_df(assigned_hours_daily_list: list[dict[str, Any]]) -> pandas.DataFrame:
    required_columns = ["date", "job_id", "job_name", "assigned_working_hours", "active_user_count"]

    df = pandas.DataFrame(assigned_hours_daily_list)
    if len(df) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_positive = df.query("assigned_working_hours > 0")
    if len(df_positive) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_hours = (
        df_positive.groupby(["date", "job_id"], as_index=False)
        .agg({"assigned_working_hours": "sum", "job_name": "first"})
        .sort_values(["date", "job_id"])
    )
    df_active_user = (
        df_positive.groupby(["date", "job_id"], as_index=False)
        .agg({"workspace_member_id": "nunique"})
        .rename(columns={"workspace_member_id": "active_user_count"})
    )
    df_total = df_hours.merge(df_active_user, on=["date", "job_id"], how="inner")

    return df_total[required_columns]


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    start_date: str | None = args.start_date
    end_date: str | None = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(v is None for v in [job_id_list, start_date, end_date]):
        print(f"{command}: error: '--start_date'や'--job_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)  # noqa: T201
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    main_obj = ListAssignedHoursDaily(annowork_service=annowork_service, workspace_id=args.workspace_id)

    assigned_hours_daily_list = main_obj.get_assigned_hours_daily_list(
        start_date=start_date,
        end_date=end_date,
        job_ids=job_id_list,
        user_ids=None,
    )

    df = get_daily_assigned_hours_by_job_df([e.to_dict() for e in assigned_hours_daily_list])

    logger.info(f"{len(df)} 件の日ごとのアサイン時間情報（ジョブごと）を出力します。")

    match OutputFormat(args.format):
        case OutputFormat.CSV:
            print_csv(df, output=args.output)

        case OutputFormat.JSON:
            print_json(df.to_dict("records"), is_pretty=True, output=args.output)
        case _ as unreachable:
            assert_noreturn(unreachable)


def parse_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace_id",
        type=str,
        required=True,
        help="対象のワークスペースID",
    )

    parser.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="集計対象のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

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
    subcommand_help = "作業計画から求めたアサイン時間を日ごと・ジョブごとに集計して出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

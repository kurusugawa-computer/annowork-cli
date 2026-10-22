import argparse
import logging
from pathlib import Path
from typing import Any, assert_never

import pandas

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily
from annoworkcli.schedule.read_common import add_date_arguments, resolve_start_date

logger = logging.getLogger(__name__)


def get_daily_assigned_hours_by_parent_job_df(assigned_hours_daily_list: list[dict[str, Any]]) -> pandas.DataFrame:
    required_columns = ["date", "parent_job_id", "parent_job_name", "assigned_working_hours", "active_user_count"]

    df = pandas.DataFrame(assigned_hours_daily_list)
    if len(df) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_positive = df.query("assigned_working_hours > 0")
    if len(df_positive) == 0:
        return pandas.DataFrame(columns=required_columns)

    df_hours = (
        df_positive.groupby(["date", "parent_job_id"], as_index=False)
        .agg({"assigned_working_hours": "sum", "parent_job_name": "first"})
        .sort_values(["date", "parent_job_id"])
    )
    df_active_user = (
        df_positive.groupby(["date", "parent_job_id"], as_index=False)
        .agg({"workspace_member_id": "nunique"})
        .rename(columns={"workspace_member_id": "active_user_count"})
    )
    df_total = df_hours.merge(df_active_user, on=["date", "parent_job_id"], how="inner")

    return df_total[required_columns]


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    start_date = resolve_start_date(args.start_date, args.end_date)
    end_date: str | None = args.end_date

    main_obj = ListAssignedHoursDaily(annowork_service=annowork_service, workspace_id=workspace_id)

    assigned_hours_daily_list = main_obj.get_assigned_hours_daily_list(
        start_date=start_date,
        end_date=end_date,
        parent_job_ids=parent_job_id_list,
        user_ids=None,
    )

    df = get_daily_assigned_hours_by_parent_job_df([e.to_dict() for e in assigned_hours_daily_list])

    logger.info(f"{len(df)} 件の日ごとのアサイン時間情報（親ジョブごと）を出力します。")

    match OutputFormat(args.format):
        case OutputFormat.CSV:
            print_csv(df, output=args.output)

        case OutputFormat.JSON:
            print_json(df.to_dict("records"), is_pretty=True, output=args.output)
        case _ as unreachable:
            assert_never(unreachable)


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument("-pj", "--parent_job_id", type=str, nargs="+", required=False, help="集計対象の親ジョブID")

    add_date_arguments(parser)

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
    subcommand_name = "list_daily_by_parent_job"
    subcommand_help = "作業計画から求めたアサイン時間を日ごと・親ジョブごとに集計して出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers,
        subcommand_name,
        subcommand_help,
        description=subcommand_help,
    )
    parse_args(parser)
    return parser

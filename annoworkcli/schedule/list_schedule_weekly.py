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


def get_weekly_assigned_hours_df(assigned_hours_daily_list: list[dict[str, Any]], workspace_members: list[dict[str, Any]]) -> pandas.DataFrame:
    """週単位のアサイン時間が格納されたDataFrameを生成します。

    Args:
        assigned_hours_daily_list: 日ごとのアサイン時間情報。
            date, workspace_member_id, parent_job_id, parent_job_name, assigned_working_hours を参照します。
        workspace_members: ワークスペースメンバ情報。workspace_member_id, user_id, username を参照します。

    Returns:
        以下の列を返すDataFrame。
            "workspace_member_id", "user_id","username", "parent_job_id", "parent_job_name", "start_date", "end_date", "assigned_working_hours"
    """
    df = pandas.DataFrame(assigned_hours_daily_list)
    # 1週間ごとに集計する（日曜日始まり, 日曜日がindexになっている）
    df["dt_date"] = pandas.to_datetime(df["date"])

    df_weekly = (
        # `include_groups=False`を指定する理由：pandas2.2.0で以下の警告が出ないようにするため
        # DeprecationWarning: DataFrameGroupBy.resample operated on the grouping columns.
        # This behavior is deprecated, and in a future version of pandas the grouping columns will be excluded from the operation.
        # Either pass `include_groups=False` to exclude the groupings or explicitly select the grouping columns after groupby to silence this warning.  # noqa: E501
        df.groupby(["workspace_member_id", "parent_job_id", "parent_job_name"])
        .resample("W-SUN", on="dt_date", label="left", closed="left", include_groups=False)
        .agg({"assigned_working_hours": "sum"})
    )
    df_weekly.reset_index(inplace=True)

    # 1週間の始まり（日曜日）と終わり（土曜日）の日付列を設定
    df_weekly.rename(columns={"dt_date": "dt_start_date"}, inplace=True)
    df_weekly["dt_end_date"] = df_weekly["dt_start_date"] + pandas.Timedelta(days=6)
    # pandas.Timestamp型をstr型に変換する
    df_weekly["start_date"] = df_weekly["dt_start_date"].dt.date.apply(lambda e: e.isoformat())
    df_weekly["end_date"] = df_weekly["dt_end_date"].dt.date.apply(lambda e: e.isoformat())

    # アサイン時間が0の行は不要なので、除外する
    df_weekly = df_weekly.query("assigned_working_hours > 0")

    df_workspace_member = pandas.DataFrame(workspace_members)

    df = df_weekly.merge(df_workspace_member, on="workspace_member_id", how="left")
    df.sort_values(["user_id", "parent_job_id", "start_date"], inplace=True)

    return df[["workspace_member_id", "user_id", "username", "parent_job_id", "parent_job_name", "start_date", "end_date", "assigned_working_hours"]]


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    user_id_list = get_list_from_args(args.user_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    start_date = resolve_start_date(args.start_date, args.end_date)
    end_date: str | None = args.end_date

    main_obj = ListAssignedHoursDaily(annowork_service=annowork_service, workspace_id=workspace_id)

    assigned_hours_daily_list = main_obj.get_assigned_hours_daily_list(
        start_date=start_date,
        end_date=end_date,
        parent_job_ids=parent_job_id_list,
        user_ids=user_id_list,
    )

    # AssignedHoursDailyオブジェクトのリストをdictのリストに変換
    assigned_hours_daily_dict_list = [e.to_dict() for e in assigned_hours_daily_list]

    required_columns = [
        "workspace_member_id",
        "user_id",
        "username",
        "parent_job_id",
        "parent_job_name",
        "start_date",
        "end_date",
        "assigned_working_hours",
    ]
    if len(assigned_hours_daily_dict_list) == 0:
        df = pandas.DataFrame(columns=required_columns)
    else:
        df = get_weekly_assigned_hours_df(assigned_hours_daily_dict_list, main_obj.list_schedule_obj.workspace_members)
        df = df[required_columns]

    logger.info(f"{len(df)} 件の週単位のアサイン時間情報を出力します。")

    match OutputFormat(args.format):
        case OutputFormat.CSV:
            print_csv(df, output=args.output)

        case OutputFormat.JSON:
            print_json(df.to_dict("records"), is_pretty=True, output=args.output)
        case _ as unreachable:
            assert_never(unreachable)


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="集計対象のユーザID")

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
    subcommand_name = "list_weekly"
    subcommand_help = "作業計画から求めたアサイン時間を週ごと（日曜日始まり）に出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers,
        subcommand_name,
        subcommand_help,
        description=subcommand_help,
    )
    parse_args(parser)
    return parser

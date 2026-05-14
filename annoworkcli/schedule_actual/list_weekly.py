import argparse
import logging
from pathlib import Path

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.schedule_actual.common import WEEKLY_COLUMNS, build_weekly_schedule_actual_df, get_daily_schedule_actual_df, print_df

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    daily_df = get_daily_schedule_actual_df(
        annowork_service=annowork_service,
        workspace_id=workspace_id,
        parent_job_id=args.parent_job_id,
        start_date=args.start_date,
        end_date=args.end_date,
        timezone_offset_hours=args.timezone_offset,
    )
    df = build_weekly_schedule_actual_df(daily_df)
    logger.info(f"{len(df)} 件の週ごとの予定・実績作業時間情報を出力します。")
    print_df(df[WEEKLY_COLUMNS], output=args.output, output_format=OutputFormat(args.format))


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)
    parser.add_argument(
        "-pj",
        "--parent_job_id",
        type=str,
        required=True,
        help="集計対象の親ジョブID",
    )
    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")
    parser.add_argument(
        "--timezone_offset",
        type=float,
        help="日付に対するタイムゾーンのオフセット時間を指定します。例えばJSTなら '9' です。指定しない場合はローカルのタイムゾーンを参照します。",
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
    subcommand_name = "list_weekly"
    subcommand_help = "前日までの実績と当日以降の予定を結合した週ごとの作業時間を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

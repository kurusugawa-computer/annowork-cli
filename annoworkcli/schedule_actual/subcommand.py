import argparse

import annoworkcli
import annoworkcli.common.cli
import annoworkcli.schedule_actual.list_daily
import annoworkcli.schedule_actual.list_weekly


def parse_args(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand_name")

    annoworkcli.schedule_actual.list_daily.add_parser(subparsers)
    annoworkcli.schedule_actual.list_weekly.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "schedule_actual"
    subcommand_help = "予定と実績を結合した作業時間関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False)
    parse_args(parser)
    return parser


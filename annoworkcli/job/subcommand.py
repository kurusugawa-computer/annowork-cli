import argparse

import annoworkcli
import annoworkcli.common.cli
import annoworkcli.job.delete_job
import annoworkcli.job.list_job
import annoworkcli.job.update_job_status


def parse_args(parser: argparse.ArgumentParser):  # noqa: ANN201
    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.job.delete_job.add_parser(subparsers)
    annoworkcli.job.list_job.add_parser(subparsers)
    annoworkcli.job.update_job_status.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "job"
    subcommand_help = "ジョブ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False)
    parse_args(parser)
    return parser

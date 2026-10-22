import argparse

import annoworkcli
import annoworkcli.annofab.create_job_from_annofab_project
import annoworkcli.annofab.list_assigned_hours
import annoworkcli.annofab.list_job_with_annofab_project
import annoworkcli.annofab.list_working_hours
import annoworkcli.annofab.reshape_working_hours
import annoworkcli.annofab.set_account_external_linkage_info
import annoworkcli.annofab.visualize_statistics
import annoworkcli.common.cli


def parse_args(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.annofab.create_job_from_annofab_project.add_parser(subparsers)
    annoworkcli.annofab.list_assigned_hours.add_parser(subparsers)
    annoworkcli.annofab.list_job_with_annofab_project.add_parser(subparsers)
    annoworkcli.annofab.list_working_hours.add_parser(subparsers)
    annoworkcli.annofab.reshape_working_hours.add_parser(subparsers)
    annoworkcli.annofab.set_account_external_linkage_info.add_parser(subparsers)
    annoworkcli.annofab.visualize_statistics.add_parser(subparsers)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "annofab"
    subcommand_help = "Annofab連携に関するサブコマンド"
    description = (
        "Annofab連携に関するサブコマンド\n"
        "Annofab APIにアクセスする操作ではAnnofabの認証情報が必要です。\n"
        "list_assigned_hours、および--actual_file指定時のreshape_working_hoursではAnnofabの認証は不要です。"
    )

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description, is_subcommand=False)
    parse_args(parser)
    return parser

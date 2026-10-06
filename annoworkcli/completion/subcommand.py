import argparse
import sys

import shtab

import annoworkcli.common.cli

SHELL_CHOICES = ["bash", "fish", "powershell", "tcsh", "zsh"]
"""補完スクリプトを生成できるシェル。"""


def main(args: argparse.Namespace) -> None:
    """シェル補完スクリプトを標準出力に出力します。"""
    sys.stdout.write(shtab.complete(args.root_parser, shell=args.shell))


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    """completionコマンドのパーサーを追加します。"""
    parser = annoworkcli.common.cli.add_parser(subparsers, "completion", "指定したシェル用の補完スクリプトを標準出力に書き出します。")
    parser.add_argument("shell", choices=SHELL_CHOICES, help="補完スクリプトを生成するシェルを指定します。")
    parser.set_defaults(subcommand_func=main, skip_logging=True)
    return parser

import argparse
import logging

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class UpdateWorkspace:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ) -> None:
        self.annowork_service = annowork_service

    def main(self, workspace_id: str, workspace_name: str | None = None, email: str | None = None) -> None:
        if workspace_name is None and email is None:
            raise ValueError("更新する項目を1つ以上指定してください。")
        org = self.annowork_service.wrapper.get_workspace_or_none(workspace_id)

        if org is None:
            raise ValueError(f"ワークスペース {workspace_id} は存在しません。")
        request_body = {
            "workspace_name": workspace_name if workspace_name is not None else org["workspace_name"],
            "email": email if email is not None else org["email"],
            "last_updated_datetime": org["updated_datetime"],
        }

        self.annowork_service.api.put_workspace(workspace_id, request_body=request_body)

        logger.info(f"ワークスペース {workspace_id} を更新しました。")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)

    UpdateWorkspace(
        annowork_service=annowork_service,
    ).main(workspace_id=workspace_id, workspace_name=args.workspace_name, email=args.email)


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument(
        "--workspace_name",
        type=str,
        required=False,
        help="ワークスペース名",
    )

    parser.add_argument(
        "--email",
        type=str,
        required=False,
        help="ワークスペース管理者のe-mailアドレス",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "update"
    subcommand_help = "ワークスペースを更新します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers,
        subcommand_name,
        subcommand_help,
        description=subcommand_help + "\n指定した項目のみ更新し、未指定の項目は維持します。少なくとも1項目を指定してください。",
    )
    parse_args(parser)
    return parser

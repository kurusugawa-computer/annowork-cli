import argparse
import logging
import uuid

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class CreateWorkspaceTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, workspace_tag_name: str, workspace_tag_id: str | None = None) -> None:
        workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)

        if workspace_tag_id is None:
            workspace_tag_id = str(uuid.uuid4())

        if any(tag["workspace_tag_id"] == workspace_tag_id for tag in workspace_tags):
            raise ValueError(f"ワークスペースタグ {workspace_tag_id} は既に存在します。")
        request_body = {"workspace_tag_name": workspace_tag_name}

        self.annowork_service.api.put_workspace_tag(self.workspace_id, workspace_tag_id, request_body=request_body)
        logger.info(f"ワークスペースタグを作成しました。 :: {workspace_tag_id=}, {workspace_tag_name=}")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    CreateWorkspaceTag(annowork_service=annowork_service, workspace_id=workspace_id).main(
        workspace_tag_name=args.workspace_tag_name, workspace_tag_id=args.workspace_tag_id
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument(
        "--workspace_tag_name",
        type=str,
        required=True,
        help="作成対象のワークスペースタグの名前",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        required=False,
        help="作成するワークスペースタグのID。省略時はUUIDを生成します。",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "create"
    subcommand_help = "ワークスペースタグを作成します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

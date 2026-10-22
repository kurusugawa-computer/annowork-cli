import argparse
import logging

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class UpdateWorkspaceTag:
    def __init__(self, annowork_service: AnnoworkResource, workspace_id: str) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, workspace_tag_name: str, workspace_tag_id: str) -> None:
        workspace_tags = self.annowork_service.api.get_workspace_tags(self.workspace_id)

        old_workspace_tag = next((tag for tag in workspace_tags if tag["workspace_tag_id"] == workspace_tag_id), None)
        if old_workspace_tag is None:
            raise ValueError(f"ワークスペースタグ {workspace_tag_id} は存在しません。")
        request_body = {"workspace_tag_name": workspace_tag_name, "last_updated_datetime": old_workspace_tag["updated_datetime"]}

        self.annowork_service.api.put_workspace_tag(self.workspace_id, workspace_tag_id, request_body=request_body)
        logger.info(f"ワークスペースタグを更新しました。 :: {workspace_tag_id=}, {workspace_tag_name=}")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    UpdateWorkspaceTag(annowork_service=annowork_service, workspace_id=workspace_id).main(
        workspace_tag_name=args.workspace_tag_name, workspace_tag_id=args.workspace_tag_id
    )


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument(
        "--workspace_tag_name",
        type=str,
        required=True,
        help="更新対象のワークスペースタグの名前",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        required=True,
        help="更新対象のワークスペースタグのID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "update"
    subcommand_help = "ワークスペースタグを更新します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=subcommand_help)
    parse_args(parser)
    return parser

import argparse
import logging
import uuid
from collections.abc import Collection

from annoworkapi.enums import Role
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
import annoworkcli.common.cli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class CreateWorkspaceMember:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        workspace_id: str,
    ) -> None:
        self.annowork_service = annowork_service
        self.workspace_id = workspace_id

    def main(self, user_id_list: Collection[str], role: str, workspace_tag_id_list: Collection[str] | None) -> None:
        workspace_members = self.annowork_service.api.get_workspace_members(self.workspace_id, query_params={"includes_inactive_members": True})
        existing_user_ids = {m["user_id"] for m in workspace_members}
        user_id_list = list(dict.fromkeys(user_id_list))
        success_count = 0
        skipped_count = 0
        failed_count = 0
        logger.info(f"{len(user_id_list)} 件のワークスペースメンバを作成します。")
        for index, user_id in enumerate(user_id_list, 1):
            if index % 100 == 0:
                logger.info(f"{index}/{len(user_id_list)} 件目を処理しています。")
            if user_id in existing_user_ids:
                logger.warning(f"{index} 件目: {user_id=} は既に登録されているので、スキップします。脱退済みメンバも再招待しません。")
                skipped_count += 1
                continue
            workspace_member_id = str(uuid.uuid4())
            request_body = {
                "user_id": user_id,
                "role": role,
                "workspace_tags": list(workspace_tag_id_list) if workspace_tag_id_list is not None else [],
            }
            try:
                self.annowork_service.api.put_workspace_member(self.workspace_id, workspace_member_id, request_body=request_body)
                logger.debug(f"{index} 件目: {user_id=} のワークスペースメンバを作成しました。 :: {workspace_member_id=}")
                success_count += 1
            except Exception:
                logger.warning(f"{index} 件目: {user_id=}: ワークスペースメンバの作成に失敗しました。", exc_info=True)
                failed_count += 1

        logger.info(f"成功: {success_count} 件、スキップ: {skipped_count} 件、失敗: {failed_count} 件")
        if failed_count:
            raise RuntimeError(f"{failed_count} 件のワークスペースメンバの作成に失敗しました。")


def main(args: argparse.Namespace) -> None:
    annowork_service = build_annoworkapi(args)
    workspace_id = annoworkcli.common.cli.resolve_required_workspace_id(args)
    user_id_list = get_list_from_args(args.user_id)
    workspace_tag_id_list = get_list_from_args(args.workspace_tag_id)
    assert user_id_list is not None
    CreateWorkspaceMember(
        annowork_service=annowork_service,
        workspace_id=workspace_id,
    ).main(user_id_list=user_id_list, role=args.role, workspace_tag_id_list=workspace_tag_id_list)


def parse_args(parser: argparse.ArgumentParser) -> None:
    annoworkcli.common.cli.add_workspace_id_argument_with_env_fallback(parser)

    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        required=True,
        help="作成対象のuser_id。既存メンバと脱退済みメンバはスキップします。",
    )

    parser.add_argument(
        "--role",
        type=str,
        choices=[e.value for e in Role],
        required=True,
        help="権限",
    )

    parser.add_argument(
        "-wt",
        "--workspace_tag_id",
        type=str,
        nargs="+",
        required=False,
        help="新規メンバに付与するワークスペースタグID。省略時はタグを付与しません。",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    subcommand_name = "create"
    subcommand_help = "ワークスペースメンバを作成します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers,
        subcommand_name,
        subcommand_help,
        description=subcommand_help
        + "\n既存メンバと脱退済みメンバはスキップします。権限の更新にはupdate_role、タグの変更にはappend_tag/remove_tagを使用してください。",
    )
    parse_args(parser)
    return parser

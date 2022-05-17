"""
workspace_tag に関するutil関係の関数
"""
from __future__ import annotations

from typing import Optional

workspace_TAG_NAME_COMPANY_PREFIX = "company:"
"""会社名を表す組織タグ名のプレフィックス"""


def is_company_from_workspace_tag_name(workspace_tag_name: str) -> bool:
    """組織タグ名が会社情報を表すかどうかを返します。"""
    return workspace_tag_name.startswith(workspace_TAG_NAME_COMPANY_PREFIX)


def get_company_from_workspace_tag_name(workspace_tag_name: str) -> Optional[str]:
    """組織タグ名から会社情報を取得します。
    タグ名のプレフィックスが `company:` でない場合はNoneを返します。
    """
    if not workspace_tag_name.startswith(workspace_TAG_NAME_COMPANY_PREFIX):
        return None
    return workspace_tag_name[len(workspace_TAG_NAME_COMPANY_PREFIX) :]

import pytest

from annoworkcli.workspace_tag.update_workspace_tag import UpdateWorkspaceTag


def test_既存タグの名前を競合検出付きで更新する(service):
    service.api.get_workspace_tags.return_value = [
        {"workspace_tag_id": "other", "updated_datetime": "other-version"},
        {"workspace_tag_id": "tag", "updated_datetime": "version"},
    ]
    UpdateWorkspaceTag(service, "ws").main("新しい名前", "tag")
    service.api.put_workspace_tag.assert_called_once_with(
        "ws", "tag", request_body={"workspace_tag_name": "新しい名前", "last_updated_datetime": "version"}
    )


def test_存在しないタグを作成しない(service):
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "other"}]
    with pytest.raises(ValueError):
        UpdateWorkspaceTag(service, "ws").main("名前", "missing")
    service.api.put_workspace_tag.assert_not_called()

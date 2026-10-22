import uuid

import pytest

from annoworkcli.workspace_tag.create_workspace_tag import CreateWorkspaceTag


@pytest.mark.parametrize("tag_id", ["new", None])
def test_新規タグを作成しID省略時はUUIDを生成する(service, tag_id):
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "existing"}]
    CreateWorkspaceTag(service, "ws").main("名前", tag_id)
    call = service.api.put_workspace_tag.call_args
    assert call.args[0] == "ws"
    if tag_id is None:
        uuid.UUID(call.args[1])
    else:
        assert call.args[1] == tag_id
    assert call.kwargs["request_body"] == {"workspace_tag_name": "名前"}


def test_既存タグを上書きしない(service):
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "existing"}]
    with pytest.raises(ValueError):
        CreateWorkspaceTag(service, "ws").main("新しい名前", "existing")
    service.api.put_workspace_tag.assert_not_called()

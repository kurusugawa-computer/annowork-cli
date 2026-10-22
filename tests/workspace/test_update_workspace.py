import pytest
import requests

from annoworkcli.workspace.update_workspace import UpdateWorkspace


@pytest.fixture
def existing_service(service):
    service.wrapper.get_workspace_or_none.return_value = {"workspace_name": "既存", "email": "old@example.com", "updated_datetime": "version"}
    return service


@pytest.mark.parametrize(
    "changes", [{"workspace_name": "新しい名前"}, {"email": "new@example.com"}, {"workspace_name": "名前", "email": "new@example.com"}]
)
def test_指定項目だけを変更し競合検出用の日時を送信する(existing_service, changes):
    old = existing_service.wrapper.get_workspace_or_none.return_value.copy()
    UpdateWorkspace(existing_service).main("ws", **changes)
    body = existing_service.api.put_workspace.call_args.kwargs["request_body"]
    assert body == {"workspace_name": old["workspace_name"], "email": old["email"], **changes, "last_updated_datetime": old["updated_datetime"]}
    assert existing_service.wrapper.get_workspace_or_none.return_value == old


def test_存在しないワークスペースを作成しない(service):
    service.wrapper.get_workspace_or_none.return_value = None
    with pytest.raises(ValueError):
        UpdateWorkspace(service).main("missing", workspace_name="名前")
    service.api.put_workspace.assert_not_called()


def test_更新項目なしでは書き込まない(service):
    with pytest.raises(ValueError):
        UpdateWorkspace(service).main("ws")
    service.api.put_workspace.assert_not_called()


def test_競合時に作成へ切り替えない(existing_service):
    existing_service.api.put_workspace.side_effect = requests.HTTPError()
    with pytest.raises(requests.HTTPError):
        UpdateWorkspace(existing_service).main("ws", workspace_name="名前")
    assert existing_service.api.put_workspace.call_count == 1

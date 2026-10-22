import pytest

from annoworkcli.workspace.create_workspace import CreateWorkspace


def test_存在しないワークスペースだけを作成する(service):
    service.wrapper.get_workspace_or_none.return_value = None
    CreateWorkspace(service).main("ws", "名前", "alice@example.com")
    service.api.put_workspace.assert_called_once_with("ws", request_body={"workspace_name": "名前", "email": "alice@example.com"})


def test_既存ワークスペースは上書きしない(service):
    service.wrapper.get_workspace_or_none.return_value = {"workspace_name": "既存"}
    with pytest.raises(ValueError):
        CreateWorkspace(service).main("ws", "名前", "alice@example.com")
    service.api.put_workspace.assert_not_called()

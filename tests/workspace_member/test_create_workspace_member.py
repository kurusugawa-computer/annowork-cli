from unittest.mock import MagicMock

import pytest
import requests
from annoworkapi.resource import Resource

from annoworkcli.workspace_member.create_workspace_member import CreateWorkspaceMember


@pytest.fixture
def service():
    result = MagicMock(spec=Resource)
    result.api = MagicMock()
    result.api.get_workspace_members.return_value = [
        {"user_id": "existing", "workspace_member_id": "member", "role": "owner"},
        {"user_id": "inactive", "workspace_member_id": "inactive-member", "role": "worker", "active": False},
    ]
    return result


@pytest.mark.parametrize("tags", [None, ["tag"]])
def test_既存と脱退済みメンバは変更せず新規ユーザーだけを追加する(service, tags, caplog):
    caplog.set_level("INFO")
    CreateWorkspaceMember(service, "ws").main(["existing", "new", "inactive", "new"], "worker", tags)
    calls = service.api.put_workspace_member.call_args_list
    assert len(calls) == 1
    assert calls[0].kwargs["request_body"] == {"user_id": "new", "role": "worker", "workspace_tags": tags or []}
    # 脱退済みメンバの見落としによる再招待を防ぐ。
    service.api.get_workspace_members.assert_called_once_with("ws", query_params={"includes_inactive_members": True})
    assert "成功: 1 件、スキップ: 2 件、失敗: 0 件" in caplog.text


def test_APIエラー後も残りを作成し失敗を報告する(service, caplog):
    service.api.put_workspace_member.side_effect = [requests.HTTPError(), {}]
    with pytest.raises(RuntimeError):
        CreateWorkspaceMember(service, "ws").main(["bad", "good"], "worker", None)
    assert service.api.put_workspace_member.call_count == 2
    assert service.api.put_workspace_member.call_args.kwargs["request_body"]["user_id"] == "good"
    assert any(record.exc_info for record in caplog.records)

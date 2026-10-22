from copy import deepcopy
from unittest.mock import MagicMock

import pytest
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.resource import Resource

from annoworkcli.annofab.set_account_external_linkage_info import SetAnnofabAccountId


@pytest.mark.parametrize("old_account_id", [None, "old"])
@pytest.mark.parametrize("overwrite", [True, False])
def test_設定済みの上書きを制御し他の連携項目を維持する(old_account_id, overwrite):
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.wrapper = MagicMock()
    info = {"other": {"key": "value"}, "annofab": {"extra": "keep"}}
    if old_account_id is not None:
        info["annofab"]["account_id"] = old_account_id
    original = deepcopy(info)
    service.wrapper.get_account_external_linkage_info_or_none.return_value = {"updated_datetime": "version", "external_linkage_info": info}
    command = SetAnnofabAccountId(annowork_service=service, annofab_service=MagicMock(spec=AnnofabResource), overwrite=overwrite)
    expected = old_account_id is None or overwrite
    assert command.set_account_annofab_info_for_user("alice", "new") is expected
    if expected:
        service.api.put_account_external_linkage_info.assert_called_once_with(
            "alice",
            request_body={
                "external_linkage_info": {"other": {"key": "value"}, "annofab": {"extra": "keep", "account_id": "new"}},
                "last_updated_datetime": "version",
            },
        )
    else:
        service.api.put_account_external_linkage_info.assert_not_called()
    assert info == original


def test_連携情報がないユーザーには書き込まない():
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.wrapper = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.return_value = None
    command = SetAnnofabAccountId(annowork_service=service, annofab_service=MagicMock(spec=AnnofabResource), overwrite=True)
    assert command.set_account_annofab_info_for_user("missing", "new") is False
    service.api.put_account_external_linkage_info.assert_not_called()


def test_Annofabの項目がない場合も他の連携情報を維持して追加する():
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.wrapper = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.return_value = {
        "updated_datetime": "version",
        "external_linkage_info": {"other": {"id": "keep"}},
    }
    command = SetAnnofabAccountId(annowork_service=service, annofab_service=MagicMock(spec=AnnofabResource), overwrite=False)
    assert command.set_account_annofab_info_for_user("alice", "new") is True
    body = service.api.put_account_external_linkage_info.call_args.kwargs["request_body"]
    assert body["external_linkage_info"] == {"other": {"id": "keep"}, "annofab": {"account_id": "new"}}


def test_一括設定では未所属と設定済みをスキップして残りを処理する(caplog):
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.wrapper = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.side_effect = [
        {"updated_datetime": "old-version", "external_linkage_info": {"annofab": {"account_id": "old"}}},
        {"updated_datetime": "version", "external_linkage_info": {}},
    ]
    annofab = MagicMock(spec=AnnofabResource)
    annofab.wrapper = MagicMock()
    annofab.wrapper.get_all_organization_members.return_value = [
        {"user_id": "existing", "account_id": "id"},
        {"user_id": "new", "account_id": "new-id"},
    ]
    caplog.set_level("INFO")
    command = SetAnnofabAccountId(annowork_service=service, annofab_service=annofab, overwrite=False)
    command.main("organization", ["missing", "existing", "new", "new"])
    service.api.put_account_external_linkage_info.assert_called_once_with(
        "new", request_body={"external_linkage_info": {"annofab": {"account_id": "new-id"}}, "last_updated_datetime": "version"}
    )
    assert "成功: 1 件、スキップ: 2 件、失敗: 0 件" in caplog.text

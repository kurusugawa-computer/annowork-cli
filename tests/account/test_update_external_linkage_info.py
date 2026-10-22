from unittest.mock import MagicMock

from annoworkapi.resource import Resource

from annoworkcli.account.update_external_linkage_info import UpdateExternalLinkageInfo


def test_存在しない連携情報を新規作成しない():
    service = MagicMock(spec=Resource)
    service.wrapper = MagicMock()
    service.api = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.return_value = None
    UpdateExternalLinkageInfo(service).main("alice", {"annofab": {"account_id": "id"}})
    service.api.put_account_external_linkage_info.assert_not_called()


def test_連携情報を指定内容で置き換える():
    service = MagicMock(spec=Resource)
    service.wrapper = MagicMock()
    service.api = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.return_value = {"updated_datetime": "version", "external_linkage_info": {"old": {}}}
    info = {"annofab": {"account_id": "id"}}
    UpdateExternalLinkageInfo(service).main("alice", info)
    service.api.put_account_external_linkage_info.assert_called_once_with(
        "alice", request_body={"external_linkage_info": info, "last_updated_datetime": "version"}
    )

import json
from unittest.mock import MagicMock

import pytest

from annoworkcli.account.list_external_linkage_info import ListExternalLinkageInfo
from annoworkcli.common.cli import OutputFormat


def test_main_skips_missing_account_and_continues(capsys):
    service = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.side_effect = [None, {"account_id": "account-2"}]

    ListExternalLinkageInfo(service).main(user_id_list=["missing", "existing"], output=None, output_format=OutputFormat.JSON)

    assert json.loads(capsys.readouterr().out) == [{"account_id": "account-2", "user_id": "existing"}]


def test_main_propagates_api_error():
    service = MagicMock()
    service.wrapper.get_account_external_linkage_info_or_none.side_effect = RuntimeError("API error")

    with pytest.raises(RuntimeError, match="API error"):
        ListExternalLinkageInfo(service).main(user_id_list=["user"], output=None, output_format=OutputFormat.JSON)

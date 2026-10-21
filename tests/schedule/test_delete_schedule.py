from unittest.mock import MagicMock, call

import pytest
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.schedule.delete_schedule import DeleteSchedule

pytestmark = pytest.mark.usefixtures("fixed_local_datetime")


@pytest.mark.parametrize("target_user_ids", [None, ["alice"], ["bob"]])
def test_指定した親ジョブとユーザーに一致する作業計画だけを削除する(target_user_ids):
    service = MagicMock(spec=AnnoworkResource)
    service.api = MagicMock()
    service.api.get_jobs.return_value = []
    service.api.get_workspace_members.return_value = [{"workspace_member_id": "member", "user_id": "alice"}]
    service.api.get_schedule.side_effect = [
        {"job_id": parent_job_id, "workspace_member_id": "member", "start_date": "2026-10-01", "end_date": "2026-10-01"}
        for parent_job_id in ["parent1", "parent2"]
    ]
    DeleteSchedule(service, "workspace", all_yes=True).delete_schedule(
        ["schedule1", "schedule2"], target_parent_job_ids=["parent1"], target_user_ids=target_user_ids, allow_past_end_date=True
    )
    expected = [] if target_user_ids == ["bob"] else [call("workspace", "schedule1")]
    assert service.api.delete_schedule.call_args_list == expected


@pytest.mark.parametrize("allow_past_end_date", [False, True])
def test_終了済み計画は許可時のみ削除し今日以降終了する計画は削除する(service, allow_past_end_date, caplog):
    caplog.set_level("INFO")
    end_dates = ["2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22"]
    service.api.get_schedule.side_effect = [
        {"job_id": "parent", "workspace_member_id": "member", "start_date": "2026-10-01", "end_date": end_date} for end_date in end_dates
    ]
    DeleteSchedule(service, "workspace", all_yes=True).delete_schedule(end_dates, allow_past_end_date=allow_past_end_date)
    expected = end_dates if allow_past_end_date else end_dates[2:]
    assert [call.args[1] for call in service.api.delete_schedule.call_args_list] == expected
    if not allow_past_end_date:
        assert "--allow_past_end_date" in caplog.text


def test_終了済み計画は確認せずスキップする(service, monkeypatch):
    service.api.get_schedule.return_value = {
        "job_id": "parent",
        "workspace_member_id": "member",
        "start_date": "2026-10-01",
        "end_date": "2026-10-20",
    }

    def unexpected_input(_message):
        pytest.fail("終了済み計画では削除確認しない")

    monkeypatch.setattr("builtins.input", unexpected_input)
    DeleteSchedule(service, "workspace", all_yes=False).delete_schedule(["past"])
    service.api.delete_schedule.assert_not_called()

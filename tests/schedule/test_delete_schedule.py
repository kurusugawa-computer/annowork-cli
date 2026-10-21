from unittest.mock import MagicMock, call

import pytest
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.schedule.delete_schedule import DeleteSchedule


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
        ["schedule1", "schedule2"], target_parent_job_ids=["parent1"], target_user_ids=target_user_ids
    )
    expected = [] if target_user_ids == ["bob"] else [call("workspace", "schedule1")]
    assert service.api.delete_schedule.call_args_list == expected

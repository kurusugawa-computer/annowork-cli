import datetime
from unittest.mock import MagicMock, patch

import pytest
from annoworkapi.resource import Resource as AnnoworkResource


@pytest.fixture
def service():
    result = MagicMock(spec=AnnoworkResource)
    result.api = MagicMock()
    result.api.get_workspace_members.return_value = [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice"}]
    result.api.get_jobs.return_value = [
        {"job_id": "parent", "job_name": "Parent", "job_tree": "workspace/grandparent/parent"},
        {"job_id": "grandparent", "job_name": "Grandparent", "job_tree": "workspace/grandparent"},
    ]
    result.api.get_schedules.return_value = [
        {
            "workspace_id": "workspace",
            "schedule_id": "schedule",
            "job_id": "parent",
            "workspace_member_id": "member",
            "start_date": "2026-10-01",
            "end_date": "2026-10-01",
            "type": "hours",
            "value": 3.0,
        }
    ]
    result.api.get_expected_working_times.return_value = []
    return result


@pytest.fixture
def fixed_local_datetime():
    """実行日によって書き込み系テストの日付条件が変わらないようにする。"""
    now = datetime.datetime(2026, 10, 21, 0, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    with patch("datetime.datetime", side_effect=datetime.datetime) as clock:
        clock.now.return_value.astimezone.return_value = now
        yield

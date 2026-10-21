from unittest.mock import MagicMock

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

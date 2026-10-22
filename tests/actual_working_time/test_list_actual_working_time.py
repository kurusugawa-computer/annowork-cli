from unittest.mock import MagicMock

import pytest
from annoworkapi.resource import Resource

from annoworkcli.actual_working_time.list_actual_working_hours_daily_groupby_tag import ListActualWorkingTimeGroupbyTag
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime


@pytest.fixture
def service():
    result = MagicMock(spec=Resource)
    result.api = MagicMock()
    result.api.get_workspace_members.return_value = [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice"}]
    result.api.get_jobs.return_value = [{"job_id": "job", "job_name": "Job", "job_tree": "workspace/job"}]
    result.api.get_actual_working_times.return_value = [
        {
            "workspace_member_id": "member",
            "job_id": "job",
            "actual_working_time_id": "actual",
            "start_datetime": "2026-10-01T00:00:00.000Z",
            "end_datetime": "2026-10-01T08:00:00.000Z",
            "note": "",
        }
    ]
    return result


@pytest.mark.parametrize("additional_info", [False, True])
def test_追加情報の指定に応じて生データまたは補完済みデータを返す(service, additional_info):
    original = dict(service.api.get_actual_working_times.return_value[0])
    rows = ListActualWorkingTime(service, "workspace", timezone_offset_hours=0).get_actual_working_times(
        is_set_additional_info=additional_info,
    )
    assert len(rows) == 1
    if additional_info:
        assert rows[0] == {**original, "user_id": "alice", "username": "Alice", "job_name": "Job", "actual_working_hours": 8.0}
        service.api.get_jobs.assert_called_once()
    else:
        assert rows == [original]
        service.api.get_jobs.assert_not_called()


def test_タグ別日次集計に必要な追加情報を取得する(service):
    rows = ListActualWorkingTimeGroupbyTag(service, "workspace", timezone_offset_hours=0).get_actual_working_hours_daily(
        start_date="2026-10-01",
        end_date="2026-10-01",
    )
    assert len(rows) == 1
    assert rows[0].user_id == "alice"
    assert rows[0].username == "Alice"
    assert rows[0].job_name == "Job"
    assert rows[0].actual_working_hours == 8.0

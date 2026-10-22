import json
from unittest.mock import MagicMock

import pandas
import pytest
from annoworkapi.resource import Resource

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily
from annoworkcli.schedule.list_assigned_hours_daily_groupby_tag import ListAssignedHoursDailyGroupbyTag


@pytest.mark.parametrize("tag_name", ["total", "by_tag", "Team"])
@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("selected_tags", [None, ["tag"], ["unknown"]])
def test_全体合計とタグ別集計を分離して出力する(tmp_path, tag_name, output_format, selected_tags):
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.api.get_workspace_members.return_value = [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice"}]
    service.api.get_jobs.return_value = [
        {"job_id": "parent", "job_name": "Parent", "job_tree": "workspace/parent"},
        {"job_id": "job", "job_name": "Job", "job_tree": "workspace/parent/job"},
    ]
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "tag", "workspace_tag_name": tag_name}]
    service.api.get_workspace_tag_members.return_value = [{"workspace_member_id": "member"}]
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 8.0}]
    service.api.get_schedules.return_value = [
        {
            "schedule_id": "schedule",
            "job_id": "parent",
            "workspace_member_id": "member",
            "start_date": "2026-10-01",
            "end_date": "2026-10-01",
            "type": "hours",
            "value": 8.0,
        }
    ]
    service.api.get_actual_working_times.return_value = [
        {
            "actual_working_time_id": "actual",
            "job_id": "job",
            "workspace_member_id": "member",
            "start_datetime": "2026-10-01T00:00:00Z",
            "end_datetime": "2026-10-01T08:00:00Z",
            "note": "",
        }
    ]
    output = tmp_path / "result"
    command = ListAssignedHoursDailyGroupbyTag(service, "workspace")
    command.main(
        output=output,
        output_format=output_format,
        start_date="2026-10-01",
        end_date="2026-10-01",
        parent_job_id_list=None,
        user_id_list=None,
        target_workspace_tag_ids=selected_tags,
        target_workspace_tag_names=None,
    )
    has_tag = selected_tags != ["unknown"]
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
        assert len(rows) == 1
        assert rows[0]["assigned_working_hours"] == {"total": 8.0, "by_tag": {tag_name: 8.0} if has_tag else {}}
    else:
        frame = pandas.read_csv(output)
        assert len(frame) == 1
        assert frame.loc[0, "assigned_working_hours.total"] == 8.0
        if has_tag:
            assert frame.loc[0, f"assigned_working_hours.by_tag.{tag_name}"] == 8.0
        else:
            assert not any(column.startswith("assigned_working_hours.by_tag.") for column in frame.columns)


def test_タグ集計に親ジョブIDと名前を出力する(service):
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "tag", "workspace_tag_name": "Team"}]
    service.api.get_workspace_tag_members.return_value = [{"workspace_member_id": "member"}]
    assigned = ListAssignedHoursDaily(service, "workspace").get_assigned_hours_daily_list(parent_job_ids=["parent"])
    actual = ListAssignedHoursDailyGroupbyTag(service, "workspace").get_assigned_hours_groupby_tag(assigned)
    assert actual == [
        {
            "date": "2026-10-01",
            "parent_job_id": "parent",
            "parent_job_name": "Parent",
            "assigned_working_hours": {"total": 3.0, "by_tag": {"Team": 3.0}},
        }
    ]

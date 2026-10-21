from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily
from annoworkcli.schedule.list_assigned_hours_daily_groupby_tag import ListAssignedHoursDailyGroupbyTag


def test_タグ集計に親ジョブIDと名前を出力する(service):
    service.api.get_workspace_tags.return_value = [{"workspace_tag_id": "tag", "workspace_tag_name": "Team"}]
    service.api.get_workspace_tag_members.return_value = [{"workspace_member_id": "member"}]
    assigned = ListAssignedHoursDaily(service, "workspace").get_assigned_hours_daily_list(parent_job_ids=["parent"])
    actual = ListAssignedHoursDailyGroupbyTag(service, "workspace").get_assigned_hours_groupby_tag(assigned)
    assert actual == [
        {"date": "2026-10-01", "parent_job_id": "parent", "parent_job_name": "Parent", "assigned_working_hours": {"Team": 3.0, "total": 3.0}}
    ]

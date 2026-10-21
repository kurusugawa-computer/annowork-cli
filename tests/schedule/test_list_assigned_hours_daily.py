from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily


def test_アサイン先自身のIDと名前を日次結果に設定する(service):
    actual = ListAssignedHoursDaily(service, "workspace").get_assigned_hours_daily_list(parent_job_ids=["parent"], user_ids=["alice"])
    assert [row.to_dict() for row in actual] == [
        {
            "date": "2026-10-01",
            "parent_job_id": "parent",
            "parent_job_name": "Parent",
            "workspace_member_id": "member",
            "user_id": "alice",
            "username": "Alice",
            "assigned_working_hours": 3.0,
        }
    ]

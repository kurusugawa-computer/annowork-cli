from annoworkcli.schedule.list_assigned_hours_daily_total import get_daily_total_assigned_hours_df

ASSIGNED_HOURS_DAILY_LIST = [
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "assigned_working_hours": 1,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "bob",
        "job_id": "job2",
        "assigned_working_hours": 2,
    },
    {
        "date": "2022-03-06",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "assigned_working_hours": 3,
    },
    {
        "date": "2022-03-07",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "assigned_working_hours": 0,
    },
]


def test_get_daily_total_assigned_hours_df():
    actual = get_daily_total_assigned_hours_df(ASSIGNED_HOURS_DAILY_LIST)

    assert list(actual.columns) == ["date", "assigned_working_hours"]
    assert len(actual) == 2
    assert actual.query("date == '2022-03-05'").iloc[0]["assigned_working_hours"] == 3
    assert actual.query("date == '2022-03-06'").iloc[0]["assigned_working_hours"] == 3

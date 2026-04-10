from annoworkcli.actual_working_time.list_actual_working_hours_daily_total import get_daily_total_actual_working_hours_df

ACTUAL_WORKING_HOURS_DAILY_LIST = [
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "actual_working_hours": 1,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "bob",
        "job_id": "job2",
        "actual_working_hours": 2,
    },
    {
        "date": "2022-03-06",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "actual_working_hours": 3,
    },
    {
        "date": "2022-03-07",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "actual_working_hours": 0,
    },
]


def test_get_daily_total_actual_working_hours_df():
    actual = get_daily_total_actual_working_hours_df(ACTUAL_WORKING_HOURS_DAILY_LIST)

    assert list(actual.columns) == ["date", "actual_working_hours"]
    assert len(actual) == 2
    assert actual.query("date == '2022-03-05'").iloc[0]["actual_working_hours"] == 3
    assert actual.query("date == '2022-03-06'").iloc[0]["actual_working_hours"] == 3

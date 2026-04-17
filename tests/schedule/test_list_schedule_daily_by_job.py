from annoworkcli.schedule.list_assigned_hours_daily_by_job import get_daily_assigned_hours_by_job_df

ASSIGNED_HOURS_DAILY_LIST = [
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "assigned_working_hours": 1,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "assigned_working_hours": 2,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "bob",
        "job_id": "job1",
        "job_name": "Job 1",
        "assigned_working_hours": 3,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "charlie",
        "job_id": "job2",
        "job_name": "Job 2",
        "assigned_working_hours": 4,
    },
    {
        "date": "2022-03-06",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "assigned_working_hours": 0,
    },
]


def test_get_daily_assigned_hours_by_job_df():
    actual = get_daily_assigned_hours_by_job_df(ASSIGNED_HOURS_DAILY_LIST)

    assert list(actual.columns) == ["date", "job_id", "job_name", "assigned_working_hours", "active_user_count"]
    assert len(actual) == 2

    job1 = actual.query("date == '2022-03-05' and job_id == 'job1'").iloc[0]
    assert job1["assigned_working_hours"] == 6
    assert job1["active_user_count"] == 2

    job2 = actual.query("date == '2022-03-05' and job_id == 'job2'").iloc[0]
    assert job2["assigned_working_hours"] == 4
    assert job2["active_user_count"] == 1

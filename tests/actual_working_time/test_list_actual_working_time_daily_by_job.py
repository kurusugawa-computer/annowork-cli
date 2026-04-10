import pandas

from annoworkcli.actual_working_time.list_actual_working_hours_daily_by_job import get_daily_actual_working_hours_by_job_df

ACTUAL_WORKING_HOURS_DAILY_LIST = [
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "actual_working_hours": 1,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "actual_working_hours": 2,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "bob",
        "job_id": "job1",
        "job_name": "Job 1",
        "actual_working_hours": 3,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "charlie",
        "job_id": "job2",
        "job_name": "Job 2",
        "actual_working_hours": 4,
    },
    {
        "date": "2022-03-06",
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Job 1",
        "actual_working_hours": 0,
    },
]

ALL_JOBS = [
    {"job_id": "parent1", "job_name": "Parent 1", "job_tree": "/parent1"},
    {"job_id": "job1", "job_name": "Job 1", "job_tree": "/parent1/job1"},
    {"job_id": "job2", "job_name": "Job 2", "job_tree": "/job2"},
]


def test_get_daily_actual_working_hours_by_job_df():
    actual = get_daily_actual_working_hours_by_job_df(ACTUAL_WORKING_HOURS_DAILY_LIST, ALL_JOBS)

    assert list(actual.columns) == [
        "date",
        "parent_job_id",
        "parent_job_name",
        "job_id",
        "job_name",
        "actual_working_hours",
        "active_user_count",
    ]
    assert len(actual) == 2

    job1 = actual.query("date == '2022-03-05' and job_id == 'job1'").iloc[0]
    assert job1["actual_working_hours"] == 6
    assert job1["active_user_count"] == 2
    assert job1["parent_job_id"] == "parent1"
    assert job1["parent_job_name"] == "Parent 1"

    job2 = actual.query("date == '2022-03-05' and job_id == 'job2'").iloc[0]
    assert job2["actual_working_hours"] == 4
    assert job2["active_user_count"] == 1
    assert pandas.isna(job2["parent_job_id"])
    assert pandas.isna(job2["parent_job_name"])

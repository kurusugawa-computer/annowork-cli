import os
from pathlib import Path

import pytest

from annoworkcli.actual_working_time.list_actual_working_time_weekly import get_weekly_actual_working_hours_df

# モジュールレベルでpytestのmarkerを付ける
pytestmark = pytest.mark.access_webapi


# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/actual_working_time")
out_dir = Path("./tests/out/actual_working_time")
out_dir.mkdir(exist_ok=True, parents=True)


ACTUAL_WORKING_TIMES = [
    {
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Task1",
        "start_datetime": "2022-03-05T10:00:00+09:00",
        "actual_working_hours": 1.0,
    },
    {
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Task1",
        "start_datetime": "2022-03-06T10:00:00+09:00",
        "actual_working_hours": 2.0,
    },
    {
        "workspace_member_id": "alice",
        "job_id": "job1",
        "job_name": "Task1",
        "start_datetime": "2022-03-12T10:00:00+09:00",
        "actual_working_hours": 3.0,
    },
    {
        "workspace_member_id": "bob",
        "job_id": "job2",
        "job_name": "Task2",
        "start_datetime": "2022-02-06T10:00:00+09:00",
        "actual_working_hours": 4.0,
    },
    {
        "workspace_member_id": "bob",
        "job_id": "job2",
        "job_name": "Task2",
        "start_datetime": "2022-03-13T10:00:00+09:00",
        "actual_working_hours": 0.0,
    },
]


WORKSPACE_MEMBERS = [{"workspace_member_id": "alice", "user_id": "alice", "username": "ALICE"}]


def test_get_weekly_actual_working_hours_df():
    actual = get_weekly_actual_working_hours_df(ACTUAL_WORKING_TIMES, WORKSPACE_MEMBERS)
    assert len(actual) == 3
    assert actual.query("workspace_member_id == 'alice' and start_date == '2022-03-06'").iloc[0]["actual_working_hours"] == 5

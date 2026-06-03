import os
from pathlib import Path

import pandas

from annoworkcli.annofab.list_working_hours import ListWorkingHoursWithAnnofab, _get_df_working_hours_from_df

# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/annofab/list_working_hours")
out_dir = Path("./tests/out/annofab/list_working_hours")
out_dir.mkdir(exist_ok=True, parents=True)


class Test__get_df_working_hours_from_df:
    def test_normal(self):
        df_user_and_af_account = pandas.read_csv(str(data_dir / "user_and_af_account.csv"))
        df_job_and_af_project = pandas.read_csv(str(data_dir / "job_and_af_project.csv"))
        df_af_working_hours = pandas.read_csv(str(data_dir / "af_working_hours.csv"))
        df_actual_working_hours = pandas.read_csv(str(data_dir / "actual_working_hours.csv"))

        df = _get_df_working_hours_from_df(
            df_actual_working_hours=df_actual_working_hours,
            df_user_and_af_account=df_user_and_af_account,
            df_job_and_af_project=df_job_and_af_project,
            df_af_working_hours=df_af_working_hours,
        )

        df.to_csv(out_dir / "out.csv", index=False)


class TestListWorkingHoursWithAnnofab:
    def test_get_df_job_parent_job_when_parent_job_id_is_missing(self):
        obj = ListWorkingHoursWithAnnofab.__new__(ListWorkingHoursWithAnnofab)
        obj.all_jobs = [
            {"job_id": "parent1", "job_name": "Parent 1", "job_tree": "/parent1"},
            {"job_id": "job1", "job_name": "Job 1", "job_tree": "/parent1/job1"},
        ]

        df = obj._get_df_job_parent_job()

        parent_job = df[df["job_id"] == "parent1"].iloc[0]
        child_job = df[df["job_id"] == "job1"].iloc[0]
        assert pandas.isna(parent_job["parent_job_id"])
        assert pandas.isna(parent_job["parent_job_name"])
        assert child_job["parent_job_id"] == "parent1"
        assert child_job["parent_job_name"] == "Parent 1"

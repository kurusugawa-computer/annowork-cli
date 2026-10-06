import os
from pathlib import Path
from unittest.mock import MagicMock

import pandas
import pytest
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.__main__ import create_parser
from annoworkcli.annofab.reshape_working_hours import ReshapeDataFrame, ReshapeWorkingHours, main

# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/annofab/reshape_working_hours")
out_dir = Path("./tests/out/annofab/reshape_working_hours")
out_dir.mkdir(exist_ok=True, parents=True)


class TestReshapeDataFrame:
    main_obj: ReshapeDataFrame

    @classmethod
    def setup_class(cls):
        cls.main_obj = ReshapeDataFrame()

    def test_get_df_total(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total(df_actual=df_actual, df_assigned=df_assigned)
        df.to_csv(out_dir / "out-total.csv", index=False)

    def test_get_df_total_by_user(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))
        df_user_company = pandas.read_csv(str(data_dir / "user_company.csv"))

        df = self.main_obj.get_df_total_by_user(df_actual=df_actual, df_assigned=df_assigned, df_user_company=df_user_company)
        df.to_csv(out_dir / "out-total_by_user.csv", index=False)

    def test_get_df_total_by_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_total_by_job(df_actual=df_actual)
        df.to_csv(out_dir / "out-total_by_job.csv", index=False)

    def test_get_df_total_by_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total_by_parent_job(
            df_actual=df_actual,
            df_assigned=df_assigned,
        )
        df.to_csv(out_dir / "out-total_by_parent_job.csv", index=False)

    def test_get_df_total_by_user_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_total_by_user_parent_job(
            df_actual=df_actual,
            df_assigned=df_assigned,
        )
        df.to_csv(out_dir / "out-total_by_user_parent_job.csv", index=False)

    def test_get_df_total_by_user_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_total_by_user_job(df_actual=df_actual)
        df.to_csv(out_dir / "out-total_by_user_job.csv", index=False)

    def test_get_df_details(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df_assigned = pandas.read_csv(str(data_dir / "assigned.csv"))

        df = self.main_obj.get_df_details(df_actual=df_actual, df_assigned=df_assigned)
        df.to_csv(out_dir / "out-details.csv", index=False)

    def test_get_df_list_by_date_user_parent_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))

        df = self.main_obj.get_df_list_by_date_user_parent_job(df_actual=df_actual)
        df.to_csv(out_dir / "list_by_date_user_parent_job.csv")

    def test_get_df_list_by_date_user_job(self):
        df_actual = pandas.read_csv(str(data_dir / "actual.csv"))
        df = self.main_obj.get_df_list_by_date_user_job(df_actual=df_actual)
        df.to_csv(out_dir / "list_by_date_user_job.csv")

    @pytest.mark.parametrize("shape_type", ["total", "total_by_user", "total_by_parent_job", "total_by_user_parent_job"])
    @pytest.mark.parametrize("assigned_hours,actual_hours,expected_diff", [(10, 6, 4), (6, 10, -4), (10, 0, 10), (0, 6, -6), (0, 0, 0)])
    def test_activity_diff(self, shape_type, assigned_hours, actual_hours, expected_diff):
        df_actual = pandas.DataFrame(
            [
                {
                    "user_id": "alice",
                    "username": "Alice",
                    "parent_job_id": "parent",
                    "parent_job_name": "Parent",
                    "actual_working_hours": actual_hours,
                    "annofab_working_hours": 2,
                }
            ]
        )
        df_assigned = pandas.DataFrame(
            [{"user_id": "alice", "username": "Alice", "job_id": "parent", "job_name": "Parent", "assigned_working_hours": assigned_hours}]
        )
        kwargs = {"df_actual": df_actual, "df_assigned": df_assigned}
        if shape_type == "total_by_user":
            kwargs["df_user_company"] = pandas.DataFrame([{"user_id": "alice", "company": "Company"}])
        df = getattr(self.main_obj, f"get_df_{shape_type}")(**kwargs)
        assert df["activity_diff"].tolist() == [expected_diff]


class TestReshapeWorkingHours:
    @pytest.mark.parametrize("filter_option", ["job_ids", "annofab_project_ids", "parent_job_ids"])
    def test_filter_assigned_hours(self, filter_option):
        service = MagicMock(spec=AnnoworkResource)
        service.api = MagicMock()
        service.api.get_jobs.return_value = []
        main_obj = ReshapeWorkingHours(annowork_service=service, workspace_id="workspace")
        df_actual = pandas.DataFrame(
            [
                {"job_id": "job1", "parent_job_id": "parent1", "annofab_project_id": "project1"},
                {"job_id": "job2", "parent_job_id": "parent2", "annofab_project_id": "project2"},
            ]
        )
        df_assigned = pandas.DataFrame([{"job_id": "parent1", "assigned_working_hours": 10.0}, {"job_id": "parent2", "assigned_working_hours": 20.0}])
        actual, assigned = main_obj.filter_df(
            df_actual=df_actual,
            df_assigned=df_assigned,
            job_ids=["job1"] if filter_option == "job_ids" else None,
            annofab_project_ids=["project1"] if filter_option == "annofab_project_ids" else None,
            parent_job_ids=["parent1"] if filter_option == "parent_job_ids" else None,
        )
        assert actual["job_id"].tolist() == ["job1"]
        if filter_option == "parent_job_ids":
            assert assigned["assigned_working_hours"].tolist() == [10.0]
        else:
            assert assigned.empty
            pandas.testing.assert_series_equal(assigned.dtypes, df_assigned.dtypes)
        assert len(df_assigned) == 2

    @pytest.mark.parametrize("filter_option", ["--job_id", "--annofab_project_id"])
    @pytest.mark.parametrize("use_assigned_file", [False, True])
    def test_main_skips_assigned_hours(self, tmp_path, monkeypatch, filter_option, use_assigned_file):
        service = MagicMock(spec=AnnoworkResource)
        service.api = MagicMock()
        service.api.get_jobs.return_value = []
        monkeypatch.setattr("annoworkcli.annofab.reshape_working_hours.build_annoworkapi", lambda _args: service)
        actual_file = tmp_path / "actual.csv"
        pandas.DataFrame(
            [
                {"job_id": "job1", "annofab_project_id": "project1", "actual_working_hours": 6.0, "annofab_working_hours": 4.0},
                {"job_id": "job2", "annofab_project_id": "project2", "actual_working_hours": 10.0, "annofab_working_hours": 8.0},
            ]
        ).to_csv(actual_file, index=False)
        output = tmp_path / "total.csv"
        arguments = [
            "annofab",
            "reshape_working_hours",
            "--workspace_id",
            "workspace",
            "--actual_file",
            str(actual_file),
            "--shape_type",
            "total",
            "--output",
            str(output),
            filter_option,
            "job1" if filter_option == "--job_id" else "project1",
        ]
        if use_assigned_file:
            arguments.extend(["--assigned_file", str(tmp_path / "nonexistent.csv")])
        main(create_parser().parse_args(arguments))
        result = pandas.read_csv(output)
        assert result["assigned_working_hours"].tolist() == [0.0]
        assert result["actual_working_hours"].tolist() == [6.0]
        assert result["activity_diff"].tolist() == [-6.0]
        assert not service.api.get_schedules.called
        assert not service.api.get_expected_working_times.called

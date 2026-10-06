from pathlib import Path
from unittest.mock import MagicMock

import pandas
import pytest
from annofabcli.statistics.visualize_statistics import read_actual_worktime
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.annofab.visualize_statistics import add_parser, visualize_statistics


@pytest.mark.parametrize("filter_option", ["--job_id", "--annofab_project_id"])
@pytest.mark.parametrize("has_actual_worktime", [True, False])
def test_実績作業時間CSVを最新のannofabcliに渡せる(tmp_path, monkeypatch, filter_option, has_actual_worktime):
    service = MagicMock(spec=AnnoworkResource)
    service.api = MagicMock()
    service.wrapper = MagicMock()
    service.api.get_jobs.return_value = [
        {
            "job_id": "job1",
            "job_name": "Job 1",
            "job_tree": "/job1",
            "external_linkage_info": {"url": "https://annofab.com/projects/project1"},
        }
    ]
    service.api.get_workspace_members.return_value = [{"workspace_member_id": "member1", "user_id": "user1", "username": "User 1"}]
    service.api.get_actual_working_times.return_value = (
        [
            {
                "actual_working_time_id": "actual1",
                "workspace_member_id": "member1",
                "job_id": "job1",
                "start_datetime": "2026-10-01T14:00:00.000Z",
                "end_datetime": "2026-10-01T16:00:00.000Z",
                "note": "作業",
            }
        ]
        if has_actual_worktime
        else []
    )
    service.wrapper.get_annofab_account_id_from_user_id.return_value = "account1"
    monkeypatch.setattr("annoworkcli.annofab.visualize_statistics.build_annoworkapi", lambda _args: service)
    run = MagicMock()
    monkeypatch.setattr("annoworkcli.annofab.visualize_statistics.subprocess.run", run)
    args = add_parser().parse_args(
        ["--workspace_id", "workspace", filter_option, "job1" if filter_option == "--job_id" else "project1", "--output_dir", str(tmp_path / "out")]
    )

    visualize_statistics(tmp_path, args, "workspace")

    run.assert_called_once()
    command = run.call_args.args[0]
    assert "--labor_csv" not in command
    csv_path = Path(command[command.index("--actual_worktime_csv") + 1])
    assert command[command.index("--project_id") + 1] == "project1"
    # 外部コマンドに渡したCSVを、更新後のannofabcliで実際に読み込めることを確認する。
    actual_worktime = read_actual_worktime(actual_worktime_csv=csv_path, labor_csv=None)
    assert actual_worktime is not None
    df = pandas.read_csv(csv_path)
    assert df.columns.tolist() == ["date", "account_id", "project_id", "actual_worktime_hour"]
    assert df.to_dict("records") == (
        [
            {"date": "2026-10-01", "account_id": "account1", "project_id": "project1", "actual_worktime_hour": 1.0},
            {"date": "2026-10-02", "account_id": "account1", "project_id": "project1", "actual_worktime_hour": 1.0},
        ]
        if has_actual_worktime
        else []
    )

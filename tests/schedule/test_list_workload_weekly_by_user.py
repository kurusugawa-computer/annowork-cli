import csv
import json

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_weekly_by_user import CSV_COLUMNS, ListWorkloadWeeklyByUser


def test_日曜に週を切り替えて期間内の時間だけ集計する(service):
    service.api.get_schedules.return_value[0].update(start_date="2026-09-01", end_date="2026-11-01")
    rows = ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-05")
    assert [(row.start_date, row.end_date, row.assigned_working_hours) for row in rows] == [
        ("2026-09-27", "2026-10-03", 6),
        ("2026-10-04", "2026-10-10", 6),
    ]


def test_日別の割合換算後に合算し親ジョブの内訳を保持する(service):
    service.api.get_expected_working_times.return_value = [
        {"date": date, "workspace_member_id": "member", "expected_working_hours": hours} for date, hours in [("2026-10-01", 4), ("2026-10-02", 8)]
    ]
    schedule = service.api.get_schedules.return_value[0]
    schedule.update(type="percentage", value=50, end_date="2026-10-03")
    service.api.get_schedules.return_value.append({**schedule, "schedule_id": "second", "job_id": "grandparent", "type": "hours", "value": 1})
    rows = ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    assert len(rows) == 1
    row = rows[0]
    assert (row.expected_working_hours, row.assigned_working_hours, row.remaining_working_hours) == (12, 9, 3)
    assert [(item.parent_job_id, item.assigned_working_hours) for item in row.assignments] == [("grandparent", 3), ("parent", 6)]


def test_対象ユーザーの未アサインと0時間登録を含めデータのない週は省く(service):
    service.api.get_schedules.return_value = []
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 0},
        {"date": "2026-10-02", "workspace_member_id": "other", "expected_working_hours": 8},
        {"date": "2026-10-19", "workspace_member_id": "member", "expected_working_hours": 6},
    ]
    rows = ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-10-01", user_ids=["alice"])
    assert [(row.start_date, row.expected_working_hours, row.remaining_working_hours, row.assignments) for row in rows] == [
        ("2026-09-27", 0, 0, []),
        ("2026-10-18", 6, 6, []),
    ]


@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("empty", [True, False])
def test_週とユーザーごとのCSVとJSONを出力する(service, tmp_path, output_format, empty):
    if empty:
        service.api.get_schedules.return_value = []
    output = tmp_path / "workload"
    ListWorkloadWeeklyByUser(service, "workspace").main(
        start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=output_format
    )
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
        if rows:
            assert rows[0]["assignments"] == [{"parent_job_id": "parent", "parent_job_name": "Parent", "assigned_working_hours": 3}]
    else:
        with output.open(encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == CSV_COLUMNS + ([] if empty else ["Parent"])
            rows = list(reader)
            if rows:
                assert float(rows[0]["Parent"]) == 3
    assert len(rows) == (0 if empty else 1)
    if rows:
        assert (rows[0]["start_date"], rows[0]["end_date"], rows[0]["user_id"]) == ("2026-09-27", "2026-10-03", "alice")
        assert float(rows[0]["remaining_working_hours"]) == -3


@pytest.mark.parametrize("name", ["start_date", "end_date", "", None])
def test_CSVで不正な親ジョブ名は拒否しJSONでは保持する(service, tmp_path, name):
    service.api.get_jobs.return_value[0]["job_name"] = name
    output = tmp_path / "workload"
    output.write_text("既存の出力")
    command = ListWorkloadWeeklyByUser(service, "workspace")
    with pytest.raises(ValueError):
        command.main(start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=OutputFormat.CSV)
    assert output.read_text() == "既存の出力"
    command.main(start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=OutputFormat.JSON)
    assert json.loads(output.read_text())[0]["assignments"][0]["parent_job_name"] == name


def test_年をまたぐ週と浮動小数点の差分を集計する(service):
    service.api.get_schedules.return_value[0].update(start_date="2026-12-31", end_date="2027-01-02", type="percentage", value=100)
    service.api.get_expected_working_times.return_value = [
        {"date": date, "workspace_member_id": "member", "expected_working_hours": 7.6} for date in ["2026-12-31", "2027-01-01", "2027-01-02"]
    ]
    rows = ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-12-31", end_date="2027-01-02")
    assert len(rows) == 1
    assert (rows[0].start_date, rows[0].end_date, rows[0].remaining_working_hours) == ("2026-12-27", "2027-01-02", 0)


def test_逆転した期間を拒否する(service):
    with pytest.raises(ValueError):
        ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-01")

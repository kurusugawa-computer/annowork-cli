import csv
import json

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_daily import ListWorkloadDaily
from annoworkcli.schedule.list_workload_daily_by_user import CSV_COLUMNS, ListWorkloadDailyByUser, create_workload_csv


def test_全ジョブの内訳と未アサインを日ごとに集計する(service):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": member, "expected_working_hours": 6} for member in ["member", "free"]
    ]
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.extend(
        [
            {**schedule, "schedule_id": "second", "type": "percentage", "value": 50},
            {**schedule, "schedule_id": "third", "job_id": "grandparent", "value": 2},
        ]
    )
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    free, assigned = result
    assert (free.user_id, free.remaining_working_hours, free.assignments) == ("bob", 6, [])
    assert (assigned.assigned_working_hours, assigned.remaining_working_hours) == (8, -2)
    assert [(item.parent_job_id, item.parent_job_name, item.assigned_working_hours) for item in assigned.assignments] == [
        ("grandparent", "Grandparent", 2),
        ("parent", "Parent", 6),
    ]


@pytest.mark.parametrize("percentage", [False, True])
def test_予定稼働時間が未登録の場合は0時間として過不足を判定する(service, percentage):
    if percentage:
        service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].expected_working_hours == 0
    assert result[0].remaining_working_hours == (0 if percentage else -3)
    assert result[0].assigned_working_hours == (0 if percentage else 3)


@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("percentage_only", [False, True])
def test_未登録の割合指定と時間指定を合算して数値で出力する(service, tmp_path, output_format, percentage_only):
    schedule = service.api.get_schedules.return_value[0]
    if percentage_only:
        service.api.get_schedules.return_value = []
    service.api.get_schedules.return_value.append({**schedule, "schedule_id": "percentage", "type": "percentage", "value": 50})
    assigned = 0 if percentage_only else 3
    output = tmp_path / "workload"
    ListWorkloadDailyByUser(service, "workspace").main(
        start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=output_format
    )
    if output_format == OutputFormat.JSON:
        row = json.loads(output.read_text())[0]
        assert row["assignments"][0]["assigned_working_hours"] == assigned
    else:
        with output.open(encoding="utf-8-sig") as stream:
            row = next(csv.DictReader(stream))
        assert float(row["Parent"]) == assigned
    assert "status" not in row
    assert float(row["assigned_working_hours"]) == assigned
    assert float(row["expected_working_hours"]) == 0
    assert float(row["remaining_working_hours"]) == -assigned


@pytest.mark.parametrize("expected,assigned", [(0, 3), (3, 3), (6, 3)])
def test_予定稼働時間との差分を計算する(service, expected, assigned):
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": expected}
    ]
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].remaining_working_hours == expected - assigned


def test_期間外と対象外メンバーを含めない(service):
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 6},
        {"date": "2026-10-01", "workspace_member_id": "other", "expected_working_hours": 6},
    ]
    service.api.get_schedules.return_value[0].update(start_date="2026-09-01", end_date="2026-11-01")
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01", user_ids=["alice"])
    assert len(result) == 1
    assert result[0].assigned_working_hours == 3
    assert result[0].date == "2026-10-01"


@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("empty", [False, True])
def test_JSONの内訳とCSVの親ジョブ列を出力する(service, tmp_path, output_format, empty):
    service.api.get_jobs.return_value[0]["job_name"] = '日本語,"ジョブ"'
    if empty:
        service.api.get_schedules.return_value = []
    output = tmp_path / "workload"
    ListWorkloadDailyByUser(service, "workspace").main(
        start_date="2026-10-01",
        end_date="2026-10-01",
        user_ids=None,
        output=output,
        output_format=output_format,
    )
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
    else:
        with output.open(encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames is not None
            assert "status" not in reader.fieldnames
            assert reader.fieldnames == CSV_COLUMNS + ([] if empty else ['日本語,"ジョブ"'])
            rows = list(reader)
    assert len(rows) == (0 if empty else 1)
    if not empty and output_format == OutputFormat.CSV:
        assert float(rows[0]['日本語,"ジョブ"']) == 3
        assert float(rows[0]["expected_working_hours"]) == 0
        assert float(rows[0]["remaining_working_hours"]) == -3
    elif not empty:
        assert rows[0]["assignments"] == [{"parent_job_id": "parent", "parent_job_name": '日本語,"ジョブ"', "assigned_working_hours": 3}]


def test_逆転した期間は拒否する(service):
    with pytest.raises(ValueError):
        ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-01")


@pytest.mark.parametrize("percentage", [False, True])
def test_終了日省略時は予定稼働時間と計画を上限なしで取得する(service, percentage):
    service.api.get_schedules.return_value[0].update(
        start_date="2026-09-01", end_date="2026-12-01", type="percentage" if percentage else "hours", value=50 if percentage else 3
    )
    service.api.get_expected_working_times.return_value = [
        {"date": date, "workspace_member_id": "member", "expected_working_hours": 8} for date in ["2026-09-30", "2026-10-01", "2026-12-02"]
    ]
    rows = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01")
    assert len(rows) == 63
    assert rows[0].date == "2026-10-01"
    assert rows[0].assigned_working_hours == (4 if percentage else 3)
    assert rows[-2].date == "2026-12-01"
    assert rows[-2].assigned_working_hours == (0 if percentage else 3)
    assert rows[-1].date == "2026-12-02"
    assert service.api.get_expected_working_times.call_args.kwargs["query_params"] == {"term_start": "2026-10-01", "term_end": None}


def test_割合指定の浮動小数点誤差を超過扱いしない(service):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 7.6}]
    service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].remaining_working_hours == 0


@pytest.mark.parametrize("has_schedule", [False, True])
def test_予定稼働時間とアサイン時間がともに0の登録も含める(service, has_schedule):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 0}]
    if has_schedule:
        service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    else:
        service.api.get_schedules.return_value = []
    result = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert len(result) == 1
    assert result[0].expected_working_hours == result[0].assigned_working_hours == result[0].remaining_working_hours == 0


@pytest.mark.parametrize("name", [*CSV_COLUMNS, "", None])
def test_CSVの親ジョブ名が不正なら拒否しJSONは出力できる(service, tmp_path, name):
    service.api.get_jobs.return_value[1]["job_name"] = name
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append({**schedule, "job_id": "grandparent", "schedule_id": "second"})
    command = ListWorkloadDailyByUser(service, "workspace")
    output = tmp_path / "workload"
    output.write_text("既存の出力")
    with pytest.raises(ValueError):
        command.main(start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=OutputFormat.CSV)
    assert output.read_text() == "既存の出力"
    command.main(start_date="2026-10-01", end_date="2026-10-01", user_ids=None, output=output, output_format=OutputFormat.JSON)
    assert len(json.loads(output.read_text())[0]["assignments"]) == 2


@pytest.mark.parametrize("percentage", [False, True])
def test_親ジョブ列の順序と時間が日別集計に対応する(service, percentage):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": member, "expected_working_hours": 6} for member in ["member", "free"]
    ]
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append(
        {
            **schedule,
            "schedule_id": "second",
            "job_id": "grandparent",
            "start_date": "2026-10-02",
            "end_date": "2026-10-02",
            "value": 50 if percentage else 2,
            "type": "percentage" if percentage else "hours",
        }
    )
    workloads = ListWorkloadDailyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    df = create_workload_csv(workloads)
    assert list(df.columns) == [*CSV_COLUMNS, "Grandparent", "Parent"]
    assert df["Parent"].tolist() == [0, 3, 0]
    assert df["Grandparent"].iloc[:2].tolist() == [0, 0]
    assert df["Grandparent"].iloc[2] == (0 if percentage else 2)
    summaries = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    for summary in summaries:
        rows = [row for row in workloads if row.date == summary.date]
        for assignment in summary.assignments:
            hours = [detail.assigned_working_hours for row in rows for detail in row.assignments if detail.parent_job_id == assignment.parent_job_id]
            assert assignment.assigned_working_hours == sum(hours)
        assert len(summary.members) == len(rows)

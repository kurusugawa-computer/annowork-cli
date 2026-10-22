import csv
import json
from dataclasses import asdict

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_daily import ListWorkloadDaily, create_workload_csv


def test_全体とユーザー別と親ジョブ別の時間を集計する(service):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": member, "expected_working_hours": 8} for member in ["member", "free"]
    ]
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.extend(
        [
            {**schedule, "schedule_id": "second", "type": "percentage", "value": 25},
            {**schedule, "schedule_id": "third", "job_id": "grandparent", "value": 4},
        ]
    )
    rows = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-02")
    assert asdict(rows[0]) == {
        "date": "2026-10-01",
        "expected_working_hours": 16,
        "assigned_working_hours": 9,
        "remaining_working_hours": 7,
        "members": [
            {
                "workspace_member_id": "free",
                "user_id": "bob",
                "username": "Bob",
                "expected_working_hours": 8,
                "assigned_working_hours": 0,
                "remaining_working_hours": 8,
                "status": "unassigned",
            },
            {
                "workspace_member_id": "member",
                "user_id": "alice",
                "username": "Alice",
                "expected_working_hours": 8,
                "assigned_working_hours": 9,
                "remaining_working_hours": -1,
                "status": "overloaded",
            },
        ],
        "assignments": [
            {
                "parent_job_id": "grandparent",
                "parent_job_name": "Grandparent",
                "assigned_working_hours": 4,
                "members": [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice", "assigned_working_hours": 4}],
            },
            {
                "parent_job_id": "parent",
                "parent_job_name": "Parent",
                "assigned_working_hours": 5,
                "members": [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice", "assigned_working_hours": 5}],
            },
        ],
    }
    assert asdict(rows[1]) == {
        "date": "2026-10-02",
        "expected_working_hours": 0,
        "assigned_working_hours": 0,
        "remaining_working_hours": 0,
        "members": [],
        "assignments": [],
    }


def test_同じ親ジョブの複数メンバーを集計する(service):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "other", "user_id": "bob", "username": "Bob"})
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append({**schedule, "schedule_id": "second", "workspace_member_id": "other", "value": 2})
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": member, "expected_working_hours": 8} for member in ["member", "other"]
    ]
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert (row.expected_working_hours, row.assigned_working_hours, row.remaining_working_hours) == (16, 5, 11)
    assert row.assignments[0].assigned_working_hours == 5
    assert [(member.user_id, member.assigned_working_hours) for member in row.assignments[0].members] == [("alice", 3), ("bob", 2)]


@pytest.mark.parametrize("percentage", [False, True])
def test_未登録の予定稼働時間と不明なアサイン時間を区別する(service, percentage):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "free", "expected_working_hours": 8}]
    if percentage:
        service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert row.expected_working_hours == 8
    assert row.members[1].expected_working_hours is None
    assert row.members[1].remaining_working_hours is None
    assert row.assigned_working_hours == (None if percentage else 3)
    assert row.remaining_working_hours == (None if percentage else 5)
    assert row.assignments[0].assigned_working_hours == (None if percentage else 3)
    assert row.assignments[0].members[0].assigned_working_hours == (None if percentage else 3)


def test_不明な時間は該当ジョブと日別合計へ伝播する(service):
    service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.extend(
        [
            {**schedule, "schedule_id": "second", "workspace_member_id": "other", "type": "hours", "value": 2},
            {**schedule, "schedule_id": "third", "job_id": "grandparent", "type": "hours", "value": 4},
        ]
    )
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert row.assigned_working_hours is None
    assert row.remaining_working_hours is None
    known, unknown = row.assignments
    assert known.assigned_working_hours == 4
    assert unknown.assigned_working_hours is None
    assert [member.assigned_working_hours for member in unknown.members] == [None, 2]


@pytest.mark.parametrize("has_schedule", [False, True])
def test_予定稼働時間が0の登録もメンバーに含める(service, has_schedule):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 0}]
    if has_schedule:
        service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    else:
        service.api.get_schedules.return_value = []
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert len(row.members) == 1
    assert row.expected_working_hours == row.assigned_working_hours == row.remaining_working_hours == 0
    assert row.members[0].status == "full"


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_全日をCSVとJSONで出力する(service, tmp_path, output_format):
    output = tmp_path / "workload"
    name = '日本語,"ジョブ"'
    service.api.get_jobs.return_value[0]["job_name"] = name
    ListWorkloadDaily(service, "workspace").main(start_date="2026-10-01", end_date="2026-10-02", output=output, output_format=output_format)
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
        assert len(rows) == 2
        assert rows[0]["assignments"][0]["parent_job_name"] == name
        assert rows[0]["assignments"][0]["members"][0]["user_id"] == "alice"
        assert rows[0]["members"][0]["expected_working_hours"] is None
        assert rows[1]["members"] == rows[1]["assignments"] == []
    else:
        with output.open(encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == ["date", "expected_working_hours", "assigned_working_hours", "remaining_working_hours", name]
            rows = list(reader)
        assert [row["date"] for row in rows] == ["2026-10-01", "2026-10-02"]
        assert [float(row[name]) for row in rows] == [3, 0]
        assert float(rows[0]["assigned_working_hours"]) == 3
        assert float(rows[0]["remaining_working_hours"]) == -3


def test_CSVは期間全体のジョブをID順の列にする(service):
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append(
        {**schedule, "schedule_id": "second", "job_id": "grandparent", "start_date": "2026-10-02", "end_date": "2026-10-02", "value": 2}
    )
    rows = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    df = create_workload_csv(rows)
    assert list(df.columns) == ["date", "expected_working_hours", "assigned_working_hours", "remaining_working_hours", "Grandparent", "Parent"]
    assert df["Grandparent"].tolist() == [0, 2, 0]
    assert df["Parent"].tolist() == [3, 0, 0]


@pytest.mark.parametrize("name", ["Parent", "date", "expected_working_hours", "assigned_working_hours", "remaining_working_hours", ""])
def test_CSVの列名が重複または空なら拒否しJSONでは出力できる(service, tmp_path, name):
    service.api.get_jobs.return_value[1]["job_name"] = name
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append({**schedule, "job_id": "grandparent", "schedule_id": "second"})
    command = ListWorkloadDaily(service, "workspace")
    output = tmp_path / "output"
    output.write_text("既存の出力")
    with pytest.raises(ValueError):
        command.main(start_date="2026-10-01", end_date="2026-10-01", output=output, output_format=OutputFormat.CSV)
    assert output.read_text() == "既存の出力"
    command.main(start_date="2026-10-01", end_date="2026-10-01", output=output, output_format=OutputFormat.JSON)
    assert len(json.loads(output.read_text())[0]["assignments"]) == 2


def test_削除済みジョブはJSONの名前をnullとしCSVでは拒否する(service):
    service.api.get_jobs.return_value = []
    rows = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert rows[0].assignments[0].parent_job_name is None
    with pytest.raises(ValueError):
        create_workload_csv(rows)


def test_CSVでは計算不能を空欄にする(service, tmp_path):
    service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    output = tmp_path / "workload.csv"
    ListWorkloadDaily(service, "workspace").main(start_date="2026-10-01", end_date="2026-10-01", output=output, output_format=OutputFormat.CSV)
    with output.open(encoding="utf-8-sig") as stream:
        row = next(csv.DictReader(stream))
    assert row["Parent"] == row["assigned_working_hours"] == row["remaining_working_hours"] == ""
    assert float(row["expected_working_hours"]) == 0


def test_空のCSVでもヘッダーを出力する():
    assert create_workload_csv([]).to_csv(index=False) == "date,expected_working_hours,assigned_working_hours,remaining_working_hours\n"


def test_割合指定の誤差で残り時間を負数にしない(service):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 7.6}]
    service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert row.remaining_working_hours == 0


def test_逆転した期間は拒否する(service):
    with pytest.raises(ValueError):
        ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-01")

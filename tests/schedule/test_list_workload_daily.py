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
            },
            {
                "workspace_member_id": "member",
                "user_id": "alice",
                "username": "Alice",
                "expected_working_hours": 8,
                "assigned_working_hours": 9,
                "remaining_working_hours": -1,
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
def test_未登録の予定稼働時間でもアサイン時間を集計する(service, percentage):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "free", "expected_working_hours": 8}]
    if percentage:
        service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert row.expected_working_hours == 8
    assert row.members[1].expected_working_hours == 0
    assert row.members[1].remaining_working_hours == (0 if percentage else -3)
    assert row.assigned_working_hours == (0 if percentage else 3)
    assert row.remaining_working_hours == (8 if percentage else 5)
    assert row.assignments[0].assigned_working_hours == (0 if percentage else 3)
    assert row.assignments[0].members[0].assigned_working_hours == (0 if percentage else 3)


@pytest.mark.parametrize("reverse", [False, True])
def test_予定稼働時間未登録の割合指定と時間指定を合算する(service, reverse):
    service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.extend(
        [
            {**schedule, "schedule_id": "second", "workspace_member_id": "other", "type": "hours", "value": 2},
            {**schedule, "schedule_id": "third", "job_id": "grandparent", "type": "hours", "value": 4},
        ]
    )
    if reverse:
        service.api.get_schedules.return_value.reverse()
    row = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")[0]
    assert row.assigned_working_hours == 6
    assert row.remaining_working_hours == -6
    grandparent, parent = row.assignments
    assert grandparent.assigned_working_hours == 4
    assert parent.assigned_working_hours == 2
    assert [member.assigned_working_hours for member in parent.members] == [0, 2]


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
        assert rows[0]["members"][0]["expected_working_hours"] == 0
        assert rows[0]["members"][0]["remaining_working_hours"] == -3
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


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_予定稼働時間未登録の割合指定を0時間で出力する(service, tmp_path, output_format):
    service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    output = tmp_path / "workload"
    ListWorkloadDaily(service, "workspace").main(start_date="2026-10-01", end_date="2026-10-01", output=output, output_format=output_format)
    if output_format == OutputFormat.JSON:
        row = json.loads(output.read_text())[0]
        assert row["assignments"][0]["assigned_working_hours"] == 0
        assert row["members"][0]["assigned_working_hours"] == 0
    else:
        with output.open(encoding="utf-8-sig") as stream:
            row = next(csv.DictReader(stream))
        assert float(row["Parent"]) == 0
    assert float(row["assigned_working_hours"]) == float(row["remaining_working_hours"]) == float(row["expected_working_hours"]) == 0


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


@pytest.mark.parametrize("last_source", ["schedule", "expected", "empty"])
def test_終了日省略時はデータの最終日まで集計する(service, last_source):
    service.api.get_schedules.return_value[0].update(start_date="2026-09-30", end_date="2026-12-01")
    if last_source != "schedule":
        service.api.get_schedules.return_value = []
    if last_source == "expected":
        service.api.get_expected_working_times.return_value = [{"date": "2026-12-01", "workspace_member_id": "member", "expected_working_hours": 8}]
    rows = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01")
    if last_source == "empty":
        assert rows == []
    else:
        assert len(rows) == 62
        assert rows[0].date == "2026-10-01"
        assert rows[-1].date == "2026-12-01"
        assert rows[-1].assigned_working_hours == (3 if last_source == "schedule" else 0)
        assert rows[-1].expected_working_hours == (8 if last_source == "expected" else 0)

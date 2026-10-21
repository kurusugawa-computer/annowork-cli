import csv
import json

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_daily import ListWorkloadDaily


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
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    free, assigned = result
    assert (free.user_id, free.status, free.remaining_working_hours, free.assignments) == ("bob", "unassigned", 6, [])
    assert (assigned.assigned_working_hours, assigned.remaining_working_hours, assigned.status) == (8, -2, "overloaded")
    assert [(item.parent_job_id, item.parent_job_name, item.assigned_working_hours) for item in assigned.assignments] == [
        ("grandparent", "Grandparent", 2),
        ("parent", "Parent", 6),
    ]


@pytest.mark.parametrize("percentage", [False, True])
def test_予定稼働時間が未登録の場合は判定不能とする(service, percentage):
    if percentage:
        service.api.get_schedules.return_value[0].update(type="percentage", value=50)
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].expected_working_hours is None
    assert result[0].remaining_working_hours is None
    assert result[0].status == "unknown"
    assert result[0].assigned_working_hours == (None if percentage else 3)


@pytest.mark.parametrize("expected,assigned,status", [(0, 3, "overloaded"), (3, 3, "full"), (6, 3, "under_assigned")])
def test_予定稼働時間との過不足を判定する(service, expected, assigned, status):
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": expected}
    ]
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].status == status
    assert result[0].remaining_working_hours == expected - assigned


def test_期間外と対象外メンバーを含めない(service):
    service.api.get_expected_working_times.return_value = [
        {"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 6},
        {"date": "2026-10-01", "workspace_member_id": "other", "expected_working_hours": 6},
    ]
    service.api.get_schedules.return_value[0].update(start_date="2026-09-01", end_date="2026-11-01")
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01", user_ids=["alice"])
    assert len(result) == 1
    assert result[0].assigned_working_hours == 3
    assert result[0].date == "2026-10-01"


@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("empty", [False, True])
def test_JSON配列とCSVのJSON文字列を出力する(service, tmp_path, output_format, empty):
    service.api.get_jobs.return_value[0]["job_name"] = '日本語,"ジョブ"'
    output = tmp_path / "workload"
    ListWorkloadDaily(service, "workspace").main(
        start_date="2026-10-01",
        end_date="2026-10-01",
        user_ids=None,
        statuses=["unassigned"] if empty else None,
        output=output,
        output_format=output_format,
    )
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
    else:
        with output.open() as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames is not None
            assert "assignments" in reader.fieldnames
            rows = list(reader)
        for row in rows:
            row["assignments"] = json.loads(row["assignments"])
    assert len(rows) == (0 if empty else 1)
    if not empty:
        assert rows[0]["assignments"] == [{"parent_job_id": "parent", "parent_job_name": '日本語,"ジョブ"', "assigned_working_hours": 3}]


def test_逆転した期間は拒否する(service):
    with pytest.raises(ValueError):
        ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-01")


def test_割合指定の浮動小数点誤差を超過扱いしない(service):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 7.6}]
    service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result[0].status == "full"
    assert result[0].remaining_working_hours == 0


@pytest.mark.parametrize("has_schedule", [False, True])
def test_予定稼働時間とアサイン時間がともに0の日は省略する(service, has_schedule):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-01", "workspace_member_id": "member", "expected_working_hours": 0}]
    if has_schedule:
        service.api.get_schedules.return_value[0].update(type="percentage", value=100)
    else:
        service.api.get_schedules.return_value = []
    result = ListWorkloadDaily(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-01")
    assert result == []

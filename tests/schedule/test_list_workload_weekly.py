import csv
import json

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_weekly import CSV_COLUMNS, ListWorkloadWeekly
from annoworkcli.schedule.list_workload_weekly_by_user import ListWorkloadWeeklyByUser


def test_全体集計とユーザー別内訳の合計が一致する(service):
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "free", "user_id": "bob", "username": "Bob"})
    service.api.get_expected_working_times.return_value = [
        {"date": date, "workspace_member_id": member, "expected_working_hours": 6}
        for date in ["2026-10-01", "2026-10-02"]
        for member in ["member", "free"]
    ]
    service.api.get_schedules.return_value[0].update(end_date="2026-10-02", value=8)
    result = ListWorkloadWeekly(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    users = ListWorkloadWeeklyByUser(service, "workspace").get_workloads(start_date="2026-10-01", end_date="2026-10-03")
    assert len(result) == 1
    row = result[0]
    assert (row.expected_working_hours, row.assigned_working_hours, row.remaining_working_hours) == (24, 16, 8)
    assert [(member.user_id, member.remaining_working_hours) for member in row.members] == [("bob", 12), ("alice", -4)]
    for field in ["expected_working_hours", "assigned_working_hours", "remaining_working_hours"]:
        assert getattr(row, field) == sum(getattr(user, field) for user in users)
    assert row.assignments[0].assigned_working_hours == 16
    assert row.assignments[0].members[0].assigned_working_hours == 16


def test_終了日省略時に最終データの週まで出力し空の週を補完する(service):
    service.api.get_expected_working_times.return_value = [{"date": "2026-10-19", "workspace_member_id": "member", "expected_working_hours": 6}]
    rows = ListWorkloadWeekly(service, "workspace").get_workloads(start_date="2026-10-01")
    assert [row.start_date for row in rows] == ["2026-09-27", "2026-10-04", "2026-10-11", "2026-10-18"]
    for row in rows[1:3]:
        assert (row.expected_working_hours, row.assigned_working_hours, row.remaining_working_hours, row.members, row.assignments) == (
            0,
            0,
            0,
            [],
            [],
        )
    assert rows[-1].end_date == "2026-10-24"
    assert rows[-1].remaining_working_hours == 6


@pytest.mark.parametrize("end_date", [None, "2026-10-04"])
@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_データがない場合の空配列または期間内の全週を出力する(service, tmp_path, end_date, output_format):
    service.api.get_schedules.return_value = []
    output = tmp_path / "workload"
    ListWorkloadWeekly(service, "workspace").main(start_date="2026-10-01", end_date=end_date, output=output, output_format=output_format)
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
    else:
        with output.open(encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == CSV_COLUMNS
            rows = list(reader)
    assert len(rows) == (0 if end_date is None else 2)


@pytest.mark.parametrize("output_format", list(OutputFormat))
def test_全体の週次CSVとJSONで親ジョブ別時間を出力する(service, tmp_path, output_format):
    output = tmp_path / "workload"
    ListWorkloadWeekly(service, "workspace").main(start_date="2026-10-01", end_date="2026-10-03", output=output, output_format=output_format)
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
        assert rows[0]["members"][0]["user_id"] == "alice"
        assert rows[0]["assignments"][0]["parent_job_id"] == "parent"
    else:
        with output.open(encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == [*CSV_COLUMNS, "Parent"]
            rows = list(reader)
        assert float(rows[0]["Parent"]) == 3
    assert len(rows) == 1
    assert (rows[0]["start_date"], rows[0]["end_date"]) == ("2026-09-27", "2026-10-03")
    assert float(rows[0]["assigned_working_hours"]) == 3


def test_逆転した期間を拒否する(service):
    with pytest.raises(ValueError):
        ListWorkloadWeekly(service, "workspace").get_workloads(start_date="2026-10-02", end_date="2026-10-01")

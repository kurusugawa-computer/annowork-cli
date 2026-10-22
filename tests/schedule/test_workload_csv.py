import csv
import logging

import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_workload_daily import ListWorkloadDaily
from annoworkcli.schedule.list_workload_daily_by_user import ListWorkloadDailyByUser


@pytest.mark.parametrize("by_user", [False, True])
def test_同名ジョブは警告して各ジョブの時間を別々の列に出力する(service, tmp_path, caplog, by_user):
    service.api.get_jobs.return_value[1]["job_name"] = "Parent"
    schedule = service.api.get_schedules.return_value[0]
    service.api.get_schedules.return_value.append(
        {**schedule, "schedule_id": "second", "job_id": "grandparent", "end_date": "2026-10-02", "value": 2}
    )
    output = tmp_path / "workload.csv"
    if by_user:
        ListWorkloadDailyByUser(service, "workspace").main(
            start_date="2026-10-01", end_date="2026-10-02", user_ids=None, output=output, output_format=OutputFormat.CSV
        )
    else:
        ListWorkloadDaily(service, "workspace").main(start_date="2026-10-01", end_date="2026-10-02", output=output, output_format=OutputFormat.CSV)
    with output.open(encoding="utf-8-sig") as stream:
        header, *rows = csv.reader(stream)
    assert header[-2:] == ["Parent", "Parent"]
    assert [[float(value) for value in row[-2:]] for row in rows] == [[2, 3], [2, 0]]
    assigned_index = header.index("assigned_working_hours")
    assert [float(row[assigned_index]) for row in rows] == [5, 2]
    assert any(record.levelno == logging.WARNING and "Parent" in record.message and "grandparent" in record.message for record in caplog.records)

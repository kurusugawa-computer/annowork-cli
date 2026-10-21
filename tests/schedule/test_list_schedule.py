import json

import pandas
import pytest

from annoworkcli.common.cli import OutputFormat
from annoworkcli.schedule.list_schedule import ListSchedule


def test_親ジョブIDをAPIのjob_idとして渡し取得結果の名前を変換する(service):
    actual = ListSchedule(service, "workspace").get_schedules(parent_job_ids=["parent"])

    service.api.get_schedules.assert_called_once_with("workspace", query_params={"term_start": None, "term_end": None, "job_id": "parent"})
    assert actual[0]["parent_job_id"] == "parent"
    assert "job_id" not in actual[0]
    assert service.api.get_schedules.return_value[0]["job_id"] == "parent"


@pytest.mark.parametrize("output_format", list(OutputFormat))
@pytest.mark.parametrize("empty", [False, True])
def test_一覧のCSVとJSONに親ジョブ名を使用する(service, tmp_path, output_format, empty):
    if empty:
        service.api.get_schedules.return_value = []
    output = tmp_path / "schedule"
    ListSchedule(service, "workspace").main(
        output=output,
        output_format=output_format,
        start_date=None,
        end_date=None,
        parent_job_id_list=["parent"],
        user_id_list=None,
    )
    if output_format == OutputFormat.JSON:
        rows = json.loads(output.read_text())
        assert len(rows) == (0 if empty else 1)
        if empty:
            return
        columns = rows[0].keys()
    else:
        df = pandas.read_csv(output)
        assert len(df) == (0 if empty else 1)
        columns = df.columns
        rows = df.to_dict("records")
    assert "parent_job_id" in columns
    assert "parent_job_name" in columns
    assert "job_id" not in columns
    assert "job_name" not in columns
    if not empty:
        assert rows[0]["parent_job_id"] == "parent"
        assert rows[0]["parent_job_name"] == "Parent"
        assert rows[0]["assigned_working_hours"] == 3.0

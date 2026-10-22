import datetime
import importlib
import json
from unittest.mock import MagicMock, patch

import pytest
from annoworkapi.resource import Resource


@pytest.mark.parametrize("module_name", ["list_expected_working_time", "list_expected_working_time_weekly", "list_expected_working_time_groupby_tag"])
@pytest.mark.parametrize("user_args", [[], ["--user_id", "alice"]])
@pytest.mark.parametrize("date_args", [[], ["--start_date", "2020-01-01", "--end_date", "2020-02-01"]])
def test_省略時は今日以降を制限なしで取得し明示時は指定期間を使う(monkeypatch, tmp_path, module_name, user_args, date_args):
    service = MagicMock(spec=Resource)
    service.api = MagicMock()
    service.api.get_workspace_members.return_value = [{"workspace_member_id": "member", "user_id": "alice", "username": "Alice"}]
    service.api.get_workspace_tags.return_value = []
    dates = ["2020-01-01", "2020-02-01"] if date_args else ["2026-10-21", "2026-12-01"]
    times = [{"date": date, "workspace_member_id": "member", "expected_working_hours": 8} for date in dates]
    service.api.get_expected_working_times.return_value = times
    service.api.get_expected_working_times_by_workspace_member.return_value = times
    module = importlib.import_module(f"annoworkcli.expected_working_time.{module_name}")
    monkeypatch.setattr(module, "build_annoworkapi", lambda _args: service)
    now = datetime.datetime(2026, 10, 21, 0, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    output = tmp_path / "result.json"
    with patch("datetime.datetime", side_effect=datetime.datetime) as clock:
        clock.now.return_value.astimezone.return_value = now
        args = module.add_parser().parse_args(["--workspace_id", "workspace", "--format", "json", "--output", str(output), *user_args, *date_args])
        args.subcommand_func(args)

    api = service.api.get_expected_working_times_by_workspace_member if user_args else service.api.get_expected_working_times
    expected_query = {"term_start": "2020-01-01", "term_end": "2020-02-01"} if date_args else {"term_start": "2026-10-21"}
    assert api.call_args.kwargs["query_params"] == expected_query
    rows = json.loads(output.read_text())
    if module_name == "list_expected_working_time_groupby_tag":
        assert sum(row["expected_working_hours"]["total"] for row in rows) == 16
    else:
        assert sum(row["expected_working_hours"] for row in rows) == 16

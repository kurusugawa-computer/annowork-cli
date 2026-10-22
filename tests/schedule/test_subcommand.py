import importlib
import json

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "list_schedule",
        "list_assigned_hours_daily",
        "list_assigned_hours_daily_by_parent_job",
        "list_assigned_hours_daily_groupby_tag",
        "list_schedule_weekly",
        "list_workload_daily",
        "list_workload_daily_by_user",
        "list_workload_weekly",
        "list_workload_weekly_by_user",
    ],
)
@pytest.mark.usefixtures("fixed_local_datetime")
def test_日付を省略して今日以降を終了日の制限なしで取得する(service, monkeypatch, tmp_path, module_name):
    module = importlib.import_module(f"annoworkcli.schedule.{module_name}")
    monkeypatch.setattr(module, "build_annoworkapi", lambda _args: service)
    service.api.get_schedules.return_value[0].update(start_date="2026-10-21", end_date="2026-12-01")
    output = tmp_path / "result.json"
    args = module.add_parser().parse_args(["--workspace_id", "workspace", "--format", "json", "--output", str(output)])
    args.subcommand_func(args)
    rows = json.loads(output.read_text())
    assert rows
    assert service.api.get_schedules.call_args.kwargs["query_params"]["term_start"] == "2026-10-21"
    assert service.api.get_schedules.call_args.kwargs["query_params"]["term_end"] is None
    if "date" in rows[0]:
        assert rows[0]["date"] == "2026-10-21"
        assert rows[-1]["date"] == "2026-12-01"

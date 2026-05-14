import argparse

import pandas
import pytest

from annoworkcli.common.cli import add_workspace_id_argument_with_env_fallback, resolve_required_workspace_id
from annoworkcli.common.exeptions import CommandLineArgumentError
from annoworkcli.schedule_actual.common import DAILY_COLUMNS
from annoworkcli.schedule_actual.list_daily import main as schedule_actual_list_daily_main
from annoworkcli.schedule_actual.list_daily import parse_args as parse_schedule_actual_list_daily_args
from annoworkcli.workspace.list_workspace import parse_args as parse_workspace_list_args


class TestResolveRequiredWorkspaceId:
    def test_cli引数を優先する(self, monkeypatch):
        monkeypatch.setenv("ANNOWORK_WORKSPACE_ID", "workspace_from_env")

        actual = resolve_required_workspace_id(argparse.Namespace(workspace_id="workspace_from_cli"))

        assert actual == "workspace_from_cli"

    def test環境変数から取得する(self, monkeypatch):
        monkeypatch.setenv("ANNOWORK_WORKSPACE_ID", "workspace_from_env")

        actual = resolve_required_workspace_id(argparse.Namespace(workspace_id=None))

        assert actual == "workspace_from_env"

    def test環境変数が空文字ならエラー(self, monkeypatch):
        monkeypatch.setenv("ANNOWORK_WORKSPACE_ID", "")

        with pytest.raises(CommandLineArgumentError):
            resolve_required_workspace_id(argparse.Namespace(workspace_id=None))

    def test未指定ならエラー(self, monkeypatch):
        monkeypatch.delenv("ANNOWORK_WORKSPACE_ID", raising=False)

        with pytest.raises(CommandLineArgumentError):
            resolve_required_workspace_id(argparse.Namespace(workspace_id=None))


def test_add_workspace_id_argument_with_env_fallback():
    parser = argparse.ArgumentParser()

    add_workspace_id_argument_with_env_fallback(parser)

    help_text = parser.format_help()
    assert "--workspace_id" in help_text
    assert "ANNOWORK_WORKSPACE_ID" in help_text


def test_workspace_listのworkspace_idは省略可能():
    parser = argparse.ArgumentParser()

    parse_workspace_list_args(parser)
    args = parser.parse_args([])

    assert args.workspace_id is None


def test_schedule_actual_list_dailyで環境変数のworkspace_idを使う(monkeypatch):
    parser = argparse.ArgumentParser()
    parse_schedule_actual_list_daily_args(parser)
    args = parser.parse_args(["--parent_job_id", "parent_job_1"])
    monkeypatch.setenv("ANNOWORK_WORKSPACE_ID", "workspace_from_env")

    captured: dict[str, object] = {}

    monkeypatch.setattr("annoworkcli.schedule_actual.list_daily.build_annoworkapi", lambda _args: object())

    def fake_get_daily_schedule_actual_df(
        *,
        annowork_service,
        workspace_id,
        parent_job_id,
        start_date,
        end_date,
        timezone_offset_hours,
    ):
        captured["annowork_service"] = annowork_service
        captured["workspace_id"] = workspace_id
        captured["parent_job_id"] = parent_job_id
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        captured["timezone_offset_hours"] = timezone_offset_hours
        return pandas.DataFrame(columns=DAILY_COLUMNS)

    monkeypatch.setattr("annoworkcli.schedule_actual.list_daily.get_daily_schedule_actual_df", fake_get_daily_schedule_actual_df)
    monkeypatch.setattr(
        "annoworkcli.schedule_actual.list_daily.print_df",
        lambda df, output, output_format: captured.update({"output": output, "output_format": output_format, "columns": list(df.columns)}),
    )

    schedule_actual_list_daily_main(args)

    assert captured["workspace_id"] == "workspace_from_env"
    assert captured["parent_job_id"] == "parent_job_1"
    assert captured["columns"] == DAILY_COLUMNS

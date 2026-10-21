import datetime
from unittest.mock import Mock

import pytest
import requests

from annoworkcli.__main__ import create_parser
from annoworkcli.schedule.update_start_date import UpdateStartDate, main


@pytest.fixture
def start_date_service(service):
    service.api.get_workspace_members.return_value = [
        {"workspace_member_id": name, "user_id": name, "username": name.title()} for name in ["alice", "bob", "chris", "dave", "eve", "fall"]
    ]
    service.api.get_schedules.return_value = [
        {
            "schedule_id": name,
            "job_id": "parent",
            "workspace_member_id": name,
            "end_date": "2026-12-31",
            "start_date": start,
            "type": "percentage" if index % 2 else "hours",
            "value": 50 if index % 2 else 4,
            "updated_datetime": "2026-10-10T00:00:00Z",
        }
        for index, (name, start) in enumerate(
            [
                ("alice", "2026-10-15"),
                ("bob", "2026-10-15"),
                ("chris", "2026-10-31"),
                ("dave", "2026-10-31"),
                ("eve", "2026-10-01"),
                ("fall", "2026-10-01"),
            ]
        )
    ]
    return service


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({}, {"alice", "bob", "chris", "dave"}),
        ({"from_start_date": "2026-10-16"}, {"chris", "dave"}),
        ({"to_start_date": "2026-10-15"}, {"alice", "bob"}),
        ({"from_start_date": "2026-10-15", "to_start_date": "2026-10-15"}, {"alice", "bob"}),
        ({"user_ids": ["alice", "chris", "alice"]}, {"alice", "chris"}),
        ({"user_ids": ["alice", "chris"], "from_start_date": "2026-10-16"}, {"chris"}),
        ({"from_start_date": "2026-11-01"}, set()),
    ],
)
def test_絞り込み条件をANDで適用し昨日以前に開始した計画は常に除外する(start_date_service, options, expected):
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(
        parent_job_id="parent", start_date="2026-12-15", **options
    )
    calls = start_date_service.api.put_schedule.call_args_list
    assert {call.args[1] for call in calls} == expected
    assert len(calls) == len(expected)
    originals = {schedule["schedule_id"]: schedule for schedule in start_date_service.api.get_schedules.return_value}
    for call in calls:
        old = originals[call.args[1]]
        assert call.args[0] == "workspace"
        assert call.kwargs["request_body"] == {
            **{key: old[key] for key in ["job_id", "workspace_member_id", "end_date", "type", "value"]},
            "start_date": "2026-12-15",
            "last_updated_datetime": old["updated_datetime"],
        }


def test_前倒しでき変更のない計画はスキップする(start_date_service, caplog):
    caplog.set_level("INFO")
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", start_date="2026-10-15")
    assert {call.args[1] for call in start_date_service.api.put_schedule.call_args_list} == {"chris", "dave"}
    assert all(call.kwargs["request_body"]["start_date"] == "2026-10-15" for call in start_date_service.api.put_schedule.call_args_list)
    assert caplog.records[-1].getMessage() == "成功: 2 件、スキップ: 2 件、失敗: 0 件"


def test_今日開始する計画と将来開始の複数計画もすべて対象にする(start_date_service):
    old = start_date_service.api.get_schedules.return_value[0]
    start_date_service.api.get_schedules.return_value = [
        {**old, "schedule_id": "today", "start_date": "2026-10-10"},
        {**old, "schedule_id": "future", "start_date": "2026-11-01", "end_date": "2026-12-31"},
        {**old, "schedule_id": "yesterday", "start_date": "2026-10-09"},
    ]
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", start_date="2026-12-15")
    assert {call.args[1] for call in start_date_service.api.put_schedule.call_args_list} == {"today", "future"}


@pytest.mark.parametrize("new_start", ["2026-10-10", "2026-12-31"])
def test_変更後の開始日が今日でも終了日と同日でも更新できる(start_date_service, new_start):
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", start_date=new_start)
    assert len(start_date_service.api.put_schedule.call_args_list) == 4


def test_後続計画の期間が逆転する場合も全件更新前に中止する(start_date_service):
    start_date_service.api.get_schedules.return_value[3]["end_date"] = "2026-12-01"
    start_date_service.api.get_schedules.return_value[3]["start_date"] = "2026-10-31"
    with pytest.raises(ValueError):
        UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", start_date="2026-12-15")
    start_date_service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [
        {"start_date": "2026-10-09"},
        {"from_start_date": "2026-10-09"},
        {"to_start_date": "2026-10-09"},
        {"from_start_date": "2026-11-01", "to_start_date": "2026-10-31"},
        {"start_date": "20261130"},
        {"from_start_date": "2026-02-30"},
        {"to_start_date": "invalid"},
    ],
)
def test_不正な日付はAPIアクセス前に拒否する(start_date_service, options):
    with pytest.raises(ValueError):
        UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(
            parent_job_id="parent", **{"start_date": "2026-12-15", **options}
        )
    start_date_service.api.get_schedules.assert_not_called()
    start_date_service.api.get_workspace_members.assert_not_called()
    start_date_service.api.put_schedule.assert_not_called()


def test_CLIでも不正な日付は認証前に拒否する(monkeypatch):
    clock = Mock(wraps=datetime.datetime)
    clock.now.return_value = datetime.datetime(2026, 10, 10, tzinfo=datetime.UTC)
    monkeypatch.setattr("annoworkcli.schedule.update_start_date.datetime.datetime", clock)
    api = Mock()
    monkeypatch.setattr("annoworkcli.schedule.update_start_date.cli.build_annoworkapi", api)
    args = create_parser().parse_args(
        ["schedule", "update_start_date", "--workspace_id", "workspace", "--parent_job_id", "parent", "--start_date", "2026-10-09"]
    )
    with pytest.raises(ValueError):
        main(args)
    api.assert_not_called()


@pytest.mark.parametrize("answer", ["y", "N"])
def test_確認は全体で一度だけ行い拒否した場合は更新しない(start_date_service, monkeypatch, answer):
    answers = iter([answer])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10").main(parent_job_id="parent", start_date="2026-12-15")
    assert next(answers, None) is None
    assert start_date_service.api.put_schedule.call_count == (4 if answer == "y" else 0)


def test_dry_runは確認も更新もせず変更一覧を表示する(start_date_service, monkeypatch, caplog):
    caplog.set_level("INFO")
    prompt = Mock(side_effect=AssertionError("確認してはいけません"))
    monkeypatch.setattr("builtins.input", prompt)
    UpdateStartDate(start_date_service, "workspace", today="2026-10-10").main(parent_job_id="parent", start_date="2026-12-15", dry_run=True)
    start_date_service.api.put_schedule.assert_not_called()
    prompt.assert_not_called()
    for user in ["alice", "bob", "chris", "dave"]:
        assert f"user_id='{user}'" in caplog.text
    assert "2026-10-15 → 2026-12-15" in caplog.text
    assert "2026-10-31 → 2026-12-15" in caplog.text
    assert "end_date='2026-12-31'" in caplog.text
    assert "dry_run: 4 件" in caplog.text


@pytest.mark.parametrize("status", [403, 404, 409])
def test_APIエラーでも後続を処理して失敗IDと元の開始日を報告する(start_date_service, caplog, status):
    caplog.set_level("INFO")
    response = requests.Response()
    response.status_code = status
    start_date_service.api.put_schedule.side_effect = [requests.HTTPError(response=response), {}, {}, {}]
    with pytest.raises(RuntimeError):
        UpdateStartDate(start_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", start_date="2026-12-15")
    assert start_date_service.api.put_schedule.call_count == 4
    assert "schedule_id='alice'" in caplog.text
    assert "before_start_date='2026-10-15'" in caplog.text
    assert caplog.records[-1].getMessage() == "成功: 3 件、スキップ: 0 件、失敗: 1 件"
    assert any(record.exc_info for record in caplog.records if record.levelname == "WARNING")

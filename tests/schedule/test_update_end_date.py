import datetime
from unittest.mock import Mock

import pytest
import requests

from annoworkcli.__main__ import create_parser
from annoworkcli.schedule.update_end_date import UpdateEndDate, main


@pytest.fixture
def end_date_service(service):
    service.api.get_workspace_members.return_value = [
        {"workspace_member_id": name, "user_id": name, "username": name.title()} for name in ["alice", "bob", "chris", "dave", "eve", "fall"]
    ]
    service.api.get_schedules.return_value = [
        {
            "schedule_id": name,
            "job_id": "parent",
            "workspace_member_id": name,
            "start_date": "2026-09-01",
            "end_date": end,
            "type": "percentage" if index % 2 else "hours",
            "value": 50 if index % 2 else 4,
            "updated_datetime": "2026-10-10T00:00:00Z",
        }
        for index, (name, end) in enumerate(
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
        ({"from_end_date": "2026-10-16"}, {"chris", "dave"}),
        ({"to_end_date": "2026-10-15"}, {"alice", "bob"}),
        ({"from_end_date": "2026-10-15", "to_end_date": "2026-10-15"}, {"alice", "bob"}),
        ({"user_ids": ["alice", "chris", "alice"]}, {"alice", "chris"}),
        ({"user_ids": ["alice", "chris"], "from_end_date": "2026-10-16"}, {"chris"}),
        ({"from_end_date": "2026-11-01"}, set()),
    ],
)
def test_絞り込み条件をANDで適用し終了済みの計画は常に除外する(end_date_service, options, expected):
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-11-30", **options)
    calls = end_date_service.api.put_schedule.call_args_list
    assert {call.args[1] for call in calls} == expected
    assert len(calls) == len(expected)
    originals = {schedule["schedule_id"]: schedule for schedule in end_date_service.api.get_schedules.return_value}
    for call in calls:
        old = originals[call.args[1]]
        assert call.args[0] == "workspace"
        assert call.kwargs["request_body"] == {
            **{key: old[key] for key in ["job_id", "workspace_member_id", "start_date", "type", "value"]},
            "end_date": "2026-11-30",
            "last_updated_datetime": old["updated_datetime"],
        }


def test_延長と短縮を混在でき変更のない計画はスキップする(end_date_service, caplog):
    caplog.set_level("INFO")
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-10-15")
    assert {call.args[1] for call in end_date_service.api.put_schedule.call_args_list} == {"chris", "dave"}
    assert all(call.kwargs["request_body"]["end_date"] == "2026-10-15" for call in end_date_service.api.put_schedule.call_args_list)
    assert caplog.records[-1].getMessage() == "成功: 2 件、スキップ: 2 件、失敗: 0 件"


def test_今日終了する計画と将来開始の複数計画もすべて対象にする(end_date_service):
    old = end_date_service.api.get_schedules.return_value[0]
    end_date_service.api.get_schedules.return_value = [
        {**old, "schedule_id": "today", "end_date": "2026-10-10"},
        {**old, "schedule_id": "future", "start_date": "2026-11-01", "end_date": "2026-11-15"},
        {**old, "schedule_id": "yesterday", "end_date": "2026-10-09"},
    ]
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-11-30")
    assert {call.args[1] for call in end_date_service.api.put_schedule.call_args_list} == {"today", "future"}


def test_変更後の終了日が今日でも開始日と同日でも更新できる(end_date_service):
    end_date_service.api.get_schedules.return_value[0]["start_date"] = "2026-10-10"
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-10-10")
    assert len(end_date_service.api.put_schedule.call_args_list) == 4


def test_後続計画の期間が逆転する場合も全件更新前に中止する(end_date_service):
    end_date_service.api.get_schedules.return_value[3]["start_date"] = "2026-12-01"
    end_date_service.api.get_schedules.return_value[3]["end_date"] = "2026-12-31"
    with pytest.raises(ValueError):
        UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-11-30")
    end_date_service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [
        {"end_date": "2026-10-09"},
        {"from_end_date": "2026-10-09"},
        {"to_end_date": "2026-10-09"},
        {"from_end_date": "2026-11-01", "to_end_date": "2026-10-31"},
        {"end_date": "20261130"},
        {"from_end_date": "2026-02-30"},
        {"to_end_date": "invalid"},
    ],
)
def test_不正な日付はAPIアクセス前に拒否する(end_date_service, options):
    with pytest.raises(ValueError):
        UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(
            parent_job_id="parent", **{"end_date": "2026-11-30", **options}
        )
    end_date_service.api.get_schedules.assert_not_called()
    end_date_service.api.get_workspace_members.assert_not_called()
    end_date_service.api.put_schedule.assert_not_called()


def test_CLIでも不正な日付は認証前に拒否する(monkeypatch):
    clock = Mock(wraps=datetime.datetime)
    clock.now.return_value = datetime.datetime(2026, 10, 10).astimezone()
    monkeypatch.setattr("annoworkcli.schedule.update_end_date.datetime.datetime", clock)
    api = Mock()
    monkeypatch.setattr("annoworkcli.schedule.update_end_date.cli.build_annoworkapi", api)
    args = create_parser().parse_args(
        ["schedule", "update_end_date", "--workspace_id", "workspace", "--parent_job_id", "parent", "--end_date", "2026-10-09"]
    )
    with pytest.raises(ValueError):
        main(args)
    api.assert_not_called()


@pytest.mark.parametrize("answer", ["y", "N"])
def test_確認は全体で一度だけ行い拒否した場合は更新しない(end_date_service, monkeypatch, answer):
    answers = iter([answer])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10").main(parent_job_id="parent", end_date="2026-11-30")
    assert next(answers, None) is None
    assert end_date_service.api.put_schedule.call_count == (4 if answer == "y" else 0)


def test_dry_runは確認も更新もせず変更一覧を表示する(end_date_service, monkeypatch, caplog):
    caplog.set_level("INFO")
    prompt = Mock(side_effect=AssertionError("確認してはいけません"))
    monkeypatch.setattr("builtins.input", prompt)
    UpdateEndDate(end_date_service, "workspace", today="2026-10-10").main(parent_job_id="parent", end_date="2026-11-30", dry_run=True)
    end_date_service.api.put_schedule.assert_not_called()
    prompt.assert_not_called()
    for user in ["alice", "bob", "chris", "dave"]:
        assert f"user_id='{user}'" in caplog.text
    assert "2026-10-15 → 2026-11-30" in caplog.text
    assert "2026-10-31 → 2026-11-30" in caplog.text
    assert "start_date='2026-09-01'" in caplog.text
    assert "dry_run: 4 件" in caplog.text


@pytest.mark.parametrize("status", [403, 404, 409])
def test_APIエラーでも後続を処理して失敗IDと元の終了日を報告する(end_date_service, caplog, status):
    caplog.set_level("INFO")
    response = requests.Response()
    response.status_code = status
    end_date_service.api.put_schedule.side_effect = [requests.HTTPError(response=response), {}, {}, {}]
    with pytest.raises(RuntimeError):
        UpdateEndDate(end_date_service, "workspace", today="2026-10-10", all_yes=True).main(parent_job_id="parent", end_date="2026-11-30")
    assert end_date_service.api.put_schedule.call_count == 4
    assert "schedule_id='alice'" in caplog.text
    assert "before_end_date='2026-10-15'" in caplog.text
    assert caplog.records[-1].getMessage() == "成功: 3 件、スキップ: 0 件、失敗: 1 件"
    assert any(record.exc_info for record in caplog.records if record.levelname == "WARNING")

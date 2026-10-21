import datetime
from unittest.mock import patch
from uuid import UUID

import pytest
import requests

from annoworkcli.schedule.create_schedule import CreateSchedule


def test_複数人を重複なく親ジョブへ100パーセントで作成する(service):
    service.api.get_workspace_members.return_value.append({"user_id": "bob", "workspace_member_id": "member-bob"})
    CreateSchedule(service, "workspace", all_yes=True).main(
        parent_job_id="parent", user_ids=["alice", "bob", "alice"], start_date="2026-11-02", end_date="2026-11-06"
    )
    calls = service.api.put_schedule.call_args_list
    assert len(calls) == 2
    assert len({args.args[1] for args in calls}) == 2
    for args, member_id in zip(calls, ["member", "member-bob"], strict=True):
        assert args.args[0] == "workspace"
        assert UUID(args.args[1]).version == 4
        assert args.kwargs["request_body"] == {
            "job_id": "parent",
            "workspace_member_id": member_id,
            "start_date": "2026-11-02",
            "end_date": "2026-11-06",
            "type": "percentage",
            "value": 100,
        }


def test_開始日の省略時は実行環境の今日を使用する(service):
    now = datetime.datetime(2026, 11, 2, 0, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    with patch("annoworkcli.schedule.create_schedule.datetime.datetime") as clock:
        clock.now.return_value.astimezone.return_value = now
        CreateSchedule(service, "workspace", all_yes=True).main(parent_job_id="parent", user_ids=["alice"], end_date="2026-11-06")
    assert service.api.put_schedule.call_args.kwargs["request_body"]["start_date"] == "2026-11-02"


@pytest.mark.parametrize(("assignment", "expected_type", "expected_value"), [({"hours": 4}, "hours", 4), ({"percentage": 50}, "percentage", 50)])
def test_指定した割当量を使用する(service, assignment, expected_type, expected_value):
    CreateSchedule(service, "workspace", all_yes=True).main(
        parent_job_id="parent", user_ids=["alice"], start_date="2026-11-02", end_date="2026-11-06", **assignment
    )
    body = service.api.put_schedule.call_args.kwargs["request_body"]
    assert (body["type"], body["value"]) == (expected_type, expected_value)


def test_存在しないメンバーは作成せず残りを処理して失敗を報告する(service):
    with pytest.raises(RuntimeError):
        CreateSchedule(service, "workspace", all_yes=True).main(
            parent_job_id="parent", user_ids=["missing", "alice"], start_date="2026-11-02", end_date="2026-11-06"
        )
    assert service.api.put_schedule.call_count == 1
    assert service.api.put_schedule.call_args.kwargs["request_body"]["workspace_member_id"] == "member"


def test_APIの失敗後も残りのメンバーを処理する(service):
    service.api.get_workspace_members.return_value.append({"user_id": "bob", "workspace_member_id": "member-bob"})
    service.api.put_schedule.side_effect = [requests.exceptions.HTTPError(), {}]
    with pytest.raises(RuntimeError):
        CreateSchedule(service, "workspace", all_yes=True).main(
            parent_job_id="parent", user_ids=["alice", "bob"], start_date="2026-11-02", end_date="2026-11-06"
        )
    assert service.api.put_schedule.call_count == 2


def test_確認で拒否したユーザーは作成せずALL以降は確認を省略する(service, monkeypatch):
    service.api.get_workspace_members.return_value.extend(
        [{"user_id": "bob", "workspace_member_id": "member-bob"}, {"user_id": "charlie", "workspace_member_id": "member-charlie"}]
    )
    answers = iter(["N", "ALL"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    CreateSchedule(service, "workspace").main(
        parent_job_id="parent", user_ids=["alice", "bob", "charlie"], start_date="2026-11-02", end_date="2026-11-06"
    )
    assert [call.kwargs["request_body"]["workspace_member_id"] for call in service.api.put_schedule.call_args_list] == [
        "member-bob",
        "member-charlie",
    ]


@pytest.mark.parametrize(
    "options",
    [
        {"user_ids": []},
        {"end_date": "2026-11-01"},
        {"start_date": "invalid"},
        {"start_date": "20261102"},
        {"hours": 0},
        {"hours": 25},
        {"percentage": 101},
        {"percentage": float("nan")},
        {"hours": float("inf")},
        {"hours": 4, "percentage": 50},
    ],
)
def test_不正な入力では書き込まない(service, options):
    values = {"parent_job_id": "parent", "user_ids": ["alice"], "start_date": "2026-11-02", "end_date": "2026-11-06", **options}
    with pytest.raises(ValueError):
        CreateSchedule(service, "workspace", all_yes=True).main(**values)
    service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize("assignment", [{"hours": 0.01}, {"hours": 24}, {"percentage": 0.01}, {"percentage": 100}])
def test_割当量の境界値と開始終了が同日の計画を許可する(service, assignment):
    CreateSchedule(service, "workspace", all_yes=True).main(
        parent_job_id="parent", user_ids=["alice"], start_date="2026-11-02", end_date="2026-11-02", **assignment
    )
    assert service.api.put_schedule.call_count == 1

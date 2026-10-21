import pytest
import requests

from annoworkcli.schedule.update_schedule import UpdateSchedule

pytestmark = pytest.mark.usefixtures("fixed_local_datetime")


@pytest.fixture
def update_service(service):
    service.api.get_schedule.return_value = {
        "schedule_id": "schedule",
        "workspace_id": "workspace",
        "job_id": "parent",
        "workspace_member_id": "member",
        "start_date": "2026-11-02",
        "end_date": "2026-11-06",
        "type": "percentage",
        "value": 100,
        "updated_datetime": "2026-10-21T00:00:00Z",
        "created_datetime": "2026-10-20T00:00:00Z",
    }
    return service


@pytest.mark.parametrize(
    "changes",
    [
        {"start_date": "2026-11-03"},
        {"end_date": "2026-11-30"},
        {"hours": 4},
        {"percentage": 50},
        {"start_date": "2026-12-01", "end_date": "2026-12-06", "hours": 2},
    ],
)
def test_指定項目だけを更新し親ジョブと担当者と競合検出用の日時を維持する(update_service, changes):
    old = update_service.api.get_schedule.return_value.copy()
    UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule"], **changes)
    body = update_service.api.put_schedule.call_args.kwargs["request_body"]
    expected = {key: old[key] for key in ["job_id", "workspace_member_id", "start_date", "end_date", "type", "value"]}
    expected["last_updated_datetime"] = old["updated_datetime"]
    for key in ["start_date", "end_date"]:
        if key in changes:
            expected[key] = changes[key]
    for key in ["hours", "percentage"]:
        if key in changes:
            expected.update(type=key, value=changes[key])
    assert body == expected
    assert update_service.api.get_schedule.return_value == old


def test_重複したIDと変更のない計画は更新しない(update_service):
    UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule", "schedule"], percentage=100)
    update_service.api.put_schedule.assert_not_called()
    assert update_service.api.get_schedule.call_count == 1


def test_複数計画それぞれの未指定項目を維持する(update_service):
    old = update_service.api.get_schedule.return_value.copy()
    update_service.api.get_schedule.side_effect = [
        old,
        {**old, "job_id": "other-parent", "workspace_member_id": "other-member", "start_date": "2026-11-10"},
    ]
    UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule", "other", "schedule"], end_date="2026-11-30")
    bodies = [call.kwargs["request_body"] for call in update_service.api.put_schedule.call_args_list]
    assert len(bodies) == 2
    assert bodies[1]["job_id"] == "other-parent"
    assert bodies[1]["workspace_member_id"] == "other-member"
    assert bodies[1]["start_date"] == "2026-11-10"


@pytest.mark.parametrize("status", [404, 403, 409])
def test_APIエラー後も残りを処理して失敗を報告する(update_service, status):
    response = requests.Response()
    response.status_code = status
    error = requests.exceptions.HTTPError(response=response)
    if status == 409:
        update_service.api.put_schedule.side_effect = [error, {}]
    else:
        update_service.api.get_schedule.side_effect = [error, update_service.api.get_schedule.return_value]
    with pytest.raises(RuntimeError):
        UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["bad", "good"], percentage=50)
    assert update_service.api.put_schedule.call_args.args[1] == "good"
    assert update_service.api.put_schedule.call_count == (2 if status == 409 else 1)


def test_元の終了日より後の開始日に変更すると失敗する(update_service):
    with pytest.raises(RuntimeError):
        UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule"], start_date="2026-11-07")
    update_service.api.put_schedule.assert_not_called()


def test_確認で拒否したら更新しない(update_service, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "N")
    UpdateSchedule(update_service, "workspace").main(schedule_ids=["schedule"], percentage=50)
    update_service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize(
    "options", [{}, {"schedule_ids": []}, {"hours": 0}, {"percentage": float("inf")}, {"hours": 4, "percentage": 50}, {"start_date": "invalid"}]
)
def test_不正な更新条件では書き込まない(update_service, options):
    # 空のID一覧を検証するときも更新項目を指定する。
    values = {"schedule_ids": ["schedule"], **options}
    if options.get("schedule_ids") == []:
        values["hours"] = 4
    with pytest.raises(ValueError):
        UpdateSchedule(update_service, "workspace", all_yes=True).main(**values)
    update_service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize("answer", ["y", "N"])
def test_複数計画の更新確認は一回だけ行う(update_service, monkeypatch, caplog, answer):
    caplog.set_level("INFO")
    answers = iter([answer])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    UpdateSchedule(update_service, "workspace").main(schedule_ids=["first", "second", "first"], percentage=50)
    assert next(answers, None) is None
    assert update_service.api.put_schedule.call_count == (2 if answer == "y" else 0)
    expected_summary = "成功: 2 件、スキップ: 0 件、失敗: 0 件" if answer == "y" else "成功: 0 件、スキップ: 2 件、失敗: 0 件"
    assert caplog.records[-1].getMessage() == expected_summary


@pytest.mark.parametrize("start_date", ["2026-10-20", "2026-10-21", "2026-10-22"])
def test_昨日以降の開始日への変更を許可する(update_service, start_date):
    UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule"], start_date=start_date)
    assert update_service.api.put_schedule.call_args.kwargs["request_body"]["start_date"] == start_date


@pytest.mark.parametrize("allow_past_start_date", [False, True])
def test_昨日より前への開始日変更は明示的な許可が必要(update_service, allow_past_start_date):
    command = UpdateSchedule(update_service, "workspace", all_yes=True)
    if allow_past_start_date:
        command.main(schedule_ids=["schedule"], start_date="2026-10-19", allow_past_start_date=True)
        assert update_service.api.put_schedule.call_count == 1
    else:
        with pytest.raises(ValueError):
            command.main(schedule_ids=["schedule"], start_date="2026-10-19")
        update_service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize("changes", [{"end_date": "2026-11-30"}, {"hours": 4}, {"percentage": 50}])
def test_開始日省略なら過去に開始した計画も更新できる(update_service, changes):
    update_service.api.get_schedule.return_value["start_date"] = "2026-10-01"
    UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule"], **changes)
    assert update_service.api.put_schedule.call_args.kwargs["request_body"]["start_date"] == "2026-10-01"


@pytest.mark.parametrize("start_date", ["invalid", "20261019", "2026-11-07"])
def test_過去開始日を許可しても不正な日付では更新しない(update_service, start_date):
    with pytest.raises((ValueError, RuntimeError)):
        UpdateSchedule(update_service, "workspace", all_yes=True).main(schedule_ids=["schedule"], start_date=start_date, allow_past_start_date=True)
    update_service.api.put_schedule.assert_not_called()

import pytest
import requests

from annoworkcli.schedule.delete_schedule import DeleteSchedule

pytestmark = pytest.mark.usefixtures("fixed_local_datetime")


@pytest.fixture(autouse=True)
def schedules(service):
    base = service.api.get_schedules.return_value[0]
    rows = [
        {**base, "schedule_id": name, "start_date": start, "end_date": end, "job_id": parent, "workspace_member_id": member}
        for name, start, end, parent, member in [
            ("past", "2026-10-01", "2026-10-20", "parent", "member"),
            ("ongoing", "2026-10-01", "2026-10-21", "parent", "member"),
            ("lower", "2026-11-01", "2026-12-10", "parent", "member"),
            ("upper", "2026-11-30", "2026-12-10", "parent", "member"),
            ("later", "2026-12-01", "2026-12-10", "parent", "member"),
            ("other-parent", "2026-11-01", "2026-11-30", "other", "member"),
            ("bob", "2026-11-01", "2026-11-30", "parent", "member-bob"),
        ]
    ]
    service.api.get_schedules.return_value = rows
    service.api.get_workspace_members.return_value.append({"workspace_member_id": "member-bob", "user_id": "bob"})
    return rows


@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({}, ["ongoing", "lower", "upper", "later", "bob"]),
        ({"from_start_date": "2026-11-01", "to_start_date": "2026-11-30", "user_ids": ["alice"]}, ["lower", "upper"]),
        ({"from_start_date": "2026-11-30"}, ["upper", "later"]),
        ({"to_start_date": "2026-10-01"}, ["ongoing"]),
        ({"user_ids": ["bob", "alice"]}, ["ongoing", "lower", "upper", "later", "bob"]),
        ({"user_ids": ["missing"]}, []),
        ({"user_ids": []}, []),
    ],
)
def test_親ジョブとユーザーと開始日で絞り終了日が昨日以前の計画を除外する(service, options, expected):
    DeleteSchedule(service, "workspace", all_yes=True).main(parent_job_id="parent", **options)
    assert [call.args[1] for call in service.api.delete_schedule.call_args_list] == expected
    service.api.put_schedule.assert_not_called()


@pytest.mark.parametrize("dry_run", [False, True])
def test_対象一覧を表示しdry_runでは確認も削除もしない(service, monkeypatch, caplog, dry_run):
    answers = iter(["N"] if not dry_run else [])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    caplog.set_level("INFO")
    DeleteSchedule(service, "workspace").main(parent_job_id="parent", dry_run=dry_run)
    service.api.delete_schedule.assert_not_called()
    assert "削除対象: 5 件" in caplog.text
    assert "ongoing" in caplog.text
    assert "成功: 0 件、スキップ: 5 件、失敗: 0 件" in caplog.text


def test_全件の削除確認を一回だけ行う(service, monkeypatch):
    answers = iter(["y"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    DeleteSchedule(service, "workspace").main(parent_job_id="parent")
    assert service.api.delete_schedule.call_count == 5


@pytest.mark.parametrize(
    "options", [{"from_start_date": "invalid"}, {"to_start_date": "20261101"}, {"from_start_date": "2026-12-01", "to_start_date": "2026-11-01"}]
)
def test_不正な日付はAPI呼び出し前にエラー(service, options):
    with pytest.raises(ValueError):
        DeleteSchedule(service, "workspace", all_yes=True).main(parent_job_id="parent", **options)
    service.api.get_schedules.assert_not_called()
    service.api.delete_schedule.assert_not_called()


def test_削除失敗後も残りを処理して非正常終了する(service, caplog):
    service.api.delete_schedule.side_effect = [requests.exceptions.ConnectionError(), None, None, None, None]
    caplog.set_level("INFO")
    with pytest.raises(RuntimeError):
        DeleteSchedule(service, "workspace", all_yes=True).main(parent_job_id="parent")
    assert service.api.delete_schedule.call_count == 5
    assert "成功: 4 件、スキップ: 0 件、失敗: 1 件" in caplog.text

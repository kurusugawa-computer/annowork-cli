import pytest
import requests

from annoworkcli.schedule.delete_schedule_by_schedule_id import DeleteScheduleByScheduleId

pytestmark = pytest.mark.usefixtures("fixed_local_datetime")


@pytest.mark.parametrize("allow_past_end_date", [False, True])
def test_終了済みは許可時のみ削除し今日終了する計画は削除する(service, allow_past_end_date):
    dates = ["2026-10-20", "2026-10-21", "2026-10-22"]
    service.api.get_schedule.side_effect = [{"start_date": "2026-10-01", "end_date": date} for date in dates]
    DeleteScheduleByScheduleId(service, "workspace", all_yes=True).main(dates, allow_past_end_date=allow_past_end_date)
    assert [call.args[1] for call in service.api.delete_schedule.call_args_list] == (dates if allow_past_end_date else dates[1:])


def test_終了済み計画は確認せずスキップする(service, monkeypatch):
    service.api.get_schedule.return_value = {"end_date": "2026-10-20"}
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("終了済み計画では確認しない"))
    DeleteScheduleByScheduleId(service, "workspace").main(["past"])
    service.api.delete_schedule.assert_not_called()


def test_重複IDは一度だけ削除する(service):
    service.api.get_schedule.return_value = {"end_date": "2026-10-21"}
    DeleteScheduleByScheduleId(service, "workspace", all_yes=True).main(["same", "same"])
    assert service.api.delete_schedule.call_count == 1


def test_dry_runは対象を表示するが確認も削除もしない(service, monkeypatch, caplog):
    service.api.get_schedule.return_value = {"end_date": "2026-10-21"}
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("dry_runでは確認しない"))
    caplog.set_level("INFO")
    DeleteScheduleByScheduleId(service, "workspace", all_yes=True).main(["target"], dry_run=True)
    service.api.delete_schedule.assert_not_called()
    assert "target" in caplog.text


def test_取得失敗と存在しないIDの後も処理して結果を報告する(service, caplog):
    response = requests.Response()
    response.status_code = 404
    service.api.get_schedule.side_effect = [
        requests.exceptions.ConnectionError(),
        requests.exceptions.HTTPError(response=response),
        {"end_date": "2026-10-21"},
    ]
    caplog.set_level("INFO")
    with pytest.raises(RuntimeError):
        DeleteScheduleByScheduleId(service, "workspace", all_yes=True).main(["error", "missing", "ok"])
    assert [call.args[1] for call in service.api.delete_schedule.call_args_list] == ["ok"]
    assert "成功: 1 件、スキップ: 1 件、失敗: 1 件" in caplog.text

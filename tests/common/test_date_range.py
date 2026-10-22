import datetime
from unittest.mock import patch

import pytest

from annoworkcli.common.date_range import resolve_start_date


@pytest.mark.usefixtures("fixed_local_datetime")
def test_開始日省略時はローカル日付の今日にする():
    assert resolve_start_date(None, None) == "2026-10-21"


def test_開始日を明示すれば過去の期間も指定できる():
    assert resolve_start_date("2020-01-01", "2020-01-31") == "2020-01-01"


@pytest.mark.parametrize(
    "start_date,end_date",
    [("2026-10-22", "2026-10-21"), ("20261021", None), ("invalid", None), ("2026-10-21", "2026-02-30"), (None, "2026-10-20")],
)
@pytest.mark.usefixtures("fixed_local_datetime")
def test_不正な取得期間は拒否する(start_date, end_date):
    with pytest.raises(ValueError):
        resolve_start_date(start_date, end_date)


@pytest.fixture
def fixed_local_datetime():
    now = datetime.datetime(2026, 10, 21, 0, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    with patch("datetime.datetime", side_effect=datetime.datetime) as clock:
        clock.now.return_value.astimezone.return_value = now
        yield

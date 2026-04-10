from annoworkcli.expected_working_time.list_expected_working_time_daily_total import get_daily_total_expected_working_hours_df

EXPECTED_WORKING_TIMES = [
    {
        "date": "2022-03-05",
        "workspace_member_id": "alice",
        "expected_working_hours": 1,
    },
    {
        "date": "2022-03-05",
        "workspace_member_id": "bob",
        "expected_working_hours": 2,
    },
    {
        "date": "2022-03-06",
        "workspace_member_id": "alice",
        "expected_working_hours": 3,
    },
    {
        "date": "2022-03-07",
        "workspace_member_id": "alice",
        "expected_working_hours": 0,
    },
]


def test_get_daily_total_expected_working_hours_df():
    actual = get_daily_total_expected_working_hours_df(EXPECTED_WORKING_TIMES)

    assert list(actual.columns) == ["date", "expected_working_hours"]
    assert len(actual) == 2
    assert actual.query("date == '2022-03-05'").iloc[0]["expected_working_hours"] == 3
    assert actual.query("date == '2022-03-06'").iloc[0]["expected_working_hours"] == 3

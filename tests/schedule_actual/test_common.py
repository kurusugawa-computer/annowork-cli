from annoworkcli.schedule_actual.common import build_daily_schedule_actual_df, build_weekly_schedule_actual_df


def test_build_daily_schedule_actual_df():
    actual_hours_by_date = {
        "2022-03-05": 4.0,
    }
    assigned_hours_by_date = {
        "2022-03-06": 2.0,
        "2022-03-07": 3.0,
    }

    actual = build_daily_schedule_actual_df(
        actual_hours_by_date,
        assigned_hours_by_date,
        start_date="2022-03-05",
        end_date="2022-03-07",
    )

    assert list(actual.columns) == [
        "date",
        "assigned_working_hours",
        "actual_working_hours",
        "cumulative_working_hours",
    ]
    assert actual.to_dict("records") == [
        {
            "date": "2022-03-05",
            "assigned_working_hours": 0.0,
            "actual_working_hours": 4.0,
            "cumulative_working_hours": 4.0,
        },
        {
            "date": "2022-03-06",
            "assigned_working_hours": 2.0,
            "actual_working_hours": 0.0,
            "cumulative_working_hours": 6.0,
        },
        {
            "date": "2022-03-07",
            "assigned_working_hours": 3.0,
            "actual_working_hours": 0.0,
            "cumulative_working_hours": 9.0,
        },
    ]


def test_build_weekly_schedule_actual_df():
    daily_df = build_daily_schedule_actual_df(
        {"2022-03-05": 4.0},
        {
            "2022-03-06": 2.0,
            "2022-03-07": 3.0,
            "2022-03-08": 1.0,
        },
        start_date="2022-03-05",
        end_date="2022-03-08",
    )

    actual = build_weekly_schedule_actual_df(daily_df)

    assert list(actual.columns) == [
        "start_date",
        "end_date",
        "assigned_working_hours",
        "actual_working_hours",
        "cumulative_working_hours",
    ]
    assert actual.to_dict("records") == [
        {
            "start_date": "2022-02-27",
            "end_date": "2022-03-05",
            "assigned_working_hours": 0.0,
            "actual_working_hours": 4.0,
            "cumulative_working_hours": 4.0,
        },
        {
            "start_date": "2022-03-06",
            "end_date": "2022-03-12",
            "assigned_working_hours": 6.0,
            "actual_working_hours": 0.0,
            "cumulative_working_hours": 10.0,
        },
    ]


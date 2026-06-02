from typing import TYPE_CHECKING, cast

from annoworkcli.schedule.list_assigned_hours_daily import AssignedHoursDaily
from annoworkcli.schedule_actual.common import build_daily_schedule_actual_df, build_weekly_schedule_actual_df, get_daily_schedule_actual_df

if TYPE_CHECKING:
    from annoworkapi.resource import Resource as AnnoworkResource


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


def test_get_daily_schedule_actual_dfは親ジョブIDで作業計画を取得する(monkeypatch):
    captured: dict[str, object] = {}

    class ListActualWorkingTimeStub:
        def __init__(self, annowork_service, workspace_id, *, timezone_offset_hours):  # noqa: ANN001
            pass

        def get_actual_working_times(self, **_kwargs):  # noqa: ANN003, ANN201
            return []

    class ListAssignedHoursDailyStub:
        def __init__(self, annowork_service, workspace_id):  # noqa: ANN001
            pass

        def get_assigned_hours_daily_list(self, *, start_date, end_date, job_ids, user_ids):  # noqa: ANN001, ANN201
            captured["start_date"] = start_date
            captured["end_date"] = end_date
            captured["job_ids"] = job_ids
            captured["user_ids"] = user_ids
            return [
                AssignedHoursDaily(
                    date="2022-03-06",
                    job_id="parent_job",
                    job_name="親ジョブ",
                    workspace_member_id="member",
                    user_id="user",
                    username="username",
                    assigned_working_hours=5.0,
                )
            ]

    def get_today_str_stub(*, timezone_offset_hours: float | None) -> str:  # noqa: ARG001
        return "2022-03-06"

    monkeypatch.setattr("annoworkcli.schedule_actual.common.get_today_str", get_today_str_stub)
    monkeypatch.setattr("annoworkcli.schedule_actual.common.ListActualWorkingTime", ListActualWorkingTimeStub)
    monkeypatch.setattr("annoworkcli.schedule_actual.common.ListAssignedHoursDaily", ListAssignedHoursDailyStub)

    actual = get_daily_schedule_actual_df(
        annowork_service=cast("AnnoworkResource", object()),
        workspace_id="workspace",
        parent_job_id="parent_job",
        start_date="2022-03-06",
        end_date="2022-03-06",
        timezone_offset_hours=None,
    )

    assert captured == {
        "start_date": "2022-03-06",
        "end_date": "2022-03-06",
        "job_ids": ["parent_job"],
        "user_ids": None,
    }
    assert actual.to_dict("records") == [
        {
            "date": "2022-03-06",
            "assigned_working_hours": 5.0,
            "actual_working_hours": 0.0,
            "cumulative_working_hours": 5.0,
        }
    ]

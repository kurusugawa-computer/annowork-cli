import datetime
from collections.abc import Mapping
from pathlib import Path

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

from annoworkcli.actual_working_time.list_actual_working_hours_daily import create_actual_working_hours_daily_list, filter_actual_daily_list
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import OutputFormat
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily

DAILY_COLUMNS = [
    "date",
    "assigned_working_hours",
    "actual_working_hours",
    "cumulative_working_hours",
]
WEEKLY_COLUMNS = [
    "start_date",
    "end_date",
    "assigned_working_hours",
    "actual_working_hours",
    "cumulative_working_hours",
]


def get_tzinfo(timezone_offset_hours: float | None) -> datetime.tzinfo:
    if timezone_offset_hours is not None:
        return datetime.timezone(datetime.timedelta(hours=timezone_offset_hours))
    return datetime.datetime.now().astimezone().tzinfo  # type: ignore[return-value]


def get_today_str(*, timezone_offset_hours: float | None) -> str:
    tzinfo = get_tzinfo(timezone_offset_hours)
    return datetime.datetime.now(tz=tzinfo).date().isoformat()


def build_daily_schedule_actual_df(
    actual_hours_by_date: Mapping[str, float],
    assigned_hours_by_date: Mapping[str, float],
    *,
    start_date: str | None,
    end_date: str | None,
) -> pandas.DataFrame:
    available_dates = set(actual_hours_by_date.keys()) | set(assigned_hours_by_date.keys())

    if len(available_dates) == 0 and (start_date is None or end_date is None):
        return pandas.DataFrame(columns=DAILY_COLUMNS)

    range_start = start_date or min(available_dates)
    range_end = end_date or max(available_dates)
    if range_start > range_end:
        return pandas.DataFrame(columns=DAILY_COLUMNS)

    df = pandas.DataFrame({"date": pandas.date_range(range_start, range_end).date})
    df["date"] = df["date"].apply(lambda e: e.isoformat())
    df["assigned_working_hours"] = df["date"].map(assigned_hours_by_date).fillna(0.0)
    df["actual_working_hours"] = df["date"].map(actual_hours_by_date).fillna(0.0)
    df["cumulative_working_hours"] = (df["assigned_working_hours"] + df["actual_working_hours"]).cumsum()
    return df[DAILY_COLUMNS]


def build_weekly_schedule_actual_df(daily_df: pandas.DataFrame) -> pandas.DataFrame:
    if len(daily_df) == 0:
        return pandas.DataFrame(columns=WEEKLY_COLUMNS)

    df = daily_df.copy()
    df["dt_date"] = pandas.to_datetime(df["date"])
    df_weekly = df.resample("W-SUN", on="dt_date", label="left", closed="left").agg(
        {
            "assigned_working_hours": "sum",
            "actual_working_hours": "sum",
        }
    )
    df_weekly.reset_index(inplace=True)
    df_weekly.rename(columns={"dt_date": "dt_start_date"}, inplace=True)
    df_weekly["dt_end_date"] = df_weekly["dt_start_date"] + pandas.Timedelta(days=6)
    df_weekly["start_date"] = df_weekly["dt_start_date"].dt.date.apply(lambda e: e.isoformat())
    df_weekly["end_date"] = df_weekly["dt_end_date"].dt.date.apply(lambda e: e.isoformat())
    df_weekly["cumulative_working_hours"] = (df_weekly["assigned_working_hours"] + df_weekly["actual_working_hours"]).cumsum()
    return df_weekly[WEEKLY_COLUMNS]


def _sum_working_hours_by_date(df: pandas.DataFrame, hours_column: str) -> dict[str, float]:
    if len(df) == 0:
        return {}
    return df.groupby("date", as_index=True)[hours_column].sum().to_dict()


def _clamp_range(
    *, start_date: str | None, end_date: str | None, lower: str | None = None, upper: str | None = None
) -> tuple[str | None, str | None]:
    result_start = start_date
    result_end = end_date
    if lower is not None:
        result_start = lower if result_start is None else max(result_start, lower)
    if upper is not None:
        result_end = upper if result_end is None else min(result_end, upper)
    return result_start, result_end


def get_daily_schedule_actual_df(
    *,
    annowork_service: AnnoworkResource,
    workspace_id: str,
    parent_job_id: str,
    start_date: str | None,
    end_date: str | None,
    timezone_offset_hours: float | None,
) -> pandas.DataFrame:
    today = get_today_str(timezone_offset_hours=timezone_offset_hours)
    yesterday = (datetime.date.fromisoformat(today) - datetime.timedelta(days=1)).isoformat()

    list_actual_working_time_obj = ListActualWorkingTime(
        annowork_service=annowork_service,
        workspace_id=workspace_id,
        timezone_offset_hours=timezone_offset_hours,
    )
    actual_start_date, actual_end_date = _clamp_range(start_date=start_date, end_date=end_date, upper=yesterday)
    assigned_start_date, assigned_end_date = _clamp_range(start_date=start_date, end_date=end_date, lower=today)

    actual_hours_by_date: dict[str, float] = {}
    if actual_start_date is None or actual_end_date is None or actual_start_date <= actual_end_date:
        actual_working_times = list_actual_working_time_obj.get_actual_working_times(
            parent_job_ids=[parent_job_id],
            start_date=actual_start_date,
            end_date=actual_end_date,
            user_ids=None,
            is_set_additional_info=True,
        )
        actual_daily_list = create_actual_working_hours_daily_list(
            actual_working_times,
            timezone_offset_hours=timezone_offset_hours,
            show_notes=False,
        )
        actual_daily_list = filter_actual_daily_list(actual_daily_list, start_date=actual_start_date, end_date=actual_end_date)
        actual_daily_df = pandas.DataFrame([e.to_dict() for e in actual_daily_list])
        actual_hours_by_date = _sum_working_hours_by_date(actual_daily_df, "actual_working_hours")

    assigned_hours_by_date: dict[str, float] = {}
    if assigned_start_date is None or assigned_end_date is None or assigned_start_date <= assigned_end_date:
        assigned_daily_list = ListAssignedHoursDaily(
            annowork_service=annowork_service,
            workspace_id=workspace_id,
        ).get_assigned_hours_daily_list(
            start_date=assigned_start_date,
            end_date=assigned_end_date,
            job_ids=[parent_job_id],
            user_ids=None,
        )
        assigned_daily_df = pandas.DataFrame([e.to_dict() for e in assigned_daily_list])
        assigned_hours_by_date = _sum_working_hours_by_date(assigned_daily_df, "assigned_working_hours")

    return build_daily_schedule_actual_df(
        actual_hours_by_date,
        assigned_hours_by_date,
        start_date=start_date,
        end_date=end_date,
    )


def print_df(df: pandas.DataFrame, *, output: Path | None, output_format: OutputFormat) -> None:
    if output_format == OutputFormat.JSON:
        print_json(df.to_dict("records"), is_pretty=True, output=output)
    else:
        print_csv(df, output=output)

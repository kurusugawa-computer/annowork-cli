import datetime
import json
from unittest.mock import MagicMock

import pandas
import pytest
from annoworkapi.api import AnnoworkApi
from annoworkapi.resource import Resource

from annoworkcli.__main__ import create_parser
from annoworkcli.actual_working_time.list_actual_working_time_weekly import get_weekly_actual_working_hours_df, main

WORKSPACE_MEMBERS = [
    {"workspace_member_id": "alice", "user_id": "alice", "username": "ALICE"},
    {"workspace_member_id": "bob", "user_id": "bob", "username": "BOB"},
]


def make_actual(start: str, end: str, member_index: int = 0, job_id: str = "job1"):
    return {
        **WORKSPACE_MEMBERS[member_index],
        "job_id": job_id,
        "job_name": job_id.upper(),
        "start_datetime": datetime.datetime.fromisoformat(start).astimezone(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "end_datetime": datetime.datetime.fromisoformat(end).astimezone(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "note": "",
    }


def test_get_weekly_actual_working_hours_df():
    actual = get_weekly_actual_working_hours_df(
        [
            make_actual("2022-03-05T10:00:00+09:00", "2022-03-05T11:00:00+09:00"),
            make_actual("2022-03-06T10:00:00+09:00", "2022-03-06T12:00:00+09:00"),
            make_actual("2022-03-12T10:00:00+09:00", "2022-03-12T13:00:00+09:00"),
            make_actual("2022-02-06T10:00:00+09:00", "2022-02-06T14:00:00+09:00", 1, "job2"),
            make_actual("2022-03-13T10:00:00+09:00", "2022-03-13T10:00:00+09:00", 1, "job2"),
        ],
        WORKSPACE_MEMBERS,
        timezone_offset_hours=9,
    )
    assert list(actual.columns) == [
        "workspace_member_id",
        "user_id",
        "username",
        "job_id",
        "job_name",
        "start_date",
        "end_date",
        "actual_working_hours",
    ]
    assert actual[["user_id", "job_id", "start_date", "end_date", "actual_working_hours"]].to_dict("records") == [
        {"user_id": "alice", "job_id": "job1", "start_date": "2022-02-27", "end_date": "2022-03-05", "actual_working_hours": 1.0},
        {"user_id": "alice", "job_id": "job1", "start_date": "2022-03-06", "end_date": "2022-03-12", "actual_working_hours": 5.0},
        {"user_id": "bob", "job_id": "job2", "start_date": "2022-02-06", "end_date": "2022-02-12", "actual_working_hours": 4.0},
    ]


@pytest.mark.parametrize(
    ("start", "end", "offset", "expected"),
    [
        ("2026-10-17T15:00:00Z", "2026-10-17T16:00:00Z", 9, [("2026-10-18", 1.0)]),
        ("2026-10-18T00:00:00Z", "2026-10-18T01:00:00Z", -5, [("2026-10-11", 1.0)]),
        ("2026-10-17T14:00:00Z", "2026-10-17T16:00:00Z", 9, [("2026-10-11", 1.0), ("2026-10-18", 1.0)]),
        ("2026-10-17T14:00:00Z", "2026-10-17T15:00:00Z", 9, [("2026-10-11", 1.0)]),
        ("2026-10-17T18:00:00Z", "2026-10-17T19:00:00Z", 5.5, [("2026-10-11", 0.5), ("2026-10-18", 0.5)]),
    ],
)
def test_指定タイムゾーンの週境界で作業時間を分割する(start, end, offset, expected):
    actual = get_weekly_actual_working_hours_df([make_actual(start, end)], WORKSPACE_MEMBERS, timezone_offset_hours=offset)
    assert list(zip(actual["start_date"], actual["actual_working_hours"], strict=True)) == expected


def test_タイムゾーン未指定時はローカルの週境界を使う():
    local = datetime.datetime(2026, 10, 18).astimezone()
    end = local + datetime.timedelta(hours=1)
    actual = get_weekly_actual_working_hours_df(
        [make_actual(local.astimezone(datetime.UTC).isoformat(), end.astimezone(datetime.UTC).isoformat())], WORKSPACE_MEMBERS
    )
    assert actual["start_date"].tolist() == ["2026-10-18"]
    assert actual["actual_working_hours"].tolist() == [1.0]


@pytest.mark.parametrize(
    ("start_date", "end_date", "expected"),
    [
        ("2026-10-18", None, [("2026-10-18", 1.0)]),
        (None, "2026-10-17", [("2026-10-11", 1.0)]),
        ("2026-10-17", "2026-10-18", [("2026-10-11", 1.0), ("2026-10-18", 1.0)]),
        ("2026-10-19", "2026-10-20", []),
    ],
)
def test_期間外の日付の作業時間を除外する(start_date, end_date, expected):
    actual = get_weekly_actual_working_hours_df(
        [make_actual("2026-10-17T14:00:00Z", "2026-10-17T16:00:00Z")],
        WORKSPACE_MEMBERS,
        timezone_offset_hours=9,
        start_date=start_date,
        end_date=end_date,
    )
    assert list(zip(actual["start_date"], actual["actual_working_hours"], strict=True)) == expected


@pytest.mark.parametrize("actuals", [[], [make_actual("2026-10-17T15:00:00Z", "2026-10-17T15:00:00Z")]])
def test_実績がない場合も出力列を返す(actuals):
    actual = get_weekly_actual_working_hours_df(actuals, WORKSPACE_MEMBERS, timezone_offset_hours=9)
    assert actual.empty
    assert "actual_working_hours" in actual.columns
    assert "start_date" in actual.columns


@pytest.mark.parametrize("output_format", ["csv", "json"])
@pytest.mark.parametrize("has_actual", [True, False])
def test_CLIで指定したタイムゾーンと期間を出力に反映する(monkeypatch, tmp_path, output_format, has_actual):
    service = MagicMock(spec=Resource)
    service.api = MagicMock(spec=AnnoworkApi)
    service.api.get_workspace_members.return_value = WORKSPACE_MEMBERS
    service.api.get_jobs.return_value = [
        {"job_id": "parent", "job_name": "PARENT", "job_tree": "ws/parent"},
        {"job_id": "job1", "job_name": "JOB1", "job_tree": "ws/parent/job1"},
    ]
    service.api.get_actual_working_times.return_value = [make_actual("2026-10-17T14:00:00Z", "2026-10-17T16:00:00Z")] if has_actual else []
    monkeypatch.setattr("annoworkcli.actual_working_time.list_actual_working_time_weekly.build_annoworkapi", lambda _args: service)
    output = tmp_path / f"weekly.{output_format}"
    args = create_parser().parse_args(
        [
            "actual_working_time",
            "list_weekly",
            "--workspace_id",
            "ws",
            "--start_date",
            "2026-10-18",
            "--end_date",
            "2026-10-18",
            "--timezone_offset",
            "9",
            "--format",
            output_format,
            "--output",
            str(output),
        ]
    )
    main(args)
    if output_format == "json":
        rows = json.loads(output.read_text())
    else:
        rows = pandas.read_csv(output).to_dict("records")
    assert len(rows) == int(has_actual)
    if has_actual:
        assert rows[0]["start_date"] == "2026-10-18"
        assert rows[0]["end_date"] == "2026-10-24"
        assert rows[0]["actual_working_hours"] == 1.0
        assert rows[0]["parent_job_id"] == "parent"

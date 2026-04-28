import configparser
import os
from pathlib import Path

import pytest

from annoworkcli.__main__ import main

pytestmark = pytest.mark.access_webapi

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

out_dir = Path("./tests/out/schedule_actual")
out_dir.mkdir(exist_ok=True, parents=True)

inifile = configparser.ConfigParser()
inifile.read("./pytest.ini", "UTF-8")
annowork_config = dict(inifile.items("annowork"))

workspace_id = annowork_config["workspace_id"]
parent_job_id = annowork_config.get("parent_job_id")

COMMAND_NAME = "schedule_actual"


def test_list_daily():
    if parent_job_id is None:
        pytest.skip("'parent_job_id' is not configured in pytest.ini")

    main(
        [
            COMMAND_NAME,
            "list_daily",
            "--workspace_id",
            workspace_id,
            "--parent_job_id",
            parent_job_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list_daily.csv"),
        ]
    )


def test_list_weekly():
    if parent_job_id is None:
        pytest.skip("'parent_job_id' is not configured in pytest.ini")

    main(
        [
            COMMAND_NAME,
            "list_weekly",
            "--workspace_id",
            workspace_id,
            "--parent_job_id",
            parent_job_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list_weekly.csv"),
        ]
    )

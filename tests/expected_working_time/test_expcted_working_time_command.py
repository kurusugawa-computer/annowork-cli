import configparser
import os
from pathlib import Path

import pytest

from annoworkcli.__main__ import main

# モジュールレベルでpytestのmarkerを付ける
pytestmark = pytest.mark.access_webapi


# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/expected_working_time")
out_dir = Path("./tests/out/expected_working_time")
out_dir.mkdir(exist_ok=True, parents=True)

inifile = configparser.ConfigParser()
inifile.read("./pytest.ini", "UTF-8")
annowork_config = dict(inifile.items("annowork"))

workspace_id = annowork_config["workspace_id"]


COMMAND_NAME = "expected_working_time"


def test_list():
    main(
        [
            COMMAND_NAME,
            "list",
            "--workspace_id",
            workspace_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list.csv"),
        ]
    )


def test_list_weekly():
    main(
        [
            COMMAND_NAME,
            "list",
            "--workspace_id",
            workspace_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list_weekly.csv"),
        ]
    )


def test_list_groupby_tag():
    main(
        [
            COMMAND_NAME,
            "list_groupby_tag",
            "--workspace_id",
            workspace_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list_groupby_tag.csv"),
        ]
    )

import configparser
import os
from pathlib import Path

import pytest

from annoworkcli.__main__ import main

# モジュールレベルでpytestのmarkerを付ける
pytestmark = pytest.mark.access_webapi


# プロジェクトトップに移動する
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../")

data_dir = Path("./tests/data/schedule")
out_dir = Path("./tests/out/schedule")
out_dir.mkdir(exist_ok=True, parents=True)

inifile = configparser.ConfigParser()
inifile.read("./pytest.ini", "UTF-8")
annowork_config = dict(inifile.items("annowork"))

organization_id = annowork_config["organization_id"]


COMMAND_NAME = "schedule"


def test_list():
    main(
        [
            COMMAND_NAME,
            "list",
            "--organization_id",
            organization_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list.csv"),
        ]
    )


def test_list_daily():
    main(
        [
            COMMAND_NAME,
            "list_daily",
            "--organization_id",
            organization_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",c
            "--output",
            str(out_dir / "list_daily.csv"),
        ]
    )


def test_list_groupby_tag():
    main(
        [
            COMMAND_NAME,
            "list_daily_groupby_tag",
            "--organization_id",
            organization_id,
            "--start_date",
            "2022-01-01",
            "--end_date",
            "2022-01-31",
            "--output",
            str(out_dir / "list_daily_groupby_tag.csv"),
        ]
    )

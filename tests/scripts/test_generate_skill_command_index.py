import argparse
import subprocess
import sys
from pathlib import Path

from annoworkcli.__main__ import create_parser
from scripts.generate_skill_command_index import OUTPUT_PATH, collect_command_groups, is_command_index_current


def test_多階層の末端コマンドと単独コマンドを収集する():
    parser = argparse.ArgumentParser()
    groups = parser.add_subparsers()
    nested = groups.add_parser("nested", help="複数階層のグループ")
    middle = nested.add_subparsers().add_parser("middle", help="中間階層")
    middle.add_subparsers().add_parser("leaf", help="末端の\n 説明")
    groups.add_parser("standalone", help="単独コマンド")

    actual = collect_command_groups(parser)

    assert [group.name for group in actual] == ["nested", "standalone"]
    assert actual[0].description == "複数階層のグループ"
    assert actual[0].commands[0].names == ("nested", "middle", "leaf")
    assert actual[0].commands[0].description == "末端の 説明"
    assert actual[1].commands[0].names == ("standalone",)


def test_実際のコマンドが重複なく収集される():
    groups = collect_command_groups(create_parser())
    names = [command.names for group in groups for command in group.commands]

    assert len(names) == len(set(names))
    assert ("completion",) in names
    assert ("job", "list") in names
    assert ("annofab", "visualize_statistics") in names


def test_索引の未生成と古い内容を検出する(tmp_path):
    output = tmp_path / "command-index.md"
    assert not is_command_index_current("最新\n", output)
    output.write_text("古い内容\n", encoding="utf-8")
    assert not is_command_index_current("最新\n", output)
    output.write_text("最新\n", encoding="utf-8")
    assert is_command_index_current("最新\n", output)


def test_生成とチェックをCLIから実行する(tmp_path):
    root = Path(__file__).parents[2]
    script = tmp_path / "scripts" / "generate_skill_command_index.py"
    script.parent.mkdir()
    script.write_bytes((root / "scripts" / script.name).read_bytes())
    invocation = [sys.executable, str(script)]
    output = tmp_path / OUTPUT_PATH.relative_to(root)

    result = subprocess.run([*invocation, "--check"], capture_output=True, check=False)
    assert result.returncode != 0
    assert not output.exists()

    subprocess.run(invocation, check=True)
    assert output.read_bytes() == OUTPUT_PATH.read_bytes()
    subprocess.run([*invocation, "--check"], check=True)

    output.write_text("古い内容\n", encoding="utf-8")
    result = subprocess.run([*invocation, "--check"], capture_output=True, check=False)
    assert result.returncode != 0
    assert output.read_text(encoding="utf-8") == "古い内容\n"

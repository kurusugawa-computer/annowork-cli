import shlex
import shutil
import subprocess
import sys

import pytest

from annoworkcli.__main__ import main
from annoworkcli.completion.subcommand_completion import SHELL_CHOICES


@pytest.mark.parametrize("shell", SHELL_CHOICES)
def test_補完スクリプトを認証とログ出力なしで生成する(shell, capsys, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    def reject_network(*_args, **_kwargs):
        raise AssertionError("補完スクリプト生成中にネットワークアクセスが発生しました。")

    monkeypatch.setattr("requests.sessions.Session.request", reject_network)
    main(["completion", shell])

    captured = capsys.readouterr()
    assert "annoworkcli" in captured.out
    assert "workspace_member" in captured.out
    assert "workspace_id" in captured.out
    assert "json" in captured.out
    assert captured.err == ""
    assert not (tmp_path / ".log").exists()


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (["annoworkcli", "work"], {"workspace", "workspace_member", "workspace_tag"}),
        (["annoworkcli", "job", ""], {"change", "delete", "list"}),
        (["annoworkcli", "job", "list", "--work"], {"--workspace_id"}),
        (["annoworkcli", "job", "list", "--format", ""], {"csv", "json"}),
        (["annoworkcli", "completion", ""], set(SHELL_CHOICES)),
    ],
)
def test_Bashでコマンドとオプションと選択肢を補完する(words, expected, capsys):
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("Bashがインストールされていません。")
    main(["completion", "bash"])
    script = capsys.readouterr().out
    script += f"\nCOMP_WORDS=({shlex.join(words)})\nCOMP_CWORD={len(words) - 1}\n"
    script += '_shtab_annoworkcli\nprintf "%s\\n" "${COMPREPLY[@]}"\n'
    result = subprocess.run([bash, "--noprofile", "--norc"], input=script, text=True, capture_output=True, check=True)
    assert set(result.stdout.splitlines()) == expected
    assert result.stderr == ""


def test_モジュール実行でもannoworkcli用のスクリプトを生成する(tmp_path):
    result = subprocess.run([sys.executable, "-m", "annoworkcli", "completion", "bash"], cwd=tmp_path, text=True, capture_output=True, check=True)
    assert "complete -F _shtab_annoworkcli annoworkcli" in result.stdout
    assert "__main__" not in result.stdout
    assert result.stderr == ""
    assert not (tmp_path / ".log").exists()

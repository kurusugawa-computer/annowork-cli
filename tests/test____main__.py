import pytest

from annoworkcli.__main__ import main, mask_sensitive_value_in_argv


def test__mask_sensitive_value_in_argv__同じ引数を指定する():
    actual = mask_sensitive_value_in_argv(
        [
            "--annofab_user_id",
            "alice",
            "--annofab_password",
            "pw_alice",
            "--annofab_user_id",
            "bob",
            "--annofab_password",
            "pw_bob",
            "--annowork_user_id",
            "chris",
            "--annowork_password",
            "pw_chris",
            "--annowork_user_id",
            "dave",
            "--annowork_password",
            "pw_dave",
            "--annofab_pat",
            "pat_eve",
        ]
    )
    assert actual == [
        "--annofab_user_id",
        "***",
        "--annofab_password",
        "***",
        "--annofab_user_id",
        "***",
        "--annofab_password",
        "***",
        "--annowork_user_id",
        "***",
        "--annowork_password",
        "***",
        "--annowork_user_id",
        "***",
        "--annowork_password",
        "***",
        "--annofab_pat",
        "***",
    ]


@pytest.mark.parametrize("unknown_arguments", [["--unknown"], ["--unknown", "value"], ["--unknown=value"]])
def test_未知の引数で対象サブコマンドのusageを表示する(unknown_arguments, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["annofab", "visualize_statistics", "-w", "workspace", "-j", "job", "-o", "out", *unknown_arguments])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "annofab visualize_statistics" in captured.err.splitlines()[0]
    assert f"annofab visualize_statistics: error: unrecognized arguments: {' '.join(unknown_arguments)}" in captured.err


@pytest.mark.parametrize("command", [[], ["annofab"], ["workspace", "list"]])
def test_未知の引数で選択された階層のusageを表示する(command, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([*command, "--unknown"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    command_path = " ".join(command)
    assert f"{command_path}: error: unrecognized arguments: --unknown" in captured.err
    assert command_path in captured.err.splitlines()[0]


def test_実行時の引数で対象サブコマンドのusageを表示する(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["annoworkcli", "workspace", "list", "--unknown"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "usage: annoworkcli workspace list" in captured.err
    assert "annoworkcli workspace list: error: unrecognized arguments: --unknown" in captured.err

from annoworkcli.__main__ import create_parser


def test_create_parser__schedule_actual_list_daily():
    parser = create_parser()

    actual = parser.parse_args(
        [
            "schedule_actual",
            "list_daily",
            "--workspace_id",
            "workspace1",
            "--parent_job_id",
            "parent1",
        ]
    )

    assert actual.command_name == "schedule_actual"
    assert actual.subcommand_name == "list_daily"
    assert actual.workspace_id == "workspace1"
    assert actual.parent_job_id == "parent1"

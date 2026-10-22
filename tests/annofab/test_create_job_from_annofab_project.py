from unittest.mock import MagicMock

import pytest
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.resource import Resource

from annoworkcli.annofab.create_job_from_annofab_project import CreateJobFromAnnofabProject


@pytest.mark.parametrize("existing", [True, False])
def test_既存ジョブは変更せず新規ジョブだけを作成する(existing):
    service = MagicMock(spec=Resource)
    service.wrapper = MagicMock()
    service.api = MagicMock()
    service.wrapper.get_job_or_none.return_value = {"job_id": "project"} if existing else None
    annofab = MagicMock(spec=AnnofabResource)
    annofab.wrapper = MagicMock()
    annofab.wrapper.get_project_or_none.return_value = {"title": "プロジェクト"}
    command = CreateJobFromAnnofabProject(annowork_service=service, workspace_id="ws", annofab_service=annofab)
    assert command.create_job_from_annofab_project("parent", "project") is not existing
    if existing:
        service.api.put_job.assert_not_called()
    else:
        service.api.put_job.assert_called_once_with(
            "ws",
            "project",
            request_body={
                "job_name": "プロジェクト",
                "status": "unarchived",
                "parent_job_id": "parent",
                "external_linkage_info": {"url": "https://annofab.com/projects/project"},
            },
        )

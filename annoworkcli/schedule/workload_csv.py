import logging
from collections import defaultdict
from collections.abc import Iterable

logger = logging.getLogger(__name__)


def get_parent_job_columns(jobs: Iterable[tuple[str, str | None]], fixed_columns: list[str]) -> dict[str, str]:
    """親ジョブID順のCSV列名を返し、同名の親ジョブがあれば警告する。"""
    columns: dict[str, str] = {}
    ids_by_name: dict[str, list[str]] = defaultdict(list)
    for job_id, name in sorted(dict(jobs).items()):
        if not name or name in fixed_columns:
            raise ValueError(
                f"親ジョブ名が未取得・空、またはCSVの固定列名と衝突しています。 :: {job_id=}, {name=}。--format json で出力してください。"
            )
        ids_by_name[name].append(job_id)
        columns[job_id] = name
    for name, job_ids in ids_by_name.items():
        if len(job_ids) > 1:
            logger.warning(f"出力する親ジョブ名が重複しています。同名の列を親ジョブID順に分けて出力します。 :: {name=}, {job_ids=}")
    return columns

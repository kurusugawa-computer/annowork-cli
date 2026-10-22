from collections.abc import Iterable


def get_parent_job_columns(jobs: Iterable[tuple[str, str | None]], fixed_columns: list[str]) -> dict[str, str]:
    """親ジョブID順のCSV列名を返し、欠損・空・重複した列名は拒否する。"""
    columns: dict[str, str] = {}
    names = set(fixed_columns)
    for job_id, name in sorted(dict(jobs).items()):
        if not name or name in names:
            raise ValueError(f"親ジョブ名が未取得・空、またはCSV列名が重複しています。 :: {job_id=}, {name=}。--format json で出力してください。")
        names.add(name)
        columns[job_id] = name
    return columns

"""Stale-reference scanner for the project registry."""

from dataclasses import dataclass
from pathlib import Path

from architekta.infrastructure import GitError, is_text_file, list_tracked_files
from architekta.registry.schema import ProjectRegistry


@dataclass(frozen=True)
class StaleReference:
    """A single occurrence of a stale alias found in a tracked file."""

    file: Path
    line_number: int
    line: str
    alias: str
    canonical_name: str


def find_stale_references(registry: ProjectRegistry) -> list[StaleReference]:
    """Scan all tracked files in all registered projects for stale aliases.

    Returns every line that contains a known alias of any project. The caller
    may use these results to verify that a completed rename left no residue, or
    as a periodic hygiene check.
    """
    alias_map = {
        alias: canonical
        for canonical, record in registry.projects.items()
        for alias in record.aliases
    }
    if not alias_map:
        return []

    results: list[StaleReference] = []
    for name in sorted(registry.projects):
        project_path = registry.project_path(name)
        if not project_path.is_dir():
            continue
        try:
            tracked = list_tracked_files(project_path)
        except GitError:
            continue
        for file_path in tracked:
            if not is_text_file(file_path):
                continue
            _scan_file(file_path, alias_map, results)

    return results


def _scan_file(
    file_path: Path,
    alias_map: dict[str, str],
    results: list[StaleReference],
) -> None:
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return
    for line_number, line in enumerate(content.splitlines(), start=1):
        for alias, canonical in alias_map.items():
            if alias in line:
                results.append(
                    StaleReference(
                        file=file_path,
                        line_number=line_number,
                        line=line.rstrip(),
                        alias=alias,
                        canonical_name=canonical,
                    )
                )
                break  # One StaleReference per line is sufficient

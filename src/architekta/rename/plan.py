"""Domain models for the rename pipeline: context, reports, and dry-run rendering."""

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from architekta.registry.schema import DependencyEdge, GithubSlug, ProjectRegistry
from architekta.rename.patterns import PatternPair, generate_patterns


# ── Immutable change records ────────────────────────────────────────────────────


@dataclass(frozen=True)
class FileEdit:
    """A single changed line produced by a pattern replacement."""

    path: Path
    line_number: int
    old_line: str
    new_line: str


@dataclass(frozen=True)
class PathRename:
    """A filesystem path rename (directory or file)."""

    old: Path
    new: Path


@dataclass(frozen=True)
class ShellCommand:
    """A subprocess command run (or planned) by a pipeline stage.

    When ``checked`` is True the executor raises on non-zero exit; when False
    the command is run best-effort (e.g. ``git commit`` which exits non-zero
    when there is nothing to commit).
    """

    description: str
    args: tuple[str, ...]
    cwd: Path | None = None
    checked: bool = True


@dataclass(frozen=True)
class PendingWrite:
    """Full file content to write during the execution phase."""

    path: Path
    content: str


# ExecutionStep is the union of all actions the executor can apply.
ExecutionStep = Union[PendingWrite, PathRename, ShellCommand]


# ── Stage and pipeline reports ──────────────────────────────────────────────────


@dataclass(frozen=True)
class StageReport:
    """Output of one pipeline stage (actual or planned in dry-run mode)."""

    stage_id: int
    name: str
    path_renames: tuple[PathRename, ...] = ()
    file_edits: tuple[FileEdit, ...] = ()
    commands: tuple[ShellCommand, ...] = ()
    skipped: bool = False
    skip_reason: str = ""
    error: str | None = None
    description: str = ""

    @property
    def succeeded(self) -> bool:
        return self.error is None

    @property
    def modified_files(self) -> frozenset[Path]:
        renamed_new = frozenset(r.new for r in self.path_renames)
        edited = frozenset(e.path for e in self.file_edits)
        return renamed_new | edited


@dataclass(frozen=True)
class StagePlan:
    """Planner output: a public StageReport plus an ordered execution sequence.

    ``report`` is the display model (used for dry-run output and logging).
    ``steps`` is the ordered list of I/O actions to apply during execution.
    The two are kept separate so that planning is always side-effect-free and
    execution is driven entirely from the ``steps`` sequence without re-reading
    any files.
    """

    report: StageReport
    steps: tuple[ExecutionStep, ...]


@dataclass(frozen=True)
class PipelineReport:
    """Aggregate result of a complete rename pipeline run."""

    old_name: str
    new_name: str
    dry_run: bool
    stages: tuple[StageReport, ...]

    @property
    def succeeded(self) -> bool:
        return all(s.succeeded for s in self.stages)

    @property
    def all_modified_files(self) -> frozenset[Path]:
        return frozenset(
            path for stage in self.stages for path in stage.modified_files
        )

    def find_stage(self, name: str) -> StageReport | None:
        """Return the StageReport for the given stage name, or None."""
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None


# ── Rename context ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AffectedProject:
    """A project with a dependency edge to or from the renamed project."""

    name: str
    path: Path


@dataclass(frozen=True)
class SubmoduleRef:
    """A git-submodule edge involving the renamed project."""

    host_name: str
    host_path: Path
    old_submodule_url: str
    new_submodule_url: str


@dataclass(frozen=True)
class RenameContext:
    """All computed state required by rename pipeline stages.

    Built once from the registry before any stage runs. Frozen so that stages
    cannot mutate shared state. Because planning and execution are separated,
    this context always reflects the pre-rename state; stages derive execution
    paths (e.g. ``new_project_path``) from the stored fields.
    """

    old_name: str
    new_name: str
    owner: str
    old_project_path: Path
    new_project_path: Path
    old_github: GithubSlug
    new_github: GithubSlug
    old_conda_env: str | None
    new_conda_env: str | None
    old_workspace: str | None
    new_workspace: str | None
    patterns: tuple[PatternPair, ...]
    affected_projects: tuple[AffectedProject, ...]
    submodule_refs: tuple[SubmoduleRef, ...]
    registry_path: Path
    registry_root: Path
    skip_stages: frozenset[str]
    push: bool


def build_rename_context(
    old_name: str,
    new_name: str,
    registry: ProjectRegistry,
    skip_stages: frozenset[str],
    *,
    push: bool = False,
) -> RenameContext:
    """Extract all rename-relevant data from the registry into a frozen context."""
    old_record = registry.get_project(old_name)
    owner = old_record.github.owner

    new_relative_path = old_record.path.parent / new_name
    old_project_path = registry.root / old_record.path
    new_project_path = registry.root / new_relative_path

    new_conda_env = (
        old_record.conda_env.replace(old_name, new_name)
        if old_record.conda_env
        else None
    )
    new_workspace = (
        old_record.workspace.replace(old_name, new_name)
        if old_record.workspace
        else None
    )

    patterns = generate_patterns(
        old_name=old_name,
        new_name=new_name,
        old_aliases=list(old_record.aliases),
        old_abs_path=str(old_project_path),
        new_abs_path=str(new_project_path),
        old_conda_env=old_record.conda_env,
        new_conda_env=new_conda_env,
    )

    affected_names = registry.affected_projects(old_name)
    affected_projects = tuple(
        AffectedProject(name=n, path=registry.project_path(n))
        for n in sorted(affected_names)
        if registry.has_project(n)
    )

    submodule_refs = tuple(
        SubmoduleRef(
            host_name=edge.dependent,
            host_path=registry.project_path(edge.dependent),
            old_submodule_url=f"git@github.com:{old_record.github}.git",
            new_submodule_url=f"git@github.com:{owner}/{new_name}.git",
        )
        for edge in registry.edges_involving(old_name)
        if edge.mechanism == "git-submodule" and edge.dependency == old_name
    )

    return RenameContext(
        old_name=old_name,
        new_name=new_name,
        owner=owner,
        old_project_path=old_project_path,
        new_project_path=new_project_path,
        old_github=old_record.github,
        new_github=GithubSlug(owner=owner, repo=new_name),
        old_conda_env=old_record.conda_env,
        new_conda_env=new_conda_env,
        old_workspace=old_record.workspace,
        new_workspace=new_workspace,
        patterns=patterns,
        affected_projects=affected_projects,
        submodule_refs=submodule_refs,
        registry_path=registry.source,
        registry_root=registry.root,
        skip_stages=skip_stages,
        push=push,
    )


# ── Dry-run rendering ───────────────────────────────────────────────────────────


def render_dry_run(report: PipelineReport) -> str:
    """Format a pipeline report as a human-readable dry-run preview."""
    lines: list[str] = [
        f"Rename: {report.old_name} → {report.new_name}",
        "",
    ]
    for stage in report.stages:
        if stage.skipped:
            lines.append(f"[{stage.name}] skipped: {stage.skip_reason}")
            continue
        if stage.error:
            lines.append(f"[{stage.name}] ERROR: {stage.error}")
            continue

        section_lines: list[str] = []
        for rename in stage.path_renames:
            section_lines.append(f"  mv  {rename.old} → {rename.new}")
        if stage.file_edits:
            files_changed = len({e.path for e in stage.file_edits})
            section_lines.append(
                f"  {len(stage.file_edits)} occurrence(s) in {files_changed} file(s):"
            )
            for edit in stage.file_edits:
                section_lines.append(
                    f"    {edit.path}:{edit.line_number}  "
                    f"{edit.old_line!r} → {edit.new_line!r}"
                )
        for cmd in stage.commands:
            section_lines.append(f"  {cmd.description}: {' '.join(str(a) for a in cmd.args)}")
        if stage.description:
            section_lines.append(f"  {stage.description}")

        if section_lines:
            lines.append(f"[{stage.name}]")
            lines.extend(section_lines)
        else:
            lines.append(f"[{stage.name}] no changes")

    return "\n".join(lines) + "\n"

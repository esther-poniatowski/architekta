"""Domain models for the rename pipeline: value objects, reports, and type aliases."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Union

from architekta.infrastructure import CommandResult, GithubSlug, run_command
from architekta.rename.patterns import PatternPair


# ── Stage name constants ──────────────────────────────────────────────────────

STAGE_VALIDATE = "validate"
STAGE_FILESYSTEM = "filesystem"
STAGE_GIT_REMOTE = "git-remote"
STAGE_WORKSPACES = "workspaces"
STAGE_CONDA = "conda"
STAGE_SELF_REFS = "self-refs"
STAGE_CROSS_REFS = "cross-refs"
STAGE_SUBMODULES = "submodules"
STAGE_COMMIT = "commit"


# ── Surfaces ──────────────────────────────────────────────────────────────────


class Surface(str, Enum):
    """A location where a project's name is encoded.

    The rename pipeline must update every surface where the old name appears.
    Surfaces are an enumerated classification: each stage targets one or more
    surfaces, and the union of all covered surfaces defines the pipeline's
    completeness guarantee.
    """

    FILESYSTEM = "filesystem"
    GITHUB = "github"
    VSCODE_WORKSPACE = "vscode"
    CONDA = "conda"
    SELF_REFERENCES = "self-refs"
    CROSS_REFERENCES = "cross-refs"
    SUBMODULES = "submodules"
    GIT = "git"


# ── Project identity ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProjectIdentity:
    """The identifying attributes of a project across all surfaces.

    This is the central domain entity of the rename pipeline. It captures
    everything about a project that may be encoded in another location and
    therefore must be updated during a rename. It exists in two instances
    within a ``RenameContext``: one for the pre-rename state (``old``) and
    one for the post-rename state (``new``).
    """

    name: str
    path: Path
    github: GithubSlug
    conda_env: str | None = None
    workspace: str | None = None


# ── Immutable change records ──────────────────────────────────────────────────


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

    def execute(self) -> None:
        """Apply the rename to the filesystem."""
        self.old.rename(self.new)


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

    def execute(self) -> CommandResult:
        """Run the command and return the result.

        Raises
        ------
        RuntimeError
            If the command is ``checked`` and exits with a non-zero code.
        """
        result = run_command(list(self.args), cwd=self.cwd)
        if self.checked and not result.ok:
            detail = result.stderr or result.stdout or "command failed"
            raise RuntimeError(
                f"Stage command failed: {self.description}\n"
                f"  args: {self.args}\n"
                f"  exit: {result.returncode}\n"
                f"  detail: {detail}"
            )
        return result


@dataclass(frozen=True)
class PendingWrite:
    """Full file content to write during the execution phase."""

    path: Path
    content: str

    def execute(self) -> None:
        """Write the content to the target path."""
        self.path.write_text(self.content, encoding="utf-8")


# ExecutionStep is the union of all actions the executor can apply.
ExecutionStep = Union[PendingWrite, PathRename, ShellCommand]


# ── Outcome and result types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class CommandOutcome:
    """Structured outcome of a shell command execution."""

    args: tuple[str, ...]
    returncode: int
    ok: bool
    error: str


@dataclass(frozen=True)
class FileProcessingResult:
    """Result of reading a file, applying patterns, and preparing a write."""

    edits: list[FileEdit]
    pending_write: PendingWrite | None
    error: str | None


# ── Stage and pipeline reports ────────────────────────────────────────────────


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
    warnings: list[str] = field(default_factory=list)

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


# ── Cross-project references ──────────────────────────────────────────────────


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

"""Rename context: immutable state assembled before pipeline execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from architekta.infrastructure import GithubSlug
from architekta.rename.models import AffectedProject, ProjectIdentity, SubmoduleRef
from architekta.rename.patterns import PatternPair, generate_patterns


@dataclass(frozen=True)
class RenameContext:
    """All computed state required by rename pipeline stages.

    Built once before any stage runs.  Frozen so that stages cannot mutate
    shared state.  Because planning and execution are separated, this context
    always reflects the pre-rename state; stages derive execution paths
    (e.g. ``new.path``) from the stored fields.

    The project's identity is captured by two :class:`ProjectIdentity`
    instances — ``old`` (pre-rename) and ``new`` (post-rename) — separating
    the domain concept "what the project is" from the pipeline configuration
    "how to rename it".
    """

    old: ProjectIdentity
    new: ProjectIdentity
    patterns: tuple[PatternPair, ...]
    affected_projects: tuple[AffectedProject, ...]
    submodule_refs: tuple[SubmoduleRef, ...]
    workspace_root: Path
    skip_stages: frozenset[str]
    push: bool

    # ── Backward-compatible aliases ──────────────────────────────────────────
    # These properties preserve the previous flat field access used by
    # existing callers. New code should prefer ``ctx.old.name`` etc.

    @property
    def old_name(self) -> str:
        return self.old.name

    @property
    def new_name(self) -> str:
        return self.new.name

    @property
    def old_project_path(self) -> Path:
        return self.old.path

    @property
    def new_project_path(self) -> Path:
        return self.new.path

    @property
    def old_github(self) -> GithubSlug:
        return self.old.github

    @property
    def new_github(self) -> GithubSlug:
        return self.new.github

    @property
    def old_conda_env(self) -> str | None:
        return self.old.conda_env

    @property
    def new_conda_env(self) -> str | None:
        return self.new.conda_env

    @property
    def old_workspace(self) -> str | None:
        return self.old.workspace

    @property
    def new_workspace(self) -> str | None:
        return self.new.workspace


def build_rename_context(
    old_name: str,
    new_name: str,
    project_path: Path,
    *,
    affected_paths: tuple[Path, ...] = (),
    aliases: tuple[str, ...] = (),
    github_slug: GithubSlug | None = None,
    conda_env: str | None = None,
    workspace: str | None = None,
    skip_stages: frozenset[str] = frozenset(),
    push: bool = False,
) -> RenameContext:
    """Build a frozen rename context from explicit parameters.

    Parameters
    ----------
    project_path:
        Absolute path to the project directory being renamed.
    affected_paths:
        Paths to other projects whose files should be scanned for
        cross-references (e.g. sibling projects that depend on this one).
    aliases:
        Former project names that should also be replaced during renaming.
    github_slug:
        Pre-resolved GitHub owner/repo slug.  When ``None`` the GitHub-related
        stages will operate without slug information (the caller is responsible
        for resolving it via ``parse_github_remote`` at the CLI layer).
    conda_env:
        Current conda environment name, if distinct from the project name.
    workspace:
        VS Code workspace filename (e.g. ``"myproject.code-workspace"``).
    """
    old_project_path = project_path.resolve()
    new_project_path = old_project_path.parent / new_name

    if github_slug is None:
        raise ValueError(
            "Cannot determine GitHub identity. "
            "Pass --github-owner explicitly or ensure the git remote is set."
        )

    github_owner = github_slug.owner
    old_github = GithubSlug(owner=github_owner, repo=old_name)
    new_github = GithubSlug(owner=github_owner, repo=new_name)

    new_conda_env = (
        conda_env.replace(old_name, new_name)
        if conda_env
        else None
    )
    new_workspace = (
        workspace.replace(old_name, new_name)
        if workspace
        else None
    )

    old_identity = ProjectIdentity(
        name=old_name,
        path=old_project_path,
        github=old_github,
        conda_env=conda_env,
        workspace=workspace,
    )
    new_identity = ProjectIdentity(
        name=new_name,
        path=new_project_path,
        github=new_github,
        conda_env=new_conda_env,
        workspace=new_workspace,
    )

    patterns = generate_patterns(
        old_name=old_name,
        new_name=new_name,
        old_aliases=list(aliases),
        old_abs_path=str(old_project_path),
        new_abs_path=str(new_project_path),
        old_conda_env=conda_env,
        new_conda_env=new_conda_env,
    )

    affected_projects = tuple(
        AffectedProject(name=p.name, path=p.resolve())
        for p in sorted(affected_paths)
    )

    submodule_refs = _detect_submodule_refs(
        affected_paths, old_name, old_github, new_github,
    )

    return RenameContext(
        old=old_identity,
        new=new_identity,
        patterns=patterns,
        affected_projects=affected_projects,
        submodule_refs=submodule_refs,
        workspace_root=old_project_path.parent,
        skip_stages=skip_stages,
        push=push,
    )


def _detect_submodule_refs(
    affected_paths: tuple[Path, ...],
    old_name: str,
    old_github: GithubSlug,
    new_github: GithubSlug,
) -> tuple[SubmoduleRef, ...]:
    """Scan affected projects for ``.gitmodules`` referencing the old name."""
    refs: list[SubmoduleRef] = []
    for path in affected_paths:
        gitmodules = path / ".gitmodules"
        if not gitmodules.exists():
            continue
        try:
            content = gitmodules.read_text(encoding="utf-8")
        except OSError:
            continue
        if old_name in content:
            refs.append(SubmoduleRef(
                host_name=path.name,
                host_path=path.resolve(),
                old_submodule_url=old_github.ssh_url,
                new_submodule_url=new_github.ssh_url,
            ))
    return tuple(refs)

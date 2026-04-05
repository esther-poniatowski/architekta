"""Rename pipeline orchestration: stage registration, planning, and execution."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from architekta.infrastructure import GithubSlug
from architekta.rename.context import RenameContext, build_rename_context
from architekta.rename.models import (
    CommandOutcome,
    PipelineReport,
    StagePlan,
    StageReport,
    Surface,
    STAGE_COMMIT,
    STAGE_CONDA,
    STAGE_CROSS_REFS,
    STAGE_FILESYSTEM,
    STAGE_GIT_REMOTE,
    STAGE_SELF_REFS,
    STAGE_SUBMODULES,
    STAGE_VALIDATE,
    STAGE_WORKSPACES,
)
from architekta.rename.stages import (
    execute_stage_plan,
    plan_commit,
    plan_conda,
    plan_cross_refs,
    plan_filesystem,
    plan_git_remote,
    plan_self_refs,
    plan_submodules,
    plan_validate,
    plan_workspaces,
)


class RenameError(Exception):
    """Raised when the rename pipeline cannot proceed."""


# ── Stage registry ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StageDescriptor:
    """Metadata and planning function for one pipeline stage."""

    stage_id: int
    name: str
    skippable: bool
    fn: Callable[[RenameContext, PipelineReport], StagePlan]
    depends_on: tuple[str, ...] = ()
    surfaces: tuple[Surface, ...] = ()


_ALL_STAGE_NAMES = (
    STAGE_VALIDATE,
    STAGE_FILESYSTEM,
    STAGE_GIT_REMOTE,
    STAGE_WORKSPACES,
    STAGE_CONDA,
    STAGE_SELF_REFS,
    STAGE_CROSS_REFS,
    STAGE_SUBMODULES,
    STAGE_COMMIT,
)

_STAGES: tuple[StageDescriptor, ...] = (
    StageDescriptor(
        1, STAGE_VALIDATE, False, plan_validate,
        depends_on=(),
        surfaces=(Surface.FILESYSTEM,),
    ),
    StageDescriptor(
        2, STAGE_FILESYSTEM, False, plan_filesystem,
        depends_on=(STAGE_VALIDATE,),
        surfaces=(Surface.FILESYSTEM,),
    ),
    StageDescriptor(
        3, STAGE_GIT_REMOTE, False, plan_git_remote,
        depends_on=(STAGE_FILESYSTEM,),
        surfaces=(Surface.GITHUB, Surface.GIT),
    ),
    StageDescriptor(
        4, STAGE_WORKSPACES, False, plan_workspaces,
        depends_on=(STAGE_FILESYSTEM,),
        surfaces=(Surface.VSCODE_WORKSPACE,),
    ),
    StageDescriptor(
        5, STAGE_CONDA, True, plan_conda,
        depends_on=(STAGE_VALIDATE,),
        surfaces=(Surface.CONDA,),
    ),
    StageDescriptor(
        6, STAGE_SELF_REFS, False, plan_self_refs,
        depends_on=(STAGE_VALIDATE,),
        surfaces=(Surface.SELF_REFERENCES,),
    ),
    StageDescriptor(
        7, STAGE_CROSS_REFS, False, plan_cross_refs,
        depends_on=(STAGE_VALIDATE,),
        surfaces=(Surface.CROSS_REFERENCES,),
    ),
    StageDescriptor(
        8, STAGE_SUBMODULES, False, plan_submodules,
        depends_on=(STAGE_CROSS_REFS,),
        surfaces=(Surface.SUBMODULES,),
    ),
    StageDescriptor(
        9, STAGE_COMMIT, True, plan_commit,
        depends_on=_ALL_STAGE_NAMES[:-1],  # depends on all others
        surfaces=(Surface.GIT,),
    ),
)


def _validate_stage_order() -> None:
    """Check that each stage appears after all its declared dependencies.

    Raises
    ------
    RuntimeError
        If any dependency ordering constraint is violated.
    """
    name_to_index = {desc.name: i for i, desc in enumerate(_STAGES)}
    for i, desc in enumerate(_STAGES):
        for dep in desc.depends_on:
            dep_index = name_to_index.get(dep)
            if dep_index is None:
                raise RuntimeError(
                    f"Stage {desc.name!r} depends on unknown stage {dep!r}"
                )
            if dep_index >= i:
                raise RuntimeError(
                    f"Stage {desc.name!r} (index {i}) depends on {dep!r} "
                    f"(index {dep_index}), but {dep!r} has not run yet"
                )


_validate_stage_order()


# ── Pipeline entry point ──────────────────────────────────────────────────────


def run_rename_pipeline(
    old_name: str,
    new_name: str,
    *,
    project_path: Path,
    affected_paths: tuple[Path, ...] = (),
    aliases: tuple[str, ...] = (),
    github_slug: GithubSlug | None = None,
    conda_env: str | None = None,
    workspace: str | None = None,
    dry_run: bool = False,
    push: bool = False,
    skip_stages: set[str] | None = None,
    no_commit: bool = False,
    verbose: bool = False,
) -> PipelineReport:
    """Execute the full cross-surface project rename pipeline.

    Parameters
    ----------
    old_name, new_name:
        Current and target project names.
    project_path:
        Path to the project directory being renamed.
    affected_paths:
        Paths to other projects whose files should be scanned for
        cross-references to the old name.
    aliases:
        Former project names that should also be replaced.
    github_slug:
        Pre-resolved GitHub owner/repo slug.  If ``None``, the context builder
        will raise an error.  Resolve at the CLI layer via
        ``parse_github_remote``.
    conda_env:
        Current conda environment name, if distinct from the project name.
    workspace:
        VS Code workspace filename (e.g. ``"myproject.code-workspace"``).
    dry_run:
        If True, plan all stages but apply none.
    push:
        If True, push commits in all affected repositories after commit stage.
    skip_stages:
        Set of stage names to skip (must be skippable stages, e.g.
        ``{"conda", "commit"}``).
    no_commit:
        Convenience shorthand that adds ``"commit"`` to skip_stages.
    verbose:
        Passed through to the caller for display; does not affect execution.

    Returns
    -------
    PipelineReport
        Aggregate result of all stages. Check ``report.succeeded`` to
        determine whether any stage failed.

    Raises
    ------
    RenameError
        If project parameters are invalid or Stage 1 (Validate) reports
        errors.
    """
    skip: frozenset[str] = frozenset(skip_stages or set())
    if no_commit:
        skip = skip | {STAGE_COMMIT}

    try:
        ctx = build_rename_context(
            old_name,
            new_name,
            project_path,
            affected_paths=affected_paths,
            aliases=aliases,
            github_slug=github_slug,
            conda_env=conda_env,
            workspace=workspace,
            skip_stages=skip,
            push=push,
        )
    except (ValueError, OSError) as exc:
        raise RenameError(str(exc)) from exc

    # ── Phase 1: Plan all stages (pure reads, no writes) ─────────────────────
    stage_reports: list[StageReport] = []
    stage_plans: list[StagePlan] = []

    for descriptor in _STAGES:
        # Centralised skip gate for user-requested skips.
        if descriptor.skippable and descriptor.name in ctx.skip_stages:
            skipped = StageReport(
                stage_id=descriptor.stage_id,
                name=descriptor.name,
                skipped=True,
                skip_reason="skipped by user",
            )
            stage_reports.append(skipped)
            stage_plans.append(StagePlan(report=skipped, steps=()))
            continue

        accumulated = PipelineReport(
            old_name=old_name,
            new_name=new_name,
            dry_run=dry_run,
            stages=tuple(stage_reports),
        )
        plan = descriptor.fn(ctx, accumulated)
        stage_reports.append(plan.report)
        stage_plans.append(plan)

        # Abort planning after validate failure: later planners assume a
        # valid filesystem state (e.g. old_project_path exists).
        if descriptor.name == STAGE_VALIDATE and plan.report.error:
            return PipelineReport(
                old_name=old_name,
                new_name=new_name,
                dry_run=dry_run,
                stages=tuple(stage_reports),
            )

    # ── Phase 2: Execute (only when not dry_run) ─────────────────────────────
    if not dry_run:
        for plan in stage_plans:
            if not plan.report.skipped and plan.report.error is None:
                outcomes = execute_stage_plan(plan)
                # Attach warnings from failed unchecked commands.
                for outcome in outcomes:
                    if not outcome.ok:
                        plan.report.warnings.append(
                            f"Command {outcome.args} exited {outcome.returncode}: "
                            f"{outcome.error}"
                        )

    return PipelineReport(
        old_name=old_name,
        new_name=new_name,
        dry_run=dry_run,
        stages=tuple(stage_reports),
    )

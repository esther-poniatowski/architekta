"""Rename pipeline orchestration: stage registration, planning, and execution."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from architekta.registry.schema import ProjectRegistry, load_registry
from architekta.rename.plan import (
    PipelineReport,
    RenameContext,
    StagePlan,
    StageReport,
    build_rename_context,
)
from architekta.rename.stages import (
    execute_stage_plan,
    plan_commit,
    plan_conda,
    plan_cross_refs,
    plan_filesystem,
    plan_git_remote,
    plan_registry,
    plan_self_refs,
    plan_submodules,
    plan_validate,
    plan_workspaces,
)


class RenameError(Exception):
    """Raised when the rename pipeline cannot proceed."""


# ── Stage registry ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StageDescriptor:
    """Metadata and planning function for one pipeline stage."""

    stage_id: int
    name: str
    skippable: bool
    fn: Callable[[RenameContext, PipelineReport], StagePlan]


_STAGES: tuple[StageDescriptor, ...] = (
    StageDescriptor(1,  "validate",   False, plan_validate),
    StageDescriptor(2,  "filesystem", False, plan_filesystem),
    StageDescriptor(3,  "git-remote", False, plan_git_remote),
    StageDescriptor(4,  "workspaces", False, plan_workspaces),
    StageDescriptor(5,  "conda",      True,  plan_conda),
    StageDescriptor(6,  "self-refs",  False, plan_self_refs),
    StageDescriptor(7,  "cross-refs", False, plan_cross_refs),
    StageDescriptor(8,  "submodules", False, plan_submodules),
    StageDescriptor(9,  "registry",   False, plan_registry),
    StageDescriptor(10, "commit",     True,  plan_commit),
)


# ── Pipeline entry point ────────────────────────────────────────────────────────


def run_rename_pipeline(
    old_name: str,
    new_name: str,
    *,
    registry_path: Path,
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
        Canonical project names (as keys in the registry).
    registry_path:
        Path to the registry TOML file.
    dry_run:
        If True, plan all stages but apply none.
    push:
        If True, push commits in all affected repositories after Stage 10.
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
        If the registry cannot be loaded, the project names are invalid, or
        Stage 1 (Validate) reports errors.
    """
    skip: frozenset[str] = frozenset(skip_stages or set())
    if no_commit:
        skip = skip | {"commit"}

    reg = _load_registry_or_raise(registry_path)
    _check_name_preconditions(old_name, new_name, reg)

    ctx = build_rename_context(old_name, new_name, reg, skip, push=push)

    # ── Phase 1: Plan all stages (pure reads, no writes) ───────────────────────
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
        if descriptor.name == "validate" and plan.report.error:
            return PipelineReport(
                old_name=old_name,
                new_name=new_name,
                dry_run=dry_run,
                stages=tuple(stage_reports),
            )

    # ── Phase 2: Execute (only when not dry_run) ───────────────────────────────
    if not dry_run:
        for plan in stage_plans:
            if not plan.report.skipped and plan.report.error is None:
                execute_stage_plan(plan)

    return PipelineReport(
        old_name=old_name,
        new_name=new_name,
        dry_run=dry_run,
        stages=tuple(stage_reports),
    )


# ── Private helpers ─────────────────────────────────────────────────────────────


def _load_registry_or_raise(registry_path: Path) -> ProjectRegistry:
    from architekta.registry.exceptions import RegistryError

    try:
        return load_registry(registry_path)
    except RegistryError as exc:
        raise RenameError(f"Cannot load registry: {exc}") from exc


def _check_name_preconditions(
    old_name: str, new_name: str, registry: ProjectRegistry
) -> None:
    """Raise RenameError if the names are unusable before building the context."""
    if not registry.has_project(old_name):
        raise RenameError(
            f"Project {old_name!r} not found in registry. "
            f"Known projects: {', '.join(sorted(registry.projects))}"
        )

    all_names = registry.all_names_and_aliases()
    if new_name in all_names:
        raise RenameError(
            f"Name {new_name!r} already exists in registry "
            f"(canonical: {all_names[new_name]!r})"
        )

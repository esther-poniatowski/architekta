# INTERACTION AUDIT REPORT — architekta

**Date:** 2026-03-31
**Auditor posture:** Adversarial
**Scope:** Interaction boundaries only (coordination, data flows, sequencing, shared computation)

---

## 1. INTERACTION VERDICT

**Classification: partially coordinated**

The codebase exhibits clear architectural intent around coordination. The rename module demonstrates a disciplined plan/execute separation with a frozen `RenameContext` built once and consumed by all stages, and an explicit `PipelineReport` accumulator that allows later stages to observe earlier stage outputs. The github module uses a `TargetBinding` abstraction to coordinate across sync targets. However, several coordination gaps remain: GitHub owner/repo extraction is independently implemented in two modules with divergent regex patterns and error handling; the rename pipeline's stage sequencing relies on implicit positional assumptions rather than structural enforcement; the stage executor silently discards failures from unchecked commands; and `stage_id` values are independently maintained in two locations with an existing inconsistency. The interaction patterns scale linearly within each module (adding a new sync target, adding a new rename stage), but the cross-module interaction surface — particularly the duplicated GitHub remote parsing — grows with each new module that needs repository identity.

---

## 2. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimensions | Boundary | Operational Consequence |
|---|---|---|---|---|---|---|
| 1 | Duplicated GitHub remote parsing across modules | High | Result Sharing | Consistency | `github/utils.py:get_github_remote` ↔ `rename/plan.py:build_rename_context` | Independent regex patterns and error handling diverge silently; one module's fix does not propagate to the other |
| 2 | Stage ID declared independently in registry and planners | High | Consistency | — | `rename/pipeline.py:_STAGES` ↔ `rename/stages.py:plan_commit` | Stage 9 (commit) writes `stage_id=10` in its report, contradicting the registry's `stage_id=9`; downstream consumers (dry-run renderer, `find_stage`) receive an inconsistent identifier |
| 3 | Pipeline stage ordering enforced only by tuple position | Medium | Sequencing | — | `rename/pipeline.py:_STAGES` ↔ `rename/stages.py` (all planners) | Reordering the `_STAGES` tuple silently breaks stages that depend on prior filesystem state (e.g., `plan_git_remote` assumes directory already renamed) |
| 4 | Executor silently discards failures from unchecked commands | Medium | Failure Propagation | — | `rename/stages.py:execute_stage_plan` ↔ `rename/pipeline.py:run_rename_pipeline` | `git add`, `git commit`, and `conda rename` failures produce no signal; the pipeline reports success while mutations are incomplete |
| 5 | `_collect_edits_and_write` silently swallows read errors | Medium | Failure Propagation | — | `rename/stages.py:_collect_edits_and_write` ↔ `plan_self_refs` / `plan_cross_refs` | An OSError (permissions, encoding, disk fault) returns `([], None)`, indistinguishable from "file had no matches"; the stage reports success while files are silently unprocessed |
| 6 | Submodules stage reads accumulated report via stringly-typed stage lookup | Low | Sequencing | Consistency | `rename/stages.py:plan_submodules` ↔ `rename/plan.py:PipelineReport.find_stage` | `find_stage("cross-refs")` returns `None` if the stage is renamed or absent; the submodules planner silently skips Case B logic |
| 7 | GitHub URL template hardcoded in two locations | Low | Consistency | Result Sharing | `rename/plan.py:_detect_submodule_refs` ↔ `rename/stages.py:plan_git_remote` | If URL scheme changes, one site may be updated without the other |

---

## 3. DETAILED FINDINGS

## F1: Duplicated GitHub Remote Parsing Across Modules

- Severity: High
- Primary dimension: Result Sharing
- Secondary dimensions: Consistency
- Boundary: `github/utils.py:get_github_remote` ↔ `rename/plan.py:build_rename_context` via `git remote get-url origin` subprocess + regex extraction
- Component A location: `src/architekta/github/utils.py`, lines 57–67 (`get_github_remote`)
- Component B location: `src/architekta/rename/plan.py`, lines 17, 40–46 (`GithubSlug.from_url`), lines 257–266 (usage in `build_rename_context`)
- Interaction description: Both modules need to extract a GitHub owner/repo pair from a git remote URL. `github/utils.py` uses `re.search(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$", stdout)` and raises `RemoteNotFound` on failure. `rename/plan.py` uses `_GITHUB_URL_RE = re.compile(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$")` via `GithubSlug.from_url()` which returns `None` on failure. Although the regex patterns happen to be textually identical today, they are independently declared and maintained, and their failure modes differ (`RemoteNotFound` exception vs. `None` return).
- Implicit assumption: The two regex patterns will remain equivalent, and the two error handling strategies will remain compatible with their callers, despite having no shared code path.
- Violated principle: §1.1 Result Sharing — the same transformation on the same data type is performed through independent code paths.
- Operational consequence: If either regex is refined (e.g., to support GitHub Enterprise URLs with a different host), the change in one module does not propagate to the other. The github module would correctly parse the URL while the rename module would fail (or vice versa), producing inconsistent behavior for the same repository. Additionally, the error handling divergence means callers receive different failure signals for the same underlying problem.
- Growth scenario: Any new module that needs repository identity (e.g., a future CI or release module) will face the same choice: import from `github/utils.py`, import from `rename/plan.py`, or write a third implementation. Without a shared computation, the divergence surface grows with each new consumer.
- Evidence: `github/utils.py` line 64: `re.search(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$", stdout)`. `rename/plan.py` line 17: `_GITHUB_URL_RE = re.compile(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$")`. Both invoke `run_command(["git", ... "remote", "get-url", "origin"])` independently.
- Remediation: Extract the GitHub remote parsing into a single shared function in `infrastructure.py` (or a new `git.py` module) that returns a validated `GithubSlug` value object (which already exists in `rename/plan.py`). Both `github/utils.py:get_github_remote` and `rename/plan.py:build_rename_context` consume the shared function's result. The `GithubSlug` type should be promoted to a shared location since it represents a cross-cutting identity concept.
- Why this coordination mechanism is the correct level: This is a shared computation consumed by two independent modules. The regex, subprocess call, and URL parsing logic are identical and should not diverge. A shared function eliminates computation duplication and ensures a single point of maintenance for URL format changes.
- Migration priority: before adding features

## F2: Stage ID Declared Independently in Registry and Planners

- Severity: High
- Primary dimension: Consistency
- Secondary dimensions: —
- Boundary: `rename/pipeline.py:_STAGES` registry ↔ `rename/stages.py` planner functions via `stage_id` field in `StageReport`
- Component A location: `src/architekta/rename/pipeline.py`, lines 45–55 (`_STAGES` tuple declaring `StageDescriptor(9, "commit", ...)`)
- Component B location: `src/architekta/rename/stages.py`, line 379 (`stage_id=10` in `plan_commit`)
- Interaction description: The `_STAGES` registry in `pipeline.py` assigns `stage_id=9` to the commit stage descriptor. But `plan_commit` in `stages.py` independently writes `stage_id=10` into its `StageReport`. Each planner function independently hardcodes its own `stage_id` in its returned `StageReport`, duplicating the authoritative assignment in `_STAGES`. The pipeline orchestrator does not inject or enforce the stage_id — it trusts the planner to use the correct value.
- Implicit assumption: Every planner's hardcoded `stage_id` matches the corresponding `StageDescriptor.stage_id` in `_STAGES`.
- Violated principle: §4.1 Single Source of Truth — the `stage_id` fact is declared in two locations with no mechanism to detect divergence.
- Operational consequence: The commit stage already has an inconsistency: the registry says `stage_id=9` but the stage report says `stage_id=10`. Any consumer that correlates stage reports by `stage_id` (e.g., a future progress tracker or test that asserts stage ordering) will fail to match the commit stage. The `PipelineReport.find_stage` method happens to use `name` rather than `stage_id`, masking the defect for now.
- Growth scenario: Every new stage added to the pipeline requires maintaining the `stage_id` in two locations. The existing inconsistency demonstrates that this coupling already fails under normal development.
- Evidence: `pipeline.py` line 54: `StageDescriptor(9, "commit", True, plan_commit)`. `stages.py` line 379: `stage_id=10`. The value `10` was likely a remnant from a removed stage.
- Remediation: Have the pipeline orchestrator inject the `stage_id` from the `StageDescriptor` into the `StageReport`, rather than relying on each planner to self-assign it. Concretely: change the planner function signature so it does not set `stage_id`, and have `run_rename_pipeline` assign `stage_id` from the descriptor after receiving the `StagePlan`. Alternatively, pass the `StageDescriptor` to the planner so it can read its own ID from the single authoritative source.
- Why this coordination mechanism is the correct level: This is a consistency violation where the same fact (`stage_id`) is maintained in two locations. The correct mechanism is to eliminate the redundant declaration by making the orchestrator the single authority for stage identity.
- Migration priority: immediately

## F3: Pipeline Stage Ordering Enforced Only by Tuple Position

- Severity: Medium
- Primary dimension: Sequencing
- Secondary dimensions: —
- Boundary: `rename/pipeline.py:_STAGES` ↔ `rename/stages.py` (all planners) via implicit positional ordering in the tuple
- Component A location: `src/architekta/rename/pipeline.py`, lines 45–55 (`_STAGES` tuple)
- Component B location: `src/architekta/rename/stages.py`, lines 99–122 (`plan_git_remote` assumes directory already renamed at `ctx.new_project_path`), lines 199–229 (`plan_self_refs` reads from `ctx.old_project_path` before rename)
- Interaction description: Stages have load-bearing ordering dependencies documented in comments (`stages.py` lines 13–17) but enforced only by their position in the `_STAGES` tuple. `plan_git_remote` sets `cwd=ctx.new_project_path`, assuming Stage 2 (filesystem rename) has already planned the directory move. `plan_self_refs` reads files from `ctx.old_project_path`, assuming Stage 2 has NOT yet executed (only planned). `plan_submodules` reads `accumulated.find_stage("cross-refs")`, assuming Stage 7 has already planned.
- Implicit assumption: The `_STAGES` tuple will never be reordered, and the planning-then-execution separation will be preserved.
- Violated principle: §3.1 Structural Enforcement — ordering dependencies between stages are expressed through comments and tuple position, not through structural mechanisms.
- Operational consequence: Moving `plan_git_remote` before `plan_filesystem` in the `_STAGES` tuple would cause the executor to run `git remote set-url` in a directory that has not yet been renamed, failing silently or erroring. Moving `plan_submodules` before `plan_cross_refs` would cause `accumulated.find_stage("cross-refs")` to return `None`, silently skipping the submodule update logic.
- Growth scenario: As more stages are added, the number of implicit ordering constraints grows. The comment block in `stages.py` is already stale (references stage numbers that do not match the current registry). A developer adding a stage must read and understand all existing planners to determine safe insertion points.
- Evidence: `stages.py` line 115: `cwd=ctx.new_project_path` (assumes filesystem stage runs first). `stages.py` line 302: `accumulated.find_stage("cross-refs")` (assumes cross-refs stage has planned). `pipeline.py` lines 144–165: sequential loop over `_STAGES` with no ordering validation.
- Remediation: Introduce explicit dependency declarations on each `StageDescriptor` — a `depends_on: tuple[str, ...]` field naming the stages that must precede it. The pipeline orchestrator validates the topological order of `_STAGES` at import time (or at pipeline start), raising an error if a stage is positioned before one of its declared dependencies.
- Why this coordination mechanism is the correct level: This is a sequencing problem, not a scope or consistency problem. Dependency declarations are the minimal mechanism that makes ordering constraints explicit without requiring a full DAG scheduler, which would be disproportionate for a fixed 9-stage pipeline.
- Migration priority: before adding features

## F4: Executor Silently Discards Failures from Unchecked Commands

- Severity: Medium
- Primary dimension: Failure Propagation
- Secondary dimensions: —
- Boundary: `rename/stages.py:execute_stage_plan` ↔ `rename/pipeline.py:run_rename_pipeline` via `StagePlan.steps` execution and `PipelineReport.succeeded`
- Component A location: `src/architekta/rename/stages.py`, lines 389–404 (`execute_stage_plan`), specifically line 404: `run_command(list(step.args), cwd=step.cwd)` for unchecked commands
- Component B location: `src/architekta/rename/pipeline.py`, lines 178–188 (execution loop and final `PipelineReport` construction)
- Interaction description: The `ShellCommand` type has a `checked: bool` field. When `checked=False`, `execute_stage_plan` calls `run_command` and discards the `CommandResult` entirely. The `plan_commit` stage marks `git add` and `git commit` as `checked=False`. The pipeline reports success based on `StageReport.succeeded` (which checks `error is None`), but since execution failures in unchecked commands are never recorded back into the report, `succeeded` always returns `True` for these stages.
- Implicit assumption: Unchecked commands either always succeed or their failure is genuinely inconsequential.
- Violated principle: §6.1 Explicit Failure Boundary — the execution boundary does not declare how failures propagate for unchecked commands. §6.2 — a `git commit` failure manifests as "changes not committed" rather than an explicit error signal.
- Operational consequence: If `git commit` fails (e.g., due to a pre-commit hook, a lock file, or GPG signing failure), the pipeline reports success while no commit was actually created. The user sees a success message but the rename mutations are left uncommitted and unstaged across multiple repositories.
- Growth scenario: As more stages use `checked=False` for best-effort commands, the set of silently discardable failures grows.
- Evidence: `stages.py` line 404: `run_command(list(step.args), cwd=step.cwd)` — the `CommandResult` is not assigned to a variable or inspected. `stages.py` line 364: `checked=False` on `git commit`. `plan.py` line 119: `StageReport.succeeded` returns `self.error is None`.
- Remediation: Introduce a `CommandOutcome` record (success/failure/best-effort-warning) that the executor records for every command, regardless of `checked` status. Return a post-execution `StageReport` (or an augmented result) from `execute_stage_plan` that the pipeline can use to update the final `PipelineReport`. For `checked=False` commands, record failures as warnings rather than errors, so they appear in the report without aborting the pipeline.
- Why this coordination mechanism is the correct level: This is a failure propagation defect. The executor has the failure information but discards it. The correct mechanism is to preserve and propagate the information through the existing report structure, not to make all commands checked (which would change the pipeline's tolerance semantics).
- Migration priority: before adding features

## F5: `_collect_edits_and_write` Silently Swallows Read Errors

- Severity: Medium
- Primary dimension: Failure Propagation
- Secondary dimensions: —
- Boundary: `rename/stages.py:_collect_edits_and_write` ↔ `plan_self_refs` / `plan_cross_refs` / `plan_workspaces` / `plan_submodules` via `(list[FileEdit], PendingWrite | None)` return type
- Component A location: `src/architekta/rename/stages.py`, lines 418–455 (`_collect_edits_and_write`), specifically lines 431–433: bare `except OSError: return [], None`
- Component B location: `src/architekta/rename/stages.py`, lines 219–227 (`plan_self_refs` consuming the return), lines 247–255 (`plan_cross_refs` consuming the return)
- Interaction description: `_collect_edits_and_write` catches `OSError` on file read and returns `([], None)`, which is the same return value as "file had no pattern matches." Callers check `if edits:` and skip files that return empty edits, with no way to distinguish "file was unreadable" from "file had no old-name occurrences."
- Implicit assumption: All tracked files in the repository are readable.
- Violated principle: §6.2 Silent Failure Propagation — a failure manifests as "no result" rather than an explicit error signal, and the downstream stage cannot distinguish the two cases.
- Operational consequence: If a tracked file containing old-name references is unreadable (e.g., permissions issue, NFS mount failure, file locked by another process), the rename pipeline reports success while that file retains stale references.
- Growth scenario: This function is the central file-processing helper called by four of nine stages. Every new stage that uses it inherits the silent failure.
- Evidence: `stages.py` lines 431–433: `try: content = file_path.read_text(encoding="utf-8") / except OSError: return [], None`. `stages.py` line 223: `if edits:` — no check for whether the file was actually read.
- Remediation: Change `_collect_edits_and_write` to return a three-valued result: `(edits, pending_write, error_message)` where `error_message` is `None` on success and a diagnostic string on failure. Callers accumulate error messages into their stage report's error field (or a new warnings field), making unreadable files visible in the dry-run preview and the execution report.
- Why this coordination mechanism is the correct level: This is a failure boundary defect at a shared helper function. The correct mechanism is to make the failure explicit in the return type so that all four consuming stages can propagate it without each independently re-implementing error handling.
- Migration priority: before adding features

## F6: Submodules Stage Reads Accumulated Report via Stringly-Typed Stage Lookup

- Severity: Low
- Primary dimension: Sequencing
- Secondary dimensions: Consistency
- Boundary: `rename/stages.py:plan_submodules` ↔ `rename/plan.py:PipelineReport.find_stage` via string literal `"cross-refs"`
- Component A location: `src/architekta/rename/stages.py`, line 302: `cross_refs_report = accumulated.find_stage("cross-refs")`
- Component B location: `src/architekta/rename/plan.py`, lines 162–167 (`find_stage` method), and `rename/pipeline.py` line 48–49 where stage names are authoritatively defined
- Interaction description: `plan_submodules` looks up the cross-refs stage report by the string literal `"cross-refs"`. This string must match the `name` field in the `StageDescriptor` for stage 7 in `_STAGES`. If the stage name changes in the registry, the lookup silently returns `None` and the submodules planner skips its Case B logic without any error.
- Implicit assumption: The stage name `"cross-refs"` will remain stable across refactors.
- Violated principle: §3.2 Implicit Sequencing — the dependency from `plan_submodules` on `plan_cross_refs` having already run is expressed through a runtime string lookup that can silently return `None`, rather than through a structural mechanism.
- Operational consequence: If the cross-refs stage name is changed in the `_STAGES` registry, `plan_submodules` will silently skip all Case B submodule pointer updates. The pipeline completes without error, but submodule pointers remain stale.
- Growth scenario: Each new inter-stage dependency introduced via `find_stage` adds another stringly-typed coupling point.
- Evidence: `stages.py` line 302: `accumulated.find_stage("cross-refs")`. `pipeline.py` line 49: `StageDescriptor(7, "cross-refs", ...)`. `plan.py` line 165: `if stage.name == name: return stage`.
- Remediation: Define stage names as constants (e.g., `STAGE_CROSS_REFS = "cross-refs"`) in a shared location and use those constants in both the `StageDescriptor` declarations and in `find_stage` calls. Alternatively, pass the cross-refs `StageReport` directly to `plan_submodules` through its function signature, making the dependency explicit and type-checked.
- Why this coordination mechanism is the correct level: This is a low-severity coupling that manifests only on rename. A shared constant eliminates the stringly-typed fragility at minimal cost.
- Migration priority: next refactor cycle

## F7: GitHub URL Template Hardcoded in Two Locations

- Severity: Low
- Primary dimension: Consistency
- Secondary dimensions: Result Sharing
- Boundary: `rename/plan.py:_detect_submodule_refs` ↔ `rename/stages.py:plan_git_remote` via `git@github.com:{slug}.git` string template
- Component A location: `src/architekta/rename/plan.py`, lines 343–344: `old_submodule_url=f"git@github.com:{old_github}.git"`, `new_submodule_url=f"git@github.com:{new_github}.git"`
- Component B location: `src/architekta/rename/stages.py`, line 109: `new_url = f"git@github.com:{ctx.new_github}.git"`
- Interaction description: Both locations construct a GitHub SSH URL from a `GithubSlug` using the template `git@github.com:{slug}.git`. The template is duplicated with no shared constant or function.
- Implicit assumption: The GitHub URL scheme (SSH with `git@github.com:` prefix) is stable across both usages.
- Violated principle: §4.1 Single Source of Truth — the URL template is a fact declared independently in two locations.
- Operational consequence: If the project switches to HTTPS remote URLs, updating one site without the other would cause submodule URL mismatches, producing `git submodule sync` failures.
- Growth scenario: Any new stage that constructs GitHub URLs would face the same template duplication.
- Evidence: `plan.py` line 343: `f"git@github.com:{old_github}.git"`. `stages.py` line 109: `f"git@github.com:{ctx.new_github}.git"`.
- Remediation: Add a `ssh_url` property to the `GithubSlug` dataclass that returns `f"git@github.com:{self}.git"`. All URL construction sites consume this property. If the URL scheme needs to be configurable (SSH vs HTTPS), the property becomes the single point of change.
- Why this coordination mechanism is the correct level: This is a consistency violation on a simple derived value. A property on the existing value object is the minimal mechanism that eliminates the redundant declaration.
- Migration priority: opportunistically

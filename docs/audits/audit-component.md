# COMPONENT AUDIT REPORT — architekta

**Audit date:** 2026-03-31
**Auditor posture:** Adversarial — architecture is presumed defective until the code disproves it.
**Scope:** Component-level structural audit of all Python source under `src/architekta/`.

---

## 1. ARCHITECTURAL VERDICT

**Classification: serviceable but architecturally fragile**

The codebase demonstrates several sound structural decisions: frozen dataclasses for inter-layer data, a clean plan/execute separation in the rename pipeline, a typed `CommandResult` wrapper around subprocess calls, and an explicit stage registry with declarative descriptors. However, the architecture is weakened by duplicated infrastructure logic across modules that should share a single authoritative abstraction (GitHub URL parsing, file-scanning-and-replace), by a type-switch executor that must be edited for every new step variant, by domain-layer functions that perform I/O directly, and by unstructured diagnostic output that couples the adapter layer to ad hoc string formatting. The rename module's `plan.py` file accumulates context construction, domain models, value objects, and rendering into a single 390-line module, violating separation of concerns at the granularity where it matters most for future extension.

The codebase is fundamentally evolvable: its core data models are frozen and well-typed, its pipeline is explicitly staged, and its exception hierarchies are project-specific. But evolution is already showing early signs of structural instability — adding a new execution step type, a new sync target, or a new output format would each require modifying existing core logic rather than extending through stable seams.

---

## 2. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimensions | Structural Impact | Consequence Over Time |
|---|---|---|---|---|---|---|
| 1 | Type-switch executor defeats extensibility | High | Extensibility | Flexibility | Adding a new `ExecutionStep` variant requires editing the isinstance chain in the executor and ensuring the Union type is updated. No dispatch seam exists. | Every new step type forces modification of core execution logic, creating a growing, error-prone conditional tree. |
| 2 | Duplicated GitHub URL regex across modules | High | Redundancy | Modularity | The same regex appears in `github/utils.py` and `rename/plan.py`. Neither module knows about the other's copy. | Drift between the two copies creates silent parse divergence. Any change to GitHub URL formats must be applied in two places. |
| 3 | `plan.py` accumulates four distinct responsibilities | High | Separation of Concerns | Modularity | Value objects, context construction (with I/O), report models, and dry-run rendering coexist in one 390-line module. | The module becomes the default dumping ground for rename-related types, degrading navigability and increasing merge conflict surface. |
| 4 | `build_rename_context` performs I/O inside a domain module | High | Separation of Concerns | Robustness | `plan.py` contains a deferred import of `run_command` and calls `git remote get-url origin`. This is infrastructure I/O embedded in what the module docstring calls "domain models." | Domain code cannot be tested without a live git repository or mocking subprocess calls. The layer boundary is broken. |
| 5 | Diagnostic output uses ad hoc string formatting | Medium | Predictability | Ease of Use | All three command modules format output via hand-built `typer.echo(f"[TAG] ...")` strings with inconsistent tag vocabularies. | Adding a new output format requires rewriting every command module. Inconsistent vocabulary makes automated log parsing unreliable. |
| 6 | `_collect_edits_and_write` silently swallows OSError | Medium | Robustness | Predictability | The helper catches `OSError` on file read and returns `([], None)` with no diagnostic. Callers cannot distinguish "no matches" from "unreadable." | Unreadable files are silently skipped during rename with no user notification. |
| 7 | `github/operations.py` misrepresents its layer affiliation | Medium | Separation of Concerns | Predictability | Module docstring says "pure domain operations" but the module performs subprocess and HTTP I/O through injected callables. | Developers trusting the docstring will place further I/O here or attempt unit tests without mocking. |
| 8 | `env/commands.py` performs file I/O directly in the adapter | Medium | Separation of Concerns | Modularity | `plan.pth_file.write_text(...)` inside the Typer command handler. No application-layer execution function exists. | Adding execution concerns (rollback, logging) requires editing the CLI handler. |
| 9 | Rename stage registry is static with no extension seam | Low | Extensibility | Configurability | `_STAGES` is a module-level tuple literal. Adding a stage requires editing this tuple and importing the new planner. | Every new stage requires modifying two existing files instead of registering through a stable seam. |

---

## 3. DETAILED FINDINGS

## F1: Type-Switch Executor Defeats Extensibility

- Severity: High
- Primary dimension: Extensibility
- Secondary dimensions: Flexibility
- Location: `src/architekta/rename/stages.py:389-404` (`execute_stage_plan`)
- Symptom: The executor dispatches on `isinstance` checks across the `ExecutionStep` union (`PendingWrite`, `PathRename`, `ShellCommand`). Each branch performs a different kind of side effect.
- Violation: Extension via modification of a conditional chain rather than through protocol dispatch or visitor pattern. Violates §7.1 (Open/Closed Principle) and §6.7 (strategy substitution via if/elif type-switch).
- Principle: New behavior must be addable by introducing new implementations, not by modifying existing code paths.
- Root cause: `ExecutionStep` is a bare `Union` type alias with no shared protocol or method. The executor must know every concrete type and handle each one differently. There is no `execute()` method on the step types themselves, no visitor, and no registry.
- Blast radius: Every new step type (the union, the executor, and any code that constructs steps) must be modified in lockstep. The executor is the single execution chokepoint for all 9 pipeline stages.
- Future break scenario: Adding an `HttpRequest` step type for API-based renames (e.g., renaming a package on a registry) requires: (1) defining the dataclass, (2) adding it to the `ExecutionStep` union in `plan.py`, (3) adding an `elif isinstance(step, HttpRequest)` branch in `execute_stage_plan`. Missing step (3) causes the step to be silently dropped at runtime with no error.
- Impact: Silent data loss on missed step types; growing conditional complexity; inability to test execution logic per step type in isolation.
- Evidence: `stages.py:396-404`: `if isinstance(step, PendingWrite): ... elif isinstance(step, PathRename): ... elif isinstance(step, ShellCommand): ...` — no `else` branch exists, so an unrecognized step type is silently ignored.
- Remediation: Define a `Executable` protocol with an `execute(self) -> None` method. Each step dataclass implements the protocol. The executor becomes `for step in plan.steps: step.execute()`. Alternatively, if steps must remain inert data, introduce a step-type registry mapping each type to an executor function, and raise `TypeError` on unregistered types.
- Why this remediation is the correct abstraction level: The defect is a missing dispatch mechanism, not a missing utility function or domain object. Protocol dispatch eliminates the conditional chain and makes the extension seam structural. A registry-based alternative preserves the data/behavior separation if that is preferred.
- Migration priority: before adding features

## F2: Duplicated GitHub URL Regex Across Modules

- Severity: High
- Primary dimension: Redundancy
- Secondary dimensions: Modularity
- Location: `src/architekta/github/utils.py:64` and `src/architekta/rename/plan.py:14`
- Symptom: The regex pattern `r"github\.com[:/](.+?)/(.+?)(?:\.git)?$"` appears twice: once as a raw `re.search` call in `github/utils.py:get_github_remote`, and once as a compiled `_GITHUB_URL_RE` pattern in `rename/plan.py:GithubSlug.from_url`. Both extract owner and repo from a GitHub URL. Neither references the other.
- Violation: Duplication of parsing logic at identical granularity, violating §2 (Redundancy) and §3 (Modularity — independently reusable units).
- Principle: Duplication must be detected at every granularity and eliminated through the correct abstraction mechanism.
- Root cause: The `rename` module introduced its own `GithubSlug` value object with URL parsing, unaware that `github/utils.py` already had the same extraction logic. There is no shared value object or parsing function that both modules consume.
- Blast radius: `github/utils.py:get_github_remote` returns a raw `tuple[str, str]` while `rename/plan.py:GithubSlug` returns a typed dataclass. Any change to URL format handling must be applied in both places, and the two representations are not interchangeable.
- Future break scenario: GitHub changes its URL scheme (e.g., adding organization nesting). One regex is updated; the other silently fails to parse the new format.
- Impact: Maintenance burden, silent divergence risk, concept fragmentation (two representations of the same domain concept).
- Evidence: `github/utils.py:64`: `match = re.search(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$", stdout)`. `rename/plan.py:14`: `_GITHUB_URL_RE = re.compile(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$")`.
- Remediation: Promote `GithubSlug` to a shared domain value object (e.g., in `infrastructure.py` or a new `domain.py` module). Replace `github/utils.py:get_github_remote`'s raw tuple return with `GithubSlug`, and have it delegate URL parsing to `GithubSlug.from_url`. Delete the duplicate regex.
- Why this remediation is the correct abstraction level: This is a domain-object introduction, not a utility extraction. The concept "GitHub owner/repo" is a typed value with parsing semantics that belongs in exactly one place. `GithubSlug` already models it correctly; the fix is to make it authoritative.
- Migration priority: immediately

## F3: `plan.py` Accumulates Four Distinct Responsibilities

- Severity: High
- Primary dimension: Separation of Concerns
- Secondary dimensions: Modularity
- Location: `src/architekta/rename/plan.py` (entire file, 391 lines)
- Symptom: This single module contains: (a) value objects (`GithubSlug`, `FileEdit`, `PathRename`, `ShellCommand`, `PendingWrite`), (b) report models (`StageReport`, `StagePlan`, `PipelineReport`), (c) context construction with I/O (`build_rename_context`, `_detect_submodule_refs`), and (d) presentation logic (`render_dry_run`). These are four structurally independent concerns.
- Violation: Mixing domain value objects, report/result models, context-building orchestration (which performs I/O), and adapter-layer rendering in a single module. Violates §1.5 (components must not mix orchestration and business logic, I/O and transformation, construction and execution).
- Principle: Components must not mix construction and execution, I/O and transformation, interface adaptation and core computation.
- Root cause: The module was likely grown incrementally, with each new concept placed near its consumers. No structural split was introduced as the file grew.
- Blast radius: Every rename-related module imports from `plan.py`. Adding a new value object, a new report field, a new context parameter, or a new output format all require editing this single file.
- Future break scenario: Adding a JSON output format for CI integration requires either: (1) adding a second rendering function to `plan.py`, further bloating it, or (2) importing the report models from `plan.py` into a new renderer, which also pulls in the I/O-performing `build_rename_context` and all its transitive dependencies.
- Impact: Degraded navigability, unnecessary import coupling, growing file that resists decomposition the longer it is deferred.
- Evidence: The module defines 11 classes, 3 functions, and 1 compiled regex across 391 lines. `build_rename_context` imports `run_command` (infrastructure I/O). `render_dry_run` is pure presentation. `GithubSlug` is a reusable value object. `StageReport` is a pipeline-specific report model. These have no structural reason to coexist.
- Remediation: Split into at least three modules: (1) `rename/models.py` for value objects and report dataclasses, (2) `rename/context.py` for `RenameContext`, `build_rename_context`, `_detect_submodule_refs`, and supporting types, (3) `rename/render.py` for `render_dry_run`. Re-export from `rename/__init__.py` if backward compatibility is needed.
- Why this remediation is the correct abstraction level: This is a module decomposition, not a class extraction or strategy extraction. The four responsibilities are already structurally separable; they just happen to share a file.
- Migration priority: before adding features

## F4: `build_rename_context` Performs I/O Inside a Domain Module

- Severity: High
- Primary dimension: Separation of Concerns
- Secondary dimensions: Robustness
- Location: `src/architekta/rename/plan.py:251-261`
- Symptom: `build_rename_context` contains a deferred `from architekta.infrastructure import run_command` and invokes `run_command(["git", "-C", ..., "remote", "get-url", "origin"])` to auto-detect the GitHub owner. This is subprocess I/O inside a module whose docstring reads "Domain models for the rename pipeline."
- Violation: Domain code performing infrastructure I/O, violating §1.2 ("Domain code must be pure: no file reads, writes, subprocesses, environment access") and §1.3 (dependency direction: never Domain → Infrastructure).
- Principle: Domain code must be pure. Infrastructure performs effects but does not own policy.
- Root cause: The `github_owner` auto-detection was placed inside the context builder for convenience, rather than being resolved at the adapter boundary and passed in as a pre-resolved parameter.
- Blast radius: Any test of `build_rename_context` requires either a real git repository or mocking `subprocess.run`. The `_detect_submodule_refs` helper also performs file I/O (`gitmodules.read_text`), compounding the impurity. The entire context-building path is untestable without side effects.
- Future break scenario: Adding a new auto-detection source (e.g., reading from a config file, querying a package registry) further embeds I/O in the domain layer.
- Impact: Untestable domain code, broken layer invariant, precedent for further I/O embedding in domain modules.
- Evidence: `plan.py:251-261`: `from architekta.infrastructure import run_command` / `result = run_command(["git", "-C", str(old_project_path), "remote", "get-url", "origin"])`. Also `plan.py:336`: `content = gitmodules.read_text(encoding="utf-8")` inside `_detect_submodule_refs`.
- Remediation: Move `github_owner` resolution to the adapter layer (`rename/commands.py`) or an application-layer factory. The CLI command resolves the owner (using infrastructure) and passes it as a required parameter to `build_rename_context`. Similarly, move submodule detection to an infrastructure function that returns data, and pass the results into the context builder. `build_rename_context` becomes a pure constructor of a frozen dataclass.
- Why this remediation is the correct abstraction level: This is a responsibility relocation to the correct layer, not a new abstraction. The context builder should be a pure assembler of pre-resolved data. I/O belongs at the adapter or infrastructure boundary.
- Migration priority: before adding features

## F5: Diagnostic Output Uses Ad Hoc String Formatting with Inconsistent Vocabulary

- Severity: Medium
- Primary dimension: Predictability
- Secondary dimensions: Ease of Use
- Location: `src/architekta/env/commands.py:46-57`, `src/architekta/github/commands.py:30-43`, `src/architekta/rename/commands.py:112-135`
- Symptom: All three command modules format diagnostics as hand-built `f"[TAG] ..."` strings passed to `typer.echo`. The tag vocabulary is inconsistent: `env` uses `[ERROR]` and `[OK]`, `github` uses `[ERR]`, `[OK]`, `[DRY]`, `[SET]`, `[SKIP]`, `[WARN]`, and `rename` uses `[ERR]`, `[OK]`, `[SKIP]`.
- Violation: Diagnostics are ad hoc formatted strings rather than structured records, violating §8.1 ("User-facing diagnostics are structured records, not ad hoc formatted strings") and §8.2 ("Adapters own rendering").
- Principle: User-facing diagnostics are structured records. Adapters own rendering.
- Root cause: No shared diagnostic model or formatter exists. Each command module independently formats output, leading to vocabulary drift.
- Blast radius: All three command modules. Any future command module will copy-paste one of the existing patterns.
- Future break scenario: Adding machine-parseable output (JSON mode, structured logging) requires rewriting the formatting logic in every command module.
- Impact: Unreliable output format for automation consumers, duplicated formatting code, inconsistent user experience across subcommands.
- Evidence: `env/commands.py:46`: `typer.echo(f"[ERROR] {plan.skip_reason}", err=True)`. `github/commands.py:41`: `typer.echo(f"[ERR]  {entry.project_name} [{entry.target}]: {entry.message}", err=True)`. `rename/commands.py:112`: `typer.echo(f"[SKIP] {stage.name}: {stage.skip_reason}", err=True)`.
- Remediation: Introduce a diagnostic record type (e.g., `@dataclass(frozen=True) class DiagnosticEntry: level: DiagnosticLevel, context: str, message: str`) and a shared formatter function that all command modules delegate to. The formatter is the single rendering boundary; swapping it to JSON or structured logging becomes a one-point change.
- Why this remediation is the correct abstraction level: This is a domain-object introduction (the diagnostic record) plus a service-boundary split (the formatter). It is not a utility extraction because the problem is a missing structured contract.
- Migration priority: next refactor cycle

## F6: `_collect_edits_and_write` Silently Swallows File Read Errors

- Severity: Medium
- Primary dimension: Robustness
- Secondary dimensions: Predictability
- Location: `src/architekta/rename/stages.py:431-434`
- Symptom: The helper catches `OSError` and returns `([], None)`, identical to the "no matches" return. Callers (`plan_self_refs`, `plan_cross_refs`, `plan_workspaces`, `plan_submodules`) cannot distinguish a file that had no old-name occurrences from a file that was unreadable.
- Violation: Silent fallback where deterministic policy is required, violating §8.7 ("No silent fallbacks or partial initialization") and §8.5 ("Infrastructure reports failures but does not decide whether to retry").
- Principle: No silent fallbacks. Infrastructure reports failures; application code decides recovery policy.
- Root cause: The error handling was designed for convenience (skip unreadable files) rather than correctness (report unreadable files and let the caller decide).
- Blast radius: Four stage planners call this helper. In all four, an unreadable file is silently dropped from the rename plan.
- Future break scenario: A permission error on a critical file (e.g., `pyproject.toml`) causes the rename to succeed with a partially updated project. The user discovers the inconsistency only when the project fails to build.
- Impact: Incomplete renames with no user-visible warning; impossible to audit which files were actually processed.
- Evidence: `stages.py:431-434`: `try: content = file_path.read_text(encoding="utf-8") / except OSError: return [], None`.
- Remediation: Return a structured result that distinguishes "no changes" from "read error." Add an optional `error: str | None` field to the return, or return a small `FileProcessingResult` dataclass. Stage planners accumulate read errors into `StageReport.error` so they surface in dry-run output and execution logs.
- Why this remediation is the correct abstraction level: This is a result-object introduction to make failure paths structurally explicit. The current `tuple[list, Optional]` return type cannot encode the error case.
- Migration priority: before adding features

## F7: `github/operations.py` Misrepresents Its Layer Affiliation

- Severity: Medium
- Primary dimension: Separation of Concerns
- Secondary dimensions: Predictability
- Location: `src/architekta/github/operations.py` (entire module, especially lines 173–179)
- Symptom: The module docstring reads "Pure domain operations for GitHub synchronization." However, `_read_github_description` calls `get_github_remote` which invokes `run_command` (subprocess I/O), and then calls `get_current_description` which invokes `gh repo view` (HTTP API call via subprocess).
- Violation: The module performs infrastructure I/O while claiming to be domain-pure. Violates §1.2 ("Domain code must be pure") and §1.4 (data flow direction).
- Principle: Domain code must be pure: no file reads, writes, subprocesses, environment access, or logging side effects.
- Root cause: The `TargetBinding` pattern correctly separates read/write callables from the sync logic. However, the concrete callables perform I/O and are defined in the same module, making the module impure despite the structural attempt at separation.
- Blast radius: Local to the `github` module, but the mislabeling sets a precedent: developers see "pure domain operations" performing I/O and replicate the pattern.
- Future break scenario: A developer writes tests for `sync_descriptions` expecting pure behavior, discovers it requires network mocking, and either gives up on testing or adds fragile mocks.
- Impact: Misleading module contract, hidden test complexity, layer violation precedent.
- Evidence: Module docstring at line 1: `"""Pure domain operations for GitHub synchronization."""`. Lines 173–175: `def _read_github_description(project_dir: Path): owner, repo = get_github_remote(project_dir) ...` — both `get_github_remote` and `get_current_description` call `run_command`.
- Remediation: Rename the module to reflect its actual role (e.g., `github/sync.py` as an application-layer orchestrator). Move the I/O-performing callables into `github/utils.py` or keep them in the module but drop the "pure domain" label. Alternatively, inject the read/write callables from the adapter layer so that `operations.py` truly becomes pure.
- Why this remediation is the correct abstraction level: This is a layer-boundary correction — either honest labeling of an application-layer module or genuine extraction of I/O to infrastructure. The structural shape (TargetBinding) is already correct; the fix is aligning the declared contract with actual behavior.
- Migration priority: next refactor cycle

## F8: `env/commands.py` Performs File Write I/O Directly in the Adapter Layer

- Severity: Medium
- Primary dimension: Separation of Concerns
- Secondary dimensions: Modularity
- Location: `src/architekta/env/commands.py:56`
- Symptom: The Typer command handler `install_editable` calls `plan.pth_file.write_text(...)` directly. The planning layer (`env/operations.py`) produces an `InstallPlan`, but there is no execution layer — the adapter itself performs the file write.
- Violation: Mixing interface adaptation with execution, violating §1.2 ("Adapters are thin: parse external input, call application use-cases, format output") and §1.5 ("Components must not mix construction and execution").
- Principle: Adapters are thin: parse external input, call application use-cases, format output.
- Root cause: The `env` module has a plan layer (`operations.py`) but no corresponding execute layer. The `InstallPlan` dataclass is correctly designed to carry execution data, but nobody consumes it except the CLI handler.
- Blast radius: Local to the `env` module. However, the pattern is structurally analogous to the rename module's plan/execute split, suggesting the `env` module was left incomplete.
- Future break scenario: Adding execution concerns (logging writes, rollback on partial failure, permission checks) requires editing the CLI handler, coupling adapter code to increasingly complex execution logic.
- Impact: Adapter layer accumulates execution responsibility; no reusable execution function for programmatic callers.
- Evidence: `env/commands.py:56`: `plan.pth_file.write_text("\n".join(plan.lines))`. Compare with the rename module, which has an explicit `execute_stage_plan` function.
- Remediation: Introduce an `execute_install_plan(result: InstallResult) -> None` function in `env/operations.py` (or a new `env/executor.py`) that performs the file writes. The CLI handler calls `plan_editable_install` then `execute_install_plan`, maintaining the thin-adapter pattern.
- Why this remediation is the correct abstraction level: This is a service-boundary split — separating execution from presentation. The plan dataclass already carries all the data needed; the missing piece is the execution function.
- Migration priority: next refactor cycle

## F9: Rename Stage Registry Is Closed to Extension

- Severity: Low
- Primary dimension: Extensibility
- Secondary dimensions: Configurability
- Location: `src/architekta/rename/pipeline.py:45-55`
- Symptom: `_STAGES` is a module-level tuple literal. Adding a new stage requires: (1) writing the planner function in `stages.py`, (2) importing it into `pipeline.py`, (3) editing the `_STAGES` tuple. There is no registration API, decorator, or entry-point mechanism.
- Violation: Extension via source modification of a central tuple, violating §7.5 ("New variants must be introducible through stable extension seams") and §7.1 (Open/Closed Principle).
- Principle: New behavior is added by introducing new implementations, not by modifying existing code paths.
- Root cause: The registry was designed as a static declaration for the initial 9 stages. No extension seam was introduced because all stages were known at design time.
- Blast radius: Localized to `pipeline.py` and `stages.py`. The blast radius is lower than other findings because the edit surface is small and well-defined.
- Future break scenario: Adding 3–4 new stages (e.g., Docker, CI config, package registry, documentation cross-refs) turns the tuple into a long, order-sensitive list where insertion position matters.
- Impact: Moderate maintenance friction; does not block current development but will compound as stage count grows.
- Evidence: `pipeline.py:45-55`: `_STAGES: tuple[StageDescriptor, ...] = (StageDescriptor(1, "validate", False, plan_validate), ... StageDescriptor(9, "commit", True, plan_commit))`.
- Remediation: Introduce a `register_stage` function or decorator that appends to a mutable registry, with explicit ordering constraints (e.g., `after="filesystem"`, `before="commit"`). Alternatively, keep the static tuple but extract it to a dedicated `rename/registry.py` module with a `get_stages()` function that external code can wrap or extend.
- Why this remediation is the correct abstraction level: This is a registry introduction — the standard mechanism for open/closed collections. The static tuple is acceptable at the current scale but should evolve into a registration-based design before the stage count grows further.
- Migration priority: opportunistically

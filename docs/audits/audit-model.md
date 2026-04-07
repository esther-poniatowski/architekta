# MODEL AUDIT REPORT — architekta

**Audit date:** 2026-03-31
**Auditor posture:** The code's abstractions are presumed arbitrary until shown to correspond to the problem domain.

---

## 1. DOMAIN CONCEPT MAP

Derived from README.md, docs/index.md, docs/guide/*.md, and docs/internals/rename-pipeline.md **before** reading any source code.

| # | Concept | Type | Essential Attributes | Relationships |
|---|---------|------|---------------------|---------------|
| D1 | **Project Identity** | Entity | name, path, github (owner/repo), conda_env, workspace file, obsidian_vault flag, aliases (former names) | Central entity referenced by all rename stages; contained within Registry; source and target of Dependency Edges |
| D2 | **Project Registry** | Entity | collection of Project Identity records, collection of Dependency Edges, root path, format (TOML) | Contains D1, D9; single source of truth for rename pipeline; consumed by rename, validate, audit, render commands |
| D3 | **Surface** | Classification | name (filesystem, GitHub, conda, VS Code workspace, submodule, self-references, cross-references) | A project's name is encoded across multiple Surfaces; each rename Stage targets one or more Surfaces |
| D4 | **Rename Operation** | Process | old_name, new_name, project_path, affected_paths, aliases, options (dry_run, push, skip, verbose) | Top-level process; orchestrates the Pipeline |
| D5 | **Rename Pipeline** | Process | ordered sequence of Stages, two phases (plan then execute) | Contains D6; consumes D7 (RenameContext); produces D8 (PipelineReport) |
| D6 | **Pipeline Stage** | Entity | stage_id, name, skippable flag, ordering constraints | Component of Pipeline; each stage targets one or more Surfaces; produces a StageReport; consumes RenameContext |
| D7 | **Rename Context** | Entity | old/new names, old/new paths, old/new GitHub slugs, old/new conda env, old/new workspace, patterns, affected projects, submodule refs, workspace_root, skip_stages, push | Immutable pre-computed state consumed by all stages; derived from Project Identity and CLI inputs |
| D8 | **Rename Plan / Pipeline Report** | Entity | per-stage reports (path renames, file edits, commands), dry_run flag, success status | Output of pipeline; consumed by dry-run renderer and CLI reporter |
| D9 | **Dependency Edge** | Relationship | dependent project, dependency project, integration mechanism | Connects two Project Identity records; determines which files encode cross-references |
| D10 | **Integration Mechanism** | Classification | editable-pip, git-submodule, conda-channel | Classifies D9; determines which specific files to scan during cross-ref stage |
| D11 | **Affected Project** | Entity | name, path | A project with a dependency edge to/from the renamed project; scanned for cross-references |
| D12 | **Name Pattern** | Entity | search string, replace string, ordering (longest-first) | Collection of patterns derived from Project Identity; consumed by self-ref and cross-ref stages |
| D13 | **Conda Environment** | Entity | name, path (site-packages) | Target of env management commands; target of rename stage 5 |
| D14 | **Editable Install** | Process | workspace_root, site_packages, package selection, flags | Managed by env module; produces InstallPlan |
| D15 | **Package** | Entity | name, path (under src/) | Target of editable install; resolved from workspace root |
| D16 | **Editable Install Plan** | Entity | package, pth_file path, lines to write, skipped flag | Output of planning; input to execution |
| D17 | **Project Description** | Entity | text (first prose sentence from README) | Extracted from README; propagated to Metadata Sync Targets |
| D18 | **Metadata Sync Target** | Classification | GitHub repo description, pyproject.toml description field | Destination for description propagation; each target has read/write behavior |
| D19 | **Dry Run Mode** | Constraint | boolean flag | Cross-cutting mode that causes all operations to plan without executing |
| D20 | **Submodule Reference** | Relationship | host project, old URL, new URL | Links a host project to a vendored project via .gitmodules |

---

## 2. MODEL VERDICT

**Classification: partially modeled**

The rename pipeline and environment management modules are well-modeled. The rename domain has explicit types for RenameContext, PipelineReport, StageReport, StagePlan, FileEdit, PathRename, ShellCommand, PatternPair, AffectedProject, SubmoduleRef, and GithubSlug — a rich and deliberate domain model. The env module has explicit types for EditableInstallRequest, InstallPlan, InstallResult, and PackageSpec. The github module has explicit types for SyncTargetResult, SyncBatchResult, and TargetBinding.

However, the Project Registry — which the design document identifies as the central entity and single source of truth — has no code counterpart whatsoever. The registry is described in extensive detail in docs/internals/rename-pipeline.md (with a proposed TOML schema, dependency edges, integration mechanisms, and derived artifacts), yet the codebase contains no `registry/` module. This means the rename pipeline operates without access to the structured project identity model that its design requires. Surface and Integration Mechanism, two domain classifications that determine which files to scan per stage, have no code representation. The pipeline instead relies on CLI arguments to supply what the registry would provide.

The model is adequate for the system's current use cases — a single manually-parameterized rename invocation works. It will not support the planned extensions (registry validate, registry render, registry audit, automatic affected-project discovery, integration-mechanism-aware file targeting) without introducing the missing domain types.

---

## 3. EXECUTIVE FINDINGS

| # | Title | Severity | Primary Dimension | Secondary Dimension | Domain Concept | Mapping Category | Cost |
|---|-------|----------|-------------------|---------------------|----------------|------------------|------|
| 1 | Project Registry absent | Critical | Concept Coverage | Relationship Coverage | D2: Project Registry | Domain gap | Every consumer that needs project identity or dependency topology must receive it via CLI flags; no machine-readable source of truth exists |
| 2 | Dependency Edge unmodeled | Critical | Relationship Coverage | Concept Coverage | D9: Dependency Edge | Domain gap | Cross-ref and submodule stages cannot discover affected projects or target mechanism-specific files; users must manually enumerate --affected-path |
| 3 | Integration Mechanism unmodeled | High | Concept Coverage | — | D10: Integration Mechanism | Domain gap | All cross-reference scanning uses undifferentiated text search; mechanism-specific file targeting is not implemented |
| 4 | Surface classification implicit | Medium | Concept Coverage | Abstraction Fidelity | D3: Surface | Domain gap | No enumeration of surfaces exists; stage-to-surface mapping is implicit in code structure |
| 5 | Project Identity fragmented across CLI flags | Medium | Abstraction Fidelity | Concept Coverage | D1: Project Identity | Misaligned | The domain concept of a project's full identity is reconstructed ad-hoc from CLI arguments rather than loaded from a first-class record |
| 6 | Project Description has no domain type | Low | Concept Coverage | — | D17: Project Description | Domain gap | The extracted description is a transient string; no type captures source, text, and sync targets as a unit |
| 7 | StageDescriptor stage_id inconsistency | Low | Abstraction Fidelity | — | D6: Pipeline Stage | Misaligned | Commit stage has stage_id=10 in its report but 9 in the descriptor, signaling the absent registry stage |

---

## 4. DETAILED FINDINGS

## F1: Project Registry Absent

- Severity: Critical
- Primary dimension: Concept Coverage
- Secondary dimension: Relationship Coverage
- Domain concept: D2 — Project Registry
- Concept type: entity
- Code construct: absent — no `registry/` module, no `registry.toml` parser, no registry schema type
- Mapping category: domain gap
- Ad-hoc derivation sites: `src/architekta/rename/commands.py` (CLI flags `--affected-path`, `--alias`, `--github-owner`, `--conda-env`, `--workspace` collectively encode what the registry would provide); `src/architekta/rename/plan.py:build_rename_context()` reconstructs project identity from these scattered inputs
- Consumers affected: `rename` command (needs project identity, dependency edges, aliases), planned `registry validate` command, planned `registry render` command, planned `registry audit` command, `github sync-descriptions` (currently uses filesystem discovery instead of registry lookup)
- Architectural cost: Without the registry, every rename invocation requires the user to manually supply affected paths, aliases, conda env name, workspace file, and GitHub owner. The system cannot automatically discover which projects are affected by a rename, cannot validate that all surfaces are accounted for, and cannot perform post-rename audits for stale references. The five planned `registry` subcommands described in the design document cannot be implemented.
- Evidence: The design document (`docs/internals/rename-pipeline.md`, lines 92–223) specifies a complete registry schema in TOML with project identity records and dependency edges. The implementation module structure proposed in the same document (`src/architekta/registry/`) with `schema.py`, `render.py`, `audit.py`, and `commands.py` does not exist. The CLI currently compensates by accepting `--affected-path` (repeatable), `--alias` (repeatable), `--github-owner`, `--conda-env`, and `--workspace` as manual substitutes for registry data.
- Remediation: Introduce a `registry` module with a `ProjectIdentity` dataclass (name, path, github, conda_env, workspace, obsidian_vault, aliases), a `Registry` aggregate type that loads and validates the TOML file, and modify `build_rename_context` to accept a `Registry` instance as its primary input (with CLI flags as overrides, not primary source).
- Domain justification for remediation: The registry is the canonical representation of project identity and inter-project topology. It is the concept that enables the system to transition from manually-parameterized single-project operations to ecosystem-wide automated operations — the system's stated design goal.
- Migration priority: before adding features

## F2: Dependency Edge Unmodeled

- Severity: Critical
- Primary dimension: Relationship Coverage
- Secondary dimension: Concept Coverage
- Domain concept: D9 — Dependency Edge
- Concept type: relationship
- Code construct: absent — no type for dependency edges, no representation of dependent/dependency/mechanism triples
- Mapping category: domain gap
- Ad-hoc derivation sites: `src/architekta/rename/plan.py:_detect_submodule_refs()` (lines 323–346) partially derives one type of dependency edge (git-submodule) by scanning `.gitmodules` files; `src/architekta/rename/stages.py:plan_cross_refs()` (lines 235–263) scans all tracked files in affected projects without distinguishing mechanisms
- Consumers affected: `plan_cross_refs` (needs to know which files encode a dependency for mechanism-specific targeting), `plan_submodules` (needs the complete set of submodule edges), `plan_validate` (needs to verify that all affected projects are reachable), any future `registry audit` command
- Architectural cost: Cross-reference scanning is undifferentiated: `plan_cross_refs` scans every tracked file in every affected project rather than targeting mechanism-specific files (e.g., `environment.yml` for editable-pip, `.gitmodules` for git-submodule, `pyproject.toml` for conda-channel). This produces false-positive matches in documentation and comments, cannot distinguish intentional references from incidental name collisions, and will scale poorly as the ecosystem grows.
- Evidence: The design document defines a dependency edge schema with `dependent`, `dependency`, and `mechanism` fields (`docs/internals/rename-pipeline.md`, lines 73–86) and specifies mechanism-specific file targeting in stage 7 (lines 363–370). The implementation in `plan_cross_refs` ignores the mechanism entirely: it calls `list_tracked_files(ap.path)` for each affected project and applies patterns to all text files indiscriminately.
- Remediation: Introduce a `DependencyEdge` dataclass with `dependent: str`, `dependency: str`, `mechanism: IntegrationMechanism` fields. Have the cross-refs planner use the mechanism to narrow file scanning (e.g., only scan `environment.yml` and `pyproject.toml` for `editable-pip` edges, only `.gitmodules` for `git-submodule` edges, then a broader scan for documentation files).
- Domain justification for remediation: A dependency edge is a load-bearing relationship that determines which files encode a project's name in another project. Without it, the cross-reference stage cannot distinguish structural references (which must be updated) from incidental mentions (which may be false positives).
- Migration priority: before adding features

## F3: Integration Mechanism Unmodeled

- Severity: High
- Primary dimension: Concept Coverage
- Secondary dimension: —
- Domain concept: D10 — Integration Mechanism
- Concept type: classification
- Code construct: absent — no enum, no type, no string constants for editable-pip / git-submodule / conda-channel
- Mapping category: domain gap
- Ad-hoc derivation sites: `src/architekta/rename/plan.py:_detect_submodule_refs()` implicitly handles the git-submodule mechanism by checking for `.gitmodules`; no code handles editable-pip or conda-channel mechanisms specifically
- Consumers affected: `plan_cross_refs` (needs mechanism to select files), `plan_submodules` (needs mechanism to distinguish submodule edges from other edges), any future `registry render` command (needs mechanism for dependency table formatting)
- Architectural cost: The system cannot perform mechanism-aware file targeting. The design document specifies that `editable-pip` edges should target `environment.yml` and `pyproject.toml`, `git-submodule` edges should target `.gitmodules`, and `conda-channel` edges should target `environment.yml` (package name). Without this classification, all files are scanned uniformly, making cross-reference replacement imprecise and brittle.
- Evidence: The design document (`docs/internals/rename-pipeline.md`, lines 73–86, 363–370) defines three mechanisms with specific file targeting rules. The code contains no equivalent classification. `_detect_submodule_refs` (plan.py, lines 323–346) hard-codes `.gitmodules` detection but does not represent it as a mechanism type.
- Remediation: Introduce an `IntegrationMechanism` enum with members `EDITABLE_PIP`, `GIT_SUBMODULE`, `CONDA_CHANNEL`. Each member should declare which files it implies (as a class method or lookup table). This classification feeds into the `DependencyEdge` type (Finding 2) and drives mechanism-specific file targeting in `plan_cross_refs`.
- Domain justification for remediation: Integration mechanism is a classification that determines which files encode a dependency. It is the concept that transforms cross-reference scanning from "search everything" to "search the right files," which is essential for correctness at scale.
- Migration priority: before adding features

## F4: Surface Classification Implicit

- Severity: Medium
- Primary dimension: Concept Coverage
- Secondary dimension: Abstraction Fidelity
- Domain concept: D3 — Surface
- Concept type: classification
- Code construct: absent as a type — surfaces are implicit in the stage names and the `_STAGES` tuple in `src/architekta/rename/pipeline.py`
- Mapping category: domain gap
- Ad-hoc derivation sites: Each stage planner (`plan_filesystem`, `plan_git_remote`, `plan_workspaces`, `plan_conda`, `plan_self_refs`, `plan_cross_refs`, `plan_submodules`, `plan_commit`) implicitly corresponds to one or more surfaces, but this mapping is nowhere declared
- Consumers affected: `plan_validate` (should verify that all surfaces are accounted for), dry-run renderer (could organize output by surface rather than by stage), any future surface-extensibility mechanism
- Architectural cost: Adding a new surface (e.g., Docker image tags, CI workflow references — mentioned in the design document as foreseeable extensions) requires creating a new stage planner function, adding it to `_STAGES`, and knowing which surfaces the existing stages already cover. There is no declared inventory of surfaces. The design document's surface table (docs/internals/rename-pipeline.md, lines 9–22) has no code counterpart.
- Evidence: The design document enumerates 8 named surfaces in a table. The code has no `Surface` enum or equivalent. Stage names loosely correspond to surfaces, but the mapping is implicit: `workspaces` maps to VS Code, `git-remote` maps to GitHub, `conda` maps to Conda. No code declares this correspondence.
- Remediation: Introduce a `Surface` enum (FILESYSTEM, GITHUB, VSCODE_WORKSPACE, CONDA, SELF_REFERENCES, CROSS_REFERENCES, SUBMODULES, OBSIDIAN). Annotate each `StageDescriptor` with the set of surfaces it covers. This makes the stage-to-surface mapping explicit and verifiable, and provides a hook for validation that all known surfaces are covered by at least one stage.
- Domain justification for remediation: A surface is a location where a project's name is encoded. It is the fundamental unit of the rename problem statement. Making it explicit enables the system to verify completeness: every surface must be covered by at least one stage.
- Migration priority: next refactor cycle

## F5: Project Identity Fragmented Across CLI Flags

- Severity: Medium
- Primary dimension: Abstraction Fidelity
- Secondary dimension: Concept Coverage
- Domain concept: D1 — Project Identity
- Concept type: entity
- Code construct: `src/architekta/rename/plan.py:RenameContext` (partial representation) and `src/architekta/rename/plan.py:build_rename_context()` (ad-hoc assembly)
- Mapping category: misalignment
- Ad-hoc derivation sites: `build_rename_context()` (plan.py, lines 220–320) assembles a project's identity from 7 separate CLI parameters; the rename CLI command (commands.py, lines 18–93) passes 13 parameters through to `run_rename_pipeline`
- Consumers affected: `build_rename_context`, `plan_validate`, every stage planner (all consume `RenameContext` which embeds the fragmented identity)
- Architectural cost: `RenameContext` conflates project identity (name, path, GitHub slug, conda env, workspace, aliases) with pipeline configuration (skip_stages, push, dry_run). The project identity attributes are not extracted from a first-class `ProjectIdentity` type but reconstructed from separate CLI arguments. This means: (1) the identity of the renamed project cannot be validated against a known-good source (the registry), (2) the identity cannot be reused across commands, and (3) adding new identity attributes requires modifying both the CLI and `build_rename_context`.
- Evidence: `RenameContext` has 17 fields, of which approximately 11 describe project identity and 6 describe pipeline behavior. The design document's identity record schema has 7 fields. These two structures are interleaved in `RenameContext` rather than composed.
- Remediation: Extract a `ProjectIdentity` dataclass from `RenameContext` with fields: name, path, github (GithubSlug), conda_env, workspace, aliases. `RenameContext` then composes two `ProjectIdentity` instances (old and new) plus pipeline configuration fields. This separation allows `ProjectIdentity` to be loaded from the registry (Finding 1) or constructed from CLI flags, and reused across commands.
- Domain justification for remediation: Project Identity is the central domain entity. Separating it from pipeline configuration captures the distinction between "what the project is" and "how to rename it."
- Migration priority: before adding features

## F6: Project Description Has No Domain Type

- Severity: Low
- Primary dimension: Concept Coverage
- Secondary dimension: —
- Domain concept: D17 — Project Description
- Concept type: entity
- Code construct: absent as a type — the description is a transient `str` passed between `extract_readme_description()` and `sync_descriptions()`
- Mapping category: domain gap
- Ad-hoc derivation sites: `src/architekta/github/utils.py:extract_readme_description()` returns a bare `str`; `src/architekta/github/operations.py:sync_descriptions()` passes it as a `str` parameter named `desired`
- Consumers affected: `sync_descriptions` (receives a bare string), `_sync_target` (receives the same bare string), `SyncTargetResult` (stores `desired: str | None` without provenance)
- Architectural cost: The description's source (which README, which line) is lost after extraction. When a description sync fails or produces unexpected results, there is no way to trace back to the source line. The cost is minor because there is currently only one consumer.
- Evidence: `extract_readme_description` (utils.py, lines 19–46) returns a `str`. `SyncTargetResult` stores `current: str | None` and `desired: str | None` without recording the source file, line number, or extraction method.
- Remediation: Introduce a `ProjectDescription` value object with `text: str`, `source_file: Path`, and `source_line: int`. This is a low-priority enhancement that would primarily improve diagnostic output.
- Domain justification for remediation: A description is not just a string — it is a value extracted from a specific location in a specific file. Capturing the provenance makes the sync operation auditable.
- Migration priority: opportunistically

## F7: StageDescriptor Numbering Gap Signals Absent Registry Stage

- Severity: Low
- Primary dimension: Abstraction Fidelity
- Secondary dimension: —
- Domain concept: D6 — Pipeline Stage
- Concept type: entity
- Code construct: `src/architekta/rename/pipeline.py:_STAGES` tuple and `src/architekta/rename/stages.py:plan_commit()` (line 379: `stage_id=10`)
- Mapping category: misalignment
- Ad-hoc derivation sites: none — this is a static declaration
- Consumers affected: `PipelineReport` consumers, dry-run renderer, any code that uses `stage_id` to order or identify stages
- Architectural cost: The design document specifies 10 stages (validate through commit), with stage 9 being the registry update. The implementation has 9 stages but assigns `stage_id=10` to commit and leaves stage_id=9 unused. This numbering ghost signals that the registry stage was planned but not implemented. The `_STAGES` tuple defines commit as `StageDescriptor(9, "commit", ...)` with `stage_id=9`, but `plan_commit` internally creates a `StageReport` with `stage_id=10`. This inconsistency means `StageReport.stage_id` is unreliable: the descriptor says 9, the report says 10.
- Evidence: `pipeline.py` line 54: `StageDescriptor(9, "commit", True, plan_commit)`. `stages.py` line 379: `StageReport(stage_id=10, name="commit", ...)`. The design document (`docs/internals/rename-pipeline.md`, lines 247–261) shows stage 9 as Registry and stage 10 as Commit.
- Remediation: Either (a) introduce the registry stage as stage 9 and keep commit as stage 10 (the design-documented order), or (b) renumber commit to stage_id=9 in `plan_commit` to match the `StageDescriptor`. Option (a) is preferred because it aligns with the design intent and addresses Finding 1 simultaneously.
- Domain justification for remediation: Pipeline stages have a defined identity (stage_id) and ordering. The numbering gap and the descriptor/report inconsistency indicate a misalignment between the design's stage model and the implementation's stage model.
- Migration priority: immediately (trivial fix for the numbering inconsistency; the registry stage itself is Finding 1's scope)

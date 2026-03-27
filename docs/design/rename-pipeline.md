# Design: Cross-Surface Project Rename Pipeline

**Status**: Proposed

---

## Problem Statement

A project in this ecosystem exists simultaneously across multiple surfaces that each encode
the project's name:

| Surface | Where the name appears | Example |
|---------|------------------------|---------|
| **Filesystem** | Local directory name | `work/research/geonexus/` |
| **Git** | Remote URL | `git@github.com:esther-poniatowski/geonexus.git` |
| **GitHub** | Repository name and description | `esther-poniatowski/geonexus` |
| **VS Code** | Workspace file name and folder entries | `geonexus.code-workspace`, `dev-repos.code-workspace` |
| **Obsidian** | Vault name (derived from directory name) | — |
| **Conda** | Environment name | `name: geonexus` in `environment.yml` |
| **Self-references** | Mentions within the project's own files | README, CLAUDE.md, docs, settings, comments |
| **Cross-references** | Mentions in other projects | `dependencies.yml`, `.gitmodules`, `environment.yml` pip paths, `pyproject.toml` optional deps, agent instructions |

Renaming a project requires propagating the new name consistently to every surface. The
March 2026 rename of `RS-ctx-dep-net` to `geonexus` required 30+ file edits across
8 repositories, a conda environment rename, submodule URL updates, and coordinated
commits and pushes. The operation was manual, error-prone, and took a full interactive
session.

### Root causes

1. **No machine-readable project registry.** Project identity (name, path, dependencies,
   integration mechanisms) is scattered across human-readable Markdown files
   (`dev/projects.md`, `dev/dependencies.md`, `dev/names.md`).
   These cannot be consumed by a rename pipeline.

2. **No canonical identity model.** There is no single declaration of "this project is
   called X, lives at Y, has conda env Z, and appears in these workspaces." Each surface
   encodes the name independently, with no shared schema.

3. **No propagation tool.** The ecosystem has tools for _within-project_ operations
   (ktisma for LaTeX builds, eutaxis for governance, architekta for environment and
   GitHub metadata) but no tool for _cross-project identity propagation_.

### Questions to address

1. What structured registry is needed to make project identity machine-readable?
2. What pipeline stages must a rename operation execute, and in what order?
3. What safety mechanisms prevent partial or inconsistent renames?

---

## Project Identity Model

Each project in the ecosystem has an **identity record** — the minimal set of fields that
a rename operation must inspect and potentially update.

```yaml
# Proposed schema for a single project identity record.
name: geonexus
path: work/research/geonexus          # Relative to a common root
github: esther-poniatowski/geonexus   # GitHub owner/repo
conda_env: geonexus                   # Conda environment name (null if none)
workspace: geonexus.code-workspace    # VS Code workspace file (null if none)
obsidian_vault: true                  # Whether the directory is an Obsidian vault
aliases:                              # Former names (for auditing stale references)
  - RS-ctx-dep-net
  - rs-ctx-dep-net
```

### Dependency edges

Each project may depend on or be depended upon by other projects. Each edge has an
**integration mechanism** that determines which files encode the dependency:

| Mechanism | Files that encode the project name |
|-----------|------------------------------------|
| `editable-pip` | `environment.yml` (pip `-e /path`), `pyproject.toml` (optional deps) |
| `git-submodule` | `.gitmodules` (URL + path), `vendor/` directory |
| `conda-channel` | `environment.yml` (package name) |

```yaml
# Proposed schema for a dependency edge.
dependent: geonexus
dependency: morpha
mechanism: editable-pip
```

---

## Registry Design

### Requirements

1. **Single source of truth.** One file declares all project identities and dependency
   edges. Per-project Markdown files become derived artifacts, generated from the
   registry rather than maintained by hand.

2. **Machine-readable.** TOML or YAML, parseable without custom logic.

3. **Auditable.** The registry records former names (`aliases`) so that a post-rename
   audit can grep for stale references across the entire workspace tree.

4. **Extensible.** New surfaces (e.g., Docker image tags, CI workflow references) can be
   added as optional fields without breaking existing records.

### Proposed location and format

```
projects/dev/registry.toml
```

TOML is chosen over YAML for consistency with `pyproject.toml` and `.ktisma.toml`,
which are already established in the ecosystem.

### Proposed schema

```toml
# projects/dev/registry.toml

[meta]
root = "/Users/eresther/Documents/work"   # Common root for resolving relative paths

# ──────────────────────────────────────────────────────────────────────
# Project identity records
# ──────────────────────────────────────────────────────────────────────

[projects.geonexus]
path = "research/geonexus"
github = "esther-poniatowski/geonexus"
conda_env = "geonexus"
workspace = "geonexus.code-workspace"
obsidian_vault = true
aliases = ["RS-ctx-dep-net", "rs-ctx-dep-net"]

[projects.morpha]
path = "projects/morpha"
github = "esther-poniatowski/morpha"
aliases = []

[projects.meandra]
path = "projects/meandra"
github = "esther-poniatowski/meandra"
aliases = []

[projects.tessara]
path = "projects/tessara"
github = "esther-poniatowski/tessara"
aliases = []

[projects.eikon]
path = "projects/eikon"
github = "esther-poniatowski/eikon"
aliases = []

[projects.scholia]
path = "projects/scholia"
github = "esther-poniatowski/scholia"
aliases = []

[projects.ktisma]
path = "projects/ktisma"
github = "esther-poniatowski/ktisma"
aliases = []

[projects.eutaxis]
path = "projects/eutaxis"
github = "esther-poniatowski/eutaxis"
aliases = []

[projects.architekta]
path = "projects/architekta"
github = "esther-poniatowski/architekta"
conda_env = "architekta-env"
aliases = []

# ... (remaining projects: khimera, loretex, janux, keystone, glossa, stelion, dev, techne)

# ──────────────────────────────────────────────────────────────────────
# Dependency edges
# ──────────────────────────────────────────────────────────────────────

[[dependencies]]
dependent = "geonexus"
dependency = "morpha"
mechanism = "editable-pip"

[[dependencies]]
dependent = "geonexus"
dependency = "tessara"
mechanism = "editable-pip"

[[dependencies]]
dependent = "geonexus"
dependency = "meandra"
mechanism = "editable-pip"

[[dependencies]]
dependent = "geonexus"
dependency = "eikon"
mechanism = "editable-pip"

[[dependencies]]
dependent = "geonexus"
dependency = "scholia"
mechanism = "git-submodule"

[[dependencies]]
dependent = "geonexus"
dependency = "ktisma"
mechanism = "git-submodule"

[[dependencies]]
dependent = "geonexus"
dependency = "eutaxis"
mechanism = "git-submodule"

[[dependencies]]
dependent = "techne"
dependency = "scholia"
mechanism = "git-submodule"

# ... (remaining edges)
```

### Derived artifacts

The following files currently maintained by hand become _generated_ from the registry:

| Current file | Scope | Generated by |
|---|---|---|
| `dev/dependencies.md` | Ecosystem-wide dependency tables and paths | `architekta registry render --dependencies` |
| `dev/projects.md` | Project inventory | `architekta registry render --projects` |
| `dev/dependencies.yml` (by-dependency view) | Single-project dependent list | `stelion workspace sync` (auto-detected from `extra_scan_dirs`) |

This eliminates the consistency burden: after a rename, regenerating these files
from the updated registry produces correct output everywhere.

---

## Rename Pipeline

### Overview

The pipeline consists of ten ordered stages. Each stage is idempotent: running the
pipeline a second time with the same arguments produces no additional changes.

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Validate │ ──▶ │ 2. Filesystem│ ──▶ │ 3. Git remote │ ──▶ │ 4. Workspaces │
└─────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
       │                                                             │
       ▼                                                             ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 5. Conda env │ ──▶ │ 6. Self-refs  │ ──▶ │ 7. Cross-refs │ ──▶ │ 8. Submodules │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                     │
                                                                     ▼
                                          ┌──────────────┐     ┌──────────────┐
                                          │ 9. Registry   │ ──▶ │ 10. Commit    │
                                          └──────────────┘     └──────────────┘
```

### Stage details

#### Stage 1 — Validate

**Purpose.** Ensure the rename can succeed before any mutation occurs.

**Checks:**
- The old name exists in the registry.
- The new name does not collide with any existing project name or alias.
- The target filesystem path does not already exist.
- The target GitHub repository name is available (`gh api`).
- The target conda environment name is not already in use (`conda env list`).
- All dependent and dependency projects are reachable on the filesystem.
- The working trees of all affected repositories are clean (no uncommitted changes).

**Output.** A `RenamePlan` object listing every file, path, and surface that will be
modified. This plan is the input to all subsequent stages and to the `--dry-run` report.

#### Stage 2 — Filesystem

**Purpose.** Rename the local directory.

**Actions:**
- `mv <root>/<old_path> <root>/<new_path>`

**Constraints:**
- Must run before stages 3–8, which need the directory to exist at its new path.
- If the project is an Obsidian vault, the vault name is derived from the directory name
  and updates automatically.

#### Stage 3 — Git remote

**Purpose.** Rename the GitHub repository.

**Actions:**
- `gh api -X PATCH repos/<owner>/<old_name> -f name=<new_name>`
- Update the local git remote URL: `git remote set-url origin <new_url>`

**Constraints:**
- Requires the `gh` CLI to be authenticated with `repo` scope.
- Must run after Stage 2 (needs to `cd` into the renamed directory).

#### Stage 4 — Workspaces

**Purpose.** Update VS Code workspace files that reference the project.

**Actions:**
- Rename the project's own `.code-workspace` file if it embeds the old name.
- In multi-root workspace files (e.g., `dev-repos.code-workspace`), update `folders[].name`
  and `folders[].path` entries.

**Discovery.** The registry declares which workspace files exist. Additionally, grep all
`.code-workspace` files under `<root>` for the old name.

#### Stage 5 — Conda environment

**Purpose.** Rename the conda environment.

**Actions:**
- `conda rename -n <old_env> <new_env> --yes`
- Verify that editable pip installs survived the rename.

**Constraints:**
- Only runs if the project's identity record declares a `conda_env`.
- Must run after Stage 2 (the `environment.yml` at the new path must be accessible).

#### Stage 6 — Self-references

**Purpose.** Replace occurrences of the old name within the project's own files.

**Actions:**
- Collect all text patterns to search: the old name, its aliases, and absolute/relative
  paths embedding the old name.
- Search all tracked files in the repository (excluding binary files, vendored submodules,
  and build artifacts).
- Replace each occurrence with the corresponding new-name variant.

**Pattern mapping:**
```
RS-ctx-dep-net          →  geonexus
rs-ctx-dep-net          →  geonexus
rs_ctx_dep_net          →  geonexus
/research/RS-ctx-dep-net/  →  /research/geonexus/
```

**Constraints:**
- Exclude `vendor/` directories (submodule contents are updated via Stage 8).
- Exclude `.git/` and build artifact directories.
- Flag ambiguous replacements (e.g., substring matches) for manual review.

#### Stage 7 — Cross-references

**Purpose.** Update mentions of the old name in all dependent and dependency projects.

**Actions:**
- From the registry, resolve the set of **affected projects**: all projects that have a
  dependency edge to or from the renamed project.
- In each affected project, search tracked files for the old name patterns (same pattern
  mapping as Stage 6).
- Replace each occurrence.

**Specific files to target per mechanism:**

| Mechanism | Files to update |
|-----------|----------------|
| `editable-pip` | `environment.yml` (absolute pip paths), `pyproject.toml` (optional dep group names) |
| `git-submodule` | `.gitmodules` (URL field) |
| All | `CLAUDE.md`, `docs/`, `README.md`, `.claude/settings.json` |

#### Stage 8 — Submodules

**Purpose.** Update submodule references in projects that vendor the renamed project,
and update submodule references _within_ the renamed project if its submodule sources
were modified in Stage 7.

**Actions:**

_Case A: Another project vendors the renamed project._
- Update `.gitmodules` URL from old remote to new remote.
- `git submodule sync`

_Case B: The renamed project vendors other projects whose files were modified in Stage 7._
- In each affected source repo (e.g., `projects/eutaxis`), commit and push the
  cross-reference changes from Stage 7.
- In the renamed project, `git submodule update --remote <vendor/submodule>` to
  advance the submodule pointer.

#### Stage 9 — Registry

**Purpose.** Update the registry itself.

**Actions:**
- Change the project's key in the `[projects]` table.
- Update the `path`, `github`, `conda_env`, `workspace` fields.
- Append the old name to `aliases`.
- Update all `[[dependencies]]` entries that reference the old name.
- Regenerate derived artifacts (dependencies.yml, projects.yml).

#### Stage 10 — Commit

**Purpose.** Create commits in all affected repositories.

**Actions:**
- In each affected repository, stage the modified files and create a commit with a
  standardized message:
  ```
  chore: rename <old_name> references to <new_name>
  ```
- Optionally push all affected repositories (with `--push` flag).

**Constraints:**
- Stage specific files by name, not `git add -A`.
- Do not push by default — require explicit opt-in.

---

## CLI Interface

### Primary command

```sh
architekta rename <old_name> <new_name> [OPTIONS]
```

### Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Show the full `RenamePlan` without executing any mutations. |
| `--push` | Push commits in all affected repositories after Stage 10. |
| `--skip <stage>` | Skip a specific stage (e.g., `--skip conda` if the project has no conda env). |
| `--registry <path>` | Path to the registry file (default: `dev/registry.toml`). |
| `--no-commit` | Execute all stages but skip the final commit stage. |
| `--verbose` | Print each file modification as it occurs. |

### Auxiliary commands

```sh
# Validate the registry (check all paths exist, no duplicate names/aliases, edges reference
# existing projects).
architekta registry validate

# Regenerate derived artifacts from the registry.
architekta registry render [--dependencies] [--projects] [--dependents <project>]

# Audit the ecosystem for stale references to any alias in the registry.
architekta registry audit
```

The `registry audit` command searches all tracked files in all registered projects for
any string matching an alias. It reports findings without modifying files, serving as a
post-rename verification and as a periodic hygiene check.

---

## Safety Mechanisms

### Dry-run

`--dry-run` executes Stage 1 (Validate) in full and produces a human-readable report of
every planned mutation:

```
Rename: RS-ctx-dep-net → geonexus

Filesystem:
  mv  work/research/RS-ctx-dep-net → work/research/geonexus

GitHub:
  PATCH repos/esther-poniatowski/RS-ctx-dep-net → geonexus

Conda:
  rename env rs-ctx-dep → geonexus

Self-references (23 occurrences in 11 files):
  .claude/CLAUDE.md:13   rs-ctx-dep → geonexus
  .claude/CLAUDE.md:14   rs-ctx-dep → geonexus
  ...

Cross-references (18 occurrences in 9 files across 6 projects):
  projects/dev/dependencies.yml:12    RS-ctx-dep-net → geonexus
  ...

Submodules:
  Push in: projects/eutaxis, projects/ktisma, projects/scholia
  Update in: geonexus (vendor/eutaxis, vendor/ktisma, vendor/scholia)

Commits (8 repositories):
  geonexus, morpha, meandra, tessara, eikon, eutaxis, ktisma, scholia
```

### Pre-mutation validation

Stage 1 must pass entirely before any mutation begins. If any check fails, the pipeline
aborts with a diagnostic message. No partial state is created.

### Clean-tree requirement

All affected repositories must have clean working trees (no uncommitted changes) before
the pipeline starts. This ensures that the commits in Stage 10 contain only rename-related
changes and that no user work is accidentally staged.

### Staged file tracking

A `RenamePlan` object tracks every file modification made by every stage. Stage 10 uses
this manifest to stage exactly the modified files — never `git add -A`.

### Post-rename audit

After completing a rename, the pipeline automatically runs `registry audit` to verify
that no stale references remain. Any residual matches (e.g., in binary files, git history,
or external systems) are reported for manual attention.

---

## Implementation Considerations

### Module structure

```
src/architekta/
├── rename/
│   ├── __init__.py
│   ├── commands.py          # CLI entry point (typer)
│   ├── plan.py              # RenamePlan construction and dry-run rendering
│   ├── stages.py            # Stage implementations (validate, filesystem, git, ...)
│   └── patterns.py          # Name pattern generation and replacement logic
├── registry/
│   ├── __init__.py
│   ├── commands.py          # CLI entry points (validate, render, audit)
│   ├── schema.py            # Registry TOML parsing and validation
│   ├── render.py            # Derived artifact generation (Markdown tables)
│   └── audit.py             # Stale-reference scanner
└── ...
```

### Dependencies on existing architekta modules

- **`github/`**: The `gh` CLI wrapper for repository renaming (Stage 3) and description
  sync extend the existing `github` module.
- **`env/`**: The conda rename logic (Stage 5) extends the existing environment management
  module.

### External tool requirements

| Tool | Stage | Purpose |
|------|-------|---------|
| `gh` | 3 (Git remote) | GitHub API for repository rename |
| `conda` | 5 (Conda env) | Environment rename |
| `git` | 8 (Submodules), 10 (Commit) | Submodule sync, staging, committing, pushing |

### Ordering constraints

The topological order of stages is load-bearing:

- **Filesystem (2) before everything else**: All subsequent stages `cd` into or reference
  the new path.
- **Git remote (3) before Submodules (8)**: Submodule URL updates must use the new remote.
- **Cross-references (7) before Submodules (8)**: Source repo changes must be committed
  and pushed before the vendoring project can update its submodule pointer.
- **Registry (9) after all content changes**: The registry update captures the final state.
- **Commit (10) last**: All file modifications must be complete before committing.

### Pattern generation

Given an old name and its aliases, the pipeline generates a set of search-replace pairs.
Each pair maps a specific textual form of the old identity to the corresponding new form:

```python
def generate_patterns(old: str, new: str, aliases: list[str], old_path: str, new_path: str):
    """Generate (search, replace) pairs for all textual forms of the project identity."""
    patterns = []
    # Direct name forms
    for alias in [old] + aliases:
        patterns.append((alias, new))
    # Absolute path forms
    patterns.append((old_path, new_path))
    # Conda env name (if different from project name)
    # ... additional surface-specific patterns
    return patterns
```

Patterns are applied in longest-first order to avoid partial substring replacements
(e.g., replacing `RS-ctx-dep` before `RS-ctx-dep-net` would produce `geonexus-net`).

---

## Relationship to Existing Registries

### Migration path

The current human-maintained files in `dev/` contain the same information the registry
needs, but in Markdown. The migration path:

1. **Create `registry.toml`** by extracting data from `dev/projects.md`,
   `dev/dependencies.md`, and `dev/names.md`.
2. **Validate** the registry against the actual filesystem and GitHub state.
3. **Regenerate** `dependencies.yml` and `projects.yml`
   from the registry, diff against the originals, and verify equivalence.
4. **Switch maintenance** to the registry as the source of truth. The Markdown files
   become generated artifacts.

### Relationship to eutaxis

Eutaxis manages _within-project governance_ (agent instructions, note templates, audit
protocols). The registry manages _cross-project identity and topology_. These are
complementary: eutaxis consumes project identity from the registry to generate
project-specific governance files.

---

## See Also

- [ADR 2: CLI Commands](../adr/2-cli-commands.md) — architekta command structure, where
  `rename` and `registry` commands integrate
- `dev/dependencies.md` — current human-maintained dependency graph (to be generated)
- `dev/projects.md` — current human-maintained project inventory (to be generated)
- `dev/integration-policy.md` — governance for integration mechanisms (informs the
  `mechanism` field in dependency edges)

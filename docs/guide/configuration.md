# Configuration

## Tool Configuration Files

Architekta ships configuration files for external development tools in `config/tools/`. These files
configure the tools directly -- architekta does not invoke them.

| File                  | Tool             | Purpose                       |
| --------------------- | ---------------- | ----------------------------- |
| `black.toml`          | Black            | Code formatting rules         |
| `mypy.ini`            | MyPy             | Static type checking          |
| `pylintrc.ini`        | Pylint           | Linting rules (main code)     |
| `pylintrc_tests.ini`  | Pylint           | Linting rules (test code)     |
| `pyrightconfig.json`  | Pyright          | Type analysis overrides       |
| `releaserc.toml`      | Semantic Release | Versioning and changelog      |

Spell-checking dictionaries are stored under `config/dictionaries/`:

| File          | Content                |
| ------------- | ---------------------- |
| `project.txt` | Project-specific terms |
| `python.txt`  | Python language terms  |
| `tools.txt`   | Development tool names |

## Environment Variables

| Variable            | Description                                                        | Default | Required |
| ------------------- | ------------------------------------------------------------------ | ------- | -------- |
| `CONDA_DEFAULT_ENV` | Active conda environment name (read by `env install-editable`)     | None    | No       |
| `CONDA_PREFIX`      | Active conda environment path (read by `env install-editable`)     | None    | No       |

## Rename Auto-Detection

The `rename` command auto-detects two values when the corresponding flags are omitted:

- **GitHub owner**: Extracted from the `origin` remote URL of the project repository. If the remote
  is unavailable or does not point to GitHub, pass `--github-owner` explicitly.
- **Conda environment name**: Not auto-detected. When `--conda-env` is omitted, the conda stage is
  skipped. When provided, the pipeline derives the new environment name by replacing the old project
  name within the supplied value.

## Precedence

All architekta behavior is controlled through command-line flags and environment variables. No
configuration file mechanism exists.

Values resolve in the following order (highest priority first):

1. Command-line flags
2. Environment variables (`CONDA_DEFAULT_ENV`, `CONDA_PREFIX`)
3. Auto-detected values (e.g. GitHub owner from git remote)
4. Built-in defaults

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- The options of the command line follow the names shared by the tools of the workspace:
  - `architekta rename --path` becomes `--root`;
  - `architekta rename --workspace` becomes `--workspace-file`;
  - `architekta env install-editable --path` becomes `--package-dir`.

- `architekta rename` and `architekta env install-editable` take their project from `-r`/`--root`,
  else from the environment variable `ARCHITEKTA_ROOT`, else from the current folder.
- `architekta rename` is a plain command: its options may follow the two names, and an unknown
  trailing token is a usage error (status 2), where the command group printed its help and exited
  with status 0 without renaming anything.
- `architekta rename` asks for a confirmation on a terminal; `--yes` answers it, and without a
  terminal and without `--yes` the command stops with status 2. `--dry-run` asks nothing.
- `architekta env install-editable` reads `--package-dir` from the current folder, stops with
  status 2 (formerly 3) on an existing `.pth` file that differs, and leaves an identical one in place
  without `--force`.
- `architekta github sync-descriptions` exits with status 2 (formerly 1) when it finds no project.

### Removed

- The former names `rename --path`, `rename --workspace` and `env install-editable --path`, and the
  module `architekta.renamed_options` that resolved them. The former names are rejected.

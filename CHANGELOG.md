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

### Deprecated

- The former names `rename --path`, `rename --workspace` and `env install-editable --path` remain
  as hidden aliases for one release. Each prints a warning that names the new option, and each will
  be removed in the next release.

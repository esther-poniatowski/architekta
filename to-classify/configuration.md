# Project Configuration

## Global Project Configuration

The central project configuration is specified in a combination of files.

- The development environment in VSCode is configured using the `khimera.code-workspace` file.
- The project metadata and dependencies are specified in the `pyproject.toml` file.

To ensure compatibility between pip and conda, and `environment.yml` is generated from the
`pyproject.toml` file by the `unidep` tool:

```sh
unidep merge --output environment.yml
```

## Development Tools

Helper tools are both installed in the development environment and available via the corresponding
VSCode extensions (if applicable).

### List of Tools

**Linting and formatting**:

- [black](https://black.readthedocs.io/en/stable/)
- [mypy](https://mypy.readthedocs.io/en/stable/)
- [pylint](https://pylint.pycqa.org/en/latest/)
- [pyright](https://pyright.readthedocs.io/en/latest/)
- [cspell](https://pypi.org/project/cspell/)
- Additional VSCode formatting options: `files.trimTrailingWhitespace`, `files.insertFinalNewline`,
  `files.trimFinalNewlines`. Those apply to all files, not only Python files.

**Testing**:

- [pytest](https://docs.pytest.org/en/latest/)
- [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/)
- [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/)

**Documentation**:

- [Sphinx](https://www.sphinx-doc.org/en/master/)
- [Sphinx-Autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)

### Configuration

Dictionaries for Cspell are stored in the `config/dictionaries` directory. Each dictionary is a TXT
file named according to a topic (e.g. `python.txt`, `project.txt`, etc.). The dictionaries and their
aliases are passed to the Cspell extension via the `cSpell.customDictionaries` setting in the
`.code-workspace` file.

Other tools are configured in the directory `config/tools`. Each tool is associated with a specific
configuration file, named according to the tool name. Those configurations are passed to the VSCode
extensions for the corresponding tools via the `code-workspace` file in the top-level directory of
the project. This is done by:

- Specifying an additional argument to the `args` field of the corresponding tool, which corresponds
  to the standard argument used by the tool to specify a configuration file.
- Specifying the path to the configuration file.

Examples:

```json
{
    "black-formatter.args": ["--config", "./config/tools/black.toml"],
    "mypy-type-checker.args": ["--config-file=./config/tools/mypy.ini"],
}
```

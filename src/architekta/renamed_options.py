"""Former names of renamed command-line options.

A renamed option keeps its former name for one release, as a hidden option. The commands pass the
value of that hidden option to :func:`resolve_renamed_option`, which warns and returns the value
to use.
"""

from __future__ import annotations

from typing import TypeVar

import typer
from click.core import ParameterSource

from architekta.diagnostics import DiagnosticEntry, DiagnosticLevel, emit

T = TypeVar("T")


def resolve_renamed_option(
    ctx: typer.Context, param_name: str, current_value: T, former_flag: str, former_value: T | None,
) -> T:
    """Return the value of a renamed option, accepting its former name with a warning.

    Parameters
    ----------
    ctx : typer.Context
        Context of the command that declares both options.
    param_name : str
        Name of the parameter of the current option, such as ``"root"``.
    current_value : T
        Value of the current option, as the command received it.
    former_flag : str
        Former name of the option, such as ``"--path"``.
    former_value : T | None
        Value given under the former name, or ``None`` when it is absent.

    Returns
    -------
    T
        The value given under the former name when present, else the value of the current option.

    Raises
    ------
    typer.BadParameter
        If the current option and its former name are both given.
    """
    if former_value is None:
        return current_value
    flag = next(param.opts[0] for param in ctx.command.params if param.name == param_name)
    if ctx.get_parameter_source(param_name) is not ParameterSource.DEFAULT:
        raise typer.BadParameter(f"{former_flag} is the former name of {flag}; give only {flag}.")
    emit(DiagnosticEntry(
        DiagnosticLevel.WARN, "", f"{former_flag} is deprecated and will be removed; use {flag}.",
    ))
    return former_value

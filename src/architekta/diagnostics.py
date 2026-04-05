"""Structured diagnostic output for CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import typer


class DiagnosticLevel(Enum):
    OK = "OK"
    SKIP = "SKIP"
    WARN = "WARN"
    ERROR = "ERR"
    DRY = "DRY"
    SET = "SET"


@dataclass(frozen=True)
class DiagnosticEntry:
    level: DiagnosticLevel
    context: str
    message: str


def emit(entry: DiagnosticEntry) -> None:
    tag = f"[{entry.level.value}]"
    prefix = f"{tag:<7} {entry.context}: " if entry.context else f"{tag:<7} "
    is_error = entry.level in (DiagnosticLevel.ERROR, DiagnosticLevel.WARN)
    typer.echo(f"{prefix}{entry.message}", err=is_error)

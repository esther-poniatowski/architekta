"""Shared infrastructure utilities."""

from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class CommandResult:
    """Structured subprocess result for infrastructure callers."""

    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_command(args: list[str]) -> CommandResult:
    """Run a subprocess command and preserve full diagnostics for the caller."""
    result = subprocess.run(args, capture_output=True, text=True)
    return CommandResult(
        args=tuple(args),
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )

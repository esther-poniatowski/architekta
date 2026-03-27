"""Shared infrastructure utilities."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


class GitError(Exception):
    """Raised when a git operation fails at the infrastructure layer."""


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


def run_command(args: list[str], *, cwd: Path | None = None) -> CommandResult:
    """Run a subprocess command and preserve full diagnostics for the caller."""
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=str(cwd) if cwd else None
    )
    return CommandResult(
        args=tuple(args),
        returncode=result.returncode,
        stdout=result.stdout.strip(),
        stderr=result.stderr.strip(),
    )


def list_tracked_files(repo_path: Path) -> list[Path]:
    """Return all files tracked by git in a repository, excluding ignored files.

    Raises
    ------
    GitError
        If the git command fails (e.g., not a git repo, git unavailable, bad path).
        Callers that want to tolerate unavailable repos must catch this explicitly.
    """
    result = run_command(
        ["git", "-C", str(repo_path), "ls-files", "--cached", "--exclude-standard"]
    )
    if not result.ok:
        detail = result.stderr or result.stdout or "git ls-files failed"
        raise GitError(
            f"Cannot list tracked files in {repo_path}: {detail} "
            f"(exit {result.returncode})"
        )
    return [
        repo_path / f
        for f in result.stdout.splitlines()
        if f.strip()
    ]


def is_text_file(path: Path) -> bool:
    """Return True if the file can be decoded as UTF-8 text."""
    try:
        path.read_bytes().decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False

"""Shared infrastructure utilities."""

import subprocess


def run_command(
    args: list[str],
    error_cls: type[Exception],
    context: str,
) -> str:
    """Run a subprocess command and return stdout, or raise on failure."""
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise error_cls(f"{context}: {result.stderr.strip()}")
    return result.stdout.strip()

"""Utility functions for GitHub repository metadata operations."""

import re
import subprocess
from pathlib import Path

from architekta.github.exceptions import RemoteNotFound, DescriptionNotFound, GhCliError


def extract_readme_description(project_dir: Path) -> str:
    """Extract the first descriptive sentence from a project README.

    Skips the title heading, badge lines, horizontal rules, HTML comments,
    and blank lines, returning the first line of plain prose.
    """
    readme = project_dir / "README.md"
    if not readme.exists():
        raise DescriptionNotFound(f"No README.md in {project_dir}")
    in_comment = False
    for line in readme.read_text().splitlines():
        stripped = line.strip()
        if "<!--" in stripped:
            in_comment = True
        if in_comment:
            if "-->" in stripped:
                in_comment = False
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("[!["):
            continue
        if stripped == "---":
            continue
        return stripped
    raise DescriptionNotFound(f"No description found in {readme}")


def get_github_remote(project_dir: Path) -> tuple[str, str]:
    """Parse the origin remote URL to extract the GitHub owner and repo name."""
    result = subprocess.run(
        ["git", "-C", str(project_dir), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RemoteNotFound(f"No git remote 'origin' in {project_dir}")
    url = result.stdout.strip()
    match = re.search(r"github\.com[:/](.+?)/(.+?)(?:\.git)?$", url)
    if not match:
        raise RemoteNotFound(f"Cannot parse GitHub owner/repo from remote URL: {url}")
    return match.group(1), match.group(2)


def get_current_description(owner: str, repo: str) -> str:
    """Fetch the current GitHub repository description via the gh CLI."""
    result = subprocess.run(
        ["gh", "repo", "view", f"{owner}/{repo}", "--json", "description", "-q", ".description"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GhCliError(f"Failed to query {owner}/{repo}: {result.stderr.strip()}")
    return result.stdout.strip()


def set_description(owner: str, repo: str, description: str) -> None:
    """Update the GitHub repository description via the gh CLI."""
    result = subprocess.run(
        ["gh", "repo", "edit", f"{owner}/{repo}", "--description", description],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GhCliError(f"Failed to update {owner}/{repo}: {result.stderr.strip()}")


def get_pyproject_description(project_dir: Path) -> str | None:
    """Read the description field from pyproject.toml, or None if absent."""
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.exists():
        return None
    text = pyproject.read_text()
    match = re.search(r'^description\s*=\s*"([^"]*)"', text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def set_pyproject_description(project_dir: Path, description: str) -> None:
    """Update the description field in pyproject.toml in place."""
    pyproject = project_dir / "pyproject.toml"
    text = pyproject.read_text()
    new_text, count = re.subn(
        r'^(description\s*=\s*)"[^"]*"',
        rf'\1"{description}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        raise DescriptionNotFound(f"No description field in {pyproject}")
    pyproject.write_text(new_text)

"""Name pattern generation and text replacement for rename operations."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternPair:
    """A single search-replace pair used during a rename."""

    search: str
    replace: str


def generate_patterns(
    old_name: str,
    new_name: str,
    old_aliases: list[str],
    old_abs_path: str,
    new_abs_path: str,
    old_conda_env: str | None = None,
    new_conda_env: str | None = None,
) -> tuple[PatternPair, ...]:
    """Generate ordered (search, replace) pattern pairs for a project rename.

    Patterns are sorted longest-first so that more specific forms (e.g., full
    path, conda env name with suffix) are replaced before shorter ones (e.g.,
    the bare project name), preventing partial-match corruption.

    Parameters
    ----------
    old_name:
        The canonical old project name.
    new_name:
        The canonical new project name.
    old_aliases:
        Former names that should also be replaced (from the registry aliases
        list). Each alias maps to new_name.
    old_abs_path, new_abs_path:
        Absolute filesystem paths to the project directory.
    old_conda_env, new_conda_env:
        Conda environment names, if the project declares one. Only added when
        the conda env name differs from the project name (otherwise the direct
        name pattern already covers it).
    """
    candidates: list[PatternPair] = []

    # Longest patterns first by construction, then sort for safety.
    candidates.append(PatternPair(search=old_abs_path, replace=new_abs_path))

    # Conda env name when it is distinct from all alias forms.
    alias_set = {old_name} | set(old_aliases)
    if old_conda_env and new_conda_env and old_conda_env not in alias_set:
        candidates.append(PatternPair(search=old_conda_env, replace=new_conda_env))

    # Direct name forms (canonical name + every alias).
    for name in [old_name] + old_aliases:
        if name:
            candidates.append(PatternPair(search=name, replace=new_name))

    # Deduplicate while preserving first-occurrence ordering, then sort.
    seen: set[PatternPair] = set()
    unique: list[PatternPair] = []
    for pair in candidates:
        if pair not in seen:
            seen.add(pair)
            unique.append(pair)

    return tuple(sorted(unique, key=lambda p: len(p.search), reverse=True))


def apply_patterns_to_text(
    text: str, patterns: tuple[PatternPair, ...]
) -> tuple[str, bool]:
    """Apply all patterns to a text string and indicate whether it changed.

    Patterns are applied in the order given (caller is responsible for
    longest-first ordering via ``generate_patterns``).
    """
    original = text
    for pair in patterns:
        text = text.replace(pair.search, pair.replace)
    return text, text != original

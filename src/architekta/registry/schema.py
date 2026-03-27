"""Registry domain models and TOML persistence."""

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import tomlkit
from tomlkit.exceptions import TOMLKitError

from architekta.registry.exceptions import (
    InvalidRegistry,
    ProjectNotFound,
    RegistryNotFound,
)


# ── Constants ──────────────────────────────────────────────────────────────────

KNOWN_MECHANISMS: frozenset[str] = frozenset(
    {"editable-pip", "git-submodule", "conda-channel"}
)


# ── Value objects ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GithubSlug:
    """A validated GitHub owner/repo identifier."""

    owner: str
    repo: str

    @classmethod
    def parse(cls, raw: str) -> "GithubSlug":
        """Parse an 'owner/repo' string.

        Raises
        ------
        ValueError
            If the string is not exactly 'owner/repo' with non-empty components.
        """
        parts = raw.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"GitHub identifier must be 'owner/repo', got: {raw!r}"
            )
        return cls(owner=parts[0], repo=parts[1])

    def __str__(self) -> str:
        return f"{self.owner}/{self.repo}"


# ── Domain models ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProjectRecord:
    """Identity record for a single project in the ecosystem."""

    name: str
    path: Path
    github: GithubSlug
    conda_env: str | None = None
    workspace: str | None = None
    obsidian_vault: bool = False
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencyEdge:
    """A directed dependency relationship between two projects."""

    dependent: str
    dependency: str
    mechanism: str  # one of KNOWN_MECHANISMS


@dataclass
class ProjectRegistry:
    """Registry of all project identities and dependency edges.

    Treated as immutable after construction. Provides query methods for
    navigating the dependency graph.
    """

    root: Path
    projects: dict[str, ProjectRecord]
    dependencies: tuple[DependencyEdge, ...]
    source: Path

    def get_project(self, name: str) -> ProjectRecord:
        if name not in self.projects:
            raise ProjectNotFound(f"Project {name!r} not found in registry")
        return self.projects[name]

    def has_project(self, name: str) -> bool:
        return name in self.projects

    def dependents_of(self, name: str) -> list[str]:
        """Projects that directly depend on the given project."""
        return [e.dependent for e in self.dependencies if e.dependency == name]

    def dependencies_of(self, name: str) -> list[str]:
        """Projects that the given project directly depends on."""
        return [e.dependency for e in self.dependencies if e.dependent == name]

    def affected_projects(self, name: str) -> set[str]:
        """All projects with any dependency edge to or from the given project."""
        return (
            {e.dependent for e in self.dependencies if e.dependency == name}
            | {e.dependency for e in self.dependencies if e.dependent == name}
        )

    def edges_involving(self, name: str) -> list[DependencyEdge]:
        """All dependency edges that reference the given project."""
        return [
            e
            for e in self.dependencies
            if e.dependent == name or e.dependency == name
        ]

    def project_path(self, name: str) -> Path:
        """Absolute path to the project directory."""
        return self.root / self.projects[name].path

    def all_names_and_aliases(self) -> dict[str, str]:
        """Map every known name and alias to its canonical project name."""
        result: dict[str, str] = {}
        for canonical, record in self.projects.items():
            result[canonical] = canonical
            for alias in record.aliases:
                result[alias] = canonical
        return result


# ── TOML loading ───────────────────────────────────────────────────────────────


def load_registry(path: Path) -> ProjectRegistry:
    """Parse registry.toml and return the domain model.

    Raises
    ------
    RegistryNotFound
        If the file does not exist or cannot be read.
    InvalidRegistry
        If the file structure does not match the expected schema, including
        unknown mechanism values in dependency edges.
    """
    if not path.exists():
        raise RegistryNotFound(f"Registry file not found: {path}")
    try:
        data = tomlkit.parse(path.read_text())
    except (OSError, TOMLKitError) as exc:
        raise RegistryNotFound(f"Cannot read registry at {path}: {exc}") from exc

    try:
        meta = data.get("meta", {})
        root_str = meta.get("root")
        root = Path(root_str) if root_str else path.parent.parent

        projects: dict[str, ProjectRecord] = {}
        for name, fields in data.get("projects", {}).items():
            raw_github = str(fields["github"])
            try:
                github = GithubSlug.parse(raw_github)
            except ValueError as exc:
                raise InvalidRegistry(
                    f"Project {name!r}: invalid github field: {exc}"
                ) from exc

            projects[name] = ProjectRecord(
                name=name,
                path=Path(str(fields["path"])),
                github=github,
                conda_env=str(fields["conda_env"]) if fields.get("conda_env") else None,
                workspace=str(fields["workspace"]) if fields.get("workspace") else None,
                obsidian_vault=bool(fields.get("obsidian_vault", False)),
                aliases=tuple(str(a) for a in fields.get("aliases", [])),
            )

        dependencies: list[DependencyEdge] = []
        for edge in data.get("dependencies", []):
            mechanism = str(edge["mechanism"])
            if mechanism not in KNOWN_MECHANISMS:
                raise InvalidRegistry(
                    f"Dependency edge {edge['dependent']!r} → {edge['dependency']!r}: "
                    f"unknown mechanism {mechanism!r}. "
                    f"Known values: {sorted(KNOWN_MECHANISMS)}"
                )
            dependencies.append(
                DependencyEdge(
                    dependent=str(edge["dependent"]),
                    dependency=str(edge["dependency"]),
                    mechanism=mechanism,
                )
            )

    except (KeyError, TypeError, AttributeError) as exc:
        raise InvalidRegistry(f"Invalid registry format in {path}: {exc}") from exc

    return ProjectRegistry(
        root=root,
        projects=projects,
        dependencies=tuple(dependencies),
        source=path,
    )


# ── TOML mutation ──────────────────────────────────────────────────────────────


def update_registry_for_rename(
    content: str,
    old_name: str,
    new_name: str,
    new_path: str,
    new_github: str,
    new_conda_env: str | None,
    new_workspace: str | None,
) -> str:
    """Compute updated registry TOML content reflecting a project rename.

    This is a pure transformation: it takes the current TOML content as a string
    and returns the updated content as a string. All file I/O is the caller's
    responsibility.

    Strategy: rename the section header via string replacement (preserving
    position in the file), then update field values via tomlkit round-trip
    editing (preserving comments and formatting).

    Raises
    ------
    ProjectNotFound
        If old_name is not present in the content.
    InvalidRegistry
        If the content cannot be parsed after the key rename.
    """
    old_header = f"[projects.{old_name}]"
    new_header = f"[projects.{new_name}]"
    if old_header not in content:
        raise ProjectNotFound(f"Project key {old_name!r} not found in registry content")
    content = content.replace(old_header, new_header)

    try:
        doc = tomlkit.parse(content)
    except TOMLKitError as exc:
        raise InvalidRegistry(f"Cannot parse registry after key rename: {exc}") from exc

    record = doc["projects"][new_name]  # type: ignore[index]
    record["path"] = new_path  # type: ignore[index]
    record["github"] = new_github  # type: ignore[index]

    if new_conda_env is not None:
        record["conda_env"] = new_conda_env  # type: ignore[index]
    if new_workspace is not None:
        record["workspace"] = new_workspace  # type: ignore[index]

    # Append the old canonical name to the aliases list.
    existing_aliases = list(record.get("aliases", []))  # type: ignore[union-attr]
    if old_name not in existing_aliases:
        existing_aliases.insert(0, old_name)
    record["aliases"] = existing_aliases  # type: ignore[index]

    # Update all dependency edges that reference the old name.
    for edge in doc.get("dependencies", []):
        if edge.get("dependent") == old_name:
            edge["dependent"] = new_name
        if edge.get("dependency") == old_name:
            edge["dependency"] = new_name

    return tomlkit.dumps(doc)

"""Registry validation logic."""

from dataclasses import dataclass

from architekta.registry.schema import ProjectRegistry


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation problem found in the registry."""

    severity: str  # "error" | "warning"
    message: str


@dataclass(frozen=True)
class ValidationResult:
    """Aggregated result of registry validation."""

    issues: tuple[ValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "error")

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity == "warning")


def validate_registry(
    registry: ProjectRegistry, *, check_paths: bool = True
) -> ValidationResult:
    """Check a registry for structural consistency.

    Parameters
    ----------
    registry:
        The loaded registry to validate.
    check_paths:
        When True, verify that each declared project path exists on disk.
    """
    issues: list[ValidationIssue] = []

    _check_name_collisions(registry, issues)
    _check_dependency_references(registry, issues)
    if check_paths:
        _check_project_paths(registry, issues)

    return ValidationResult(issues=tuple(issues))


def _check_name_collisions(
    registry: ProjectRegistry, issues: list[ValidationIssue]
) -> None:
    """Detect any alias that shadows another project's canonical name or alias."""
    canonical_names = set(registry.projects.keys())
    seen: dict[str, str] = {}  # name/alias → first canonical owner

    for canonical in canonical_names:
        record = registry.projects[canonical]
        all_names = [canonical] + list(record.aliases)
        for name in all_names:
            if name in seen:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Name {name!r} is shared by projects "
                            f"{seen[name]!r} and {canonical!r}"
                        ),
                    )
                )
            else:
                seen[name] = canonical


def _check_dependency_references(
    registry: ProjectRegistry, issues: list[ValidationIssue]
) -> None:
    """Ensure every dependency edge references existing project names."""
    for edge in registry.dependencies:
        for role, name in (("dependent", edge.dependent), ("dependency", edge.dependency)):
            if not registry.has_project(name):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        message=(
                            f"Dependency edge {edge.dependent!r} → {edge.dependency!r} "
                            f"references unknown project {name!r} as {role}"
                        ),
                    )
                )

        from architekta.registry.schema import KNOWN_MECHANISMS
        if edge.mechanism not in KNOWN_MECHANISMS:
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=(
                        f"Dependency edge {edge.dependent!r} → {edge.dependency!r} "
                        f"uses unknown mechanism {edge.mechanism!r}. "
                        f"Known values: {sorted(KNOWN_MECHANISMS)}"
                    ),
                )
            )


def _check_project_paths(
    registry: ProjectRegistry, issues: list[ValidationIssue]
) -> None:
    """Verify that each project's declared path exists on the filesystem."""
    for name in registry.projects:
        path = registry.project_path(name)
        if not path.exists():
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Project {name!r}: path does not exist: {path}",
                )
            )
        elif not path.is_dir():
            issues.append(
                ValidationIssue(
                    severity="error",
                    message=f"Project {name!r}: path is not a directory: {path}",
                )
            )

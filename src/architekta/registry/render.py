"""Generation of derived Markdown artifacts from the registry."""

from architekta.registry.schema import ProjectRegistry


def render_projects_markdown(registry: ProjectRegistry) -> str:
    """Render a Markdown table of all projects."""
    header = "| Project | Path | GitHub | Conda env | Workspace |\n"
    separator = "|---------|------|--------|-----------|-----------|\n"

    rows = []
    for name, record in sorted(registry.projects.items()):
        conda = record.conda_env or "—"
        workspace = record.workspace or "—"
        rows.append(
            f"| {name} | `{record.path}` "
            f"| [{record.github}](https://github.com/{record.github}) "
            f"| {conda} | {workspace} |"
        )

    return header + separator + "\n".join(rows) + "\n"


def render_dependencies_markdown(registry: ProjectRegistry) -> str:
    """Render a Markdown table of all dependency edges."""
    header = "| Dependent | Dependency | Mechanism |\n"
    separator = "|-----------|------------|-----------|\n"

    rows = []
    for edge in sorted(
        registry.dependencies, key=lambda e: (e.dependent, e.dependency)
    ):
        rows.append(
            f"| {edge.dependent} | {edge.dependency} | `{edge.mechanism}` |"
        )

    return header + separator + "\n".join(rows) + "\n"


def render_dependents_yaml(registry: ProjectRegistry, project_name: str) -> str:
    """Render a YAML list of projects that depend on the given project."""
    dependents = sorted(registry.dependents_of(project_name))
    if not dependents:
        return f"# No projects depend on {project_name}\n{project_name}: []\n"

    lines = [f"{project_name}:"]
    for dep in dependents:
        lines.append(f"  - {dep}")
    return "\n".join(lines) + "\n"

"""Dry-run rendering for pipeline reports."""

from __future__ import annotations

from architekta.rename.models import PipelineReport


def render_dry_run(report: PipelineReport) -> str:
    """Format a pipeline report as a human-readable dry-run preview."""
    lines: list[str] = [
        f"Rename: {report.old_name} \u2192 {report.new_name}",
        "",
    ]
    for stage in report.stages:
        if stage.skipped:
            lines.append(f"[{stage.name}] skipped: {stage.skip_reason}")
            continue
        if stage.error:
            lines.append(f"[{stage.name}] ERROR: {stage.error}")
            continue

        section_lines: list[str] = []
        for rename in stage.path_renames:
            section_lines.append(f"  mv  {rename.old} \u2192 {rename.new}")
        if stage.file_edits:
            files_changed = len({e.path for e in stage.file_edits})
            section_lines.append(
                f"  {len(stage.file_edits)} occurrence(s) in {files_changed} file(s):"
            )
            for edit in stage.file_edits:
                section_lines.append(
                    f"    {edit.path}:{edit.line_number}  "
                    f"{edit.old_line!r} \u2192 {edit.new_line!r}"
                )
        for cmd in stage.commands:
            section_lines.append(f"  {cmd.description}: {' '.join(str(a) for a in cmd.args)}")
        if stage.description:
            section_lines.append(f"  {stage.description}")

        if section_lines:
            lines.append(f"[{stage.name}]")
            lines.extend(section_lines)
        else:
            lines.append(f"[{stage.name}] no changes")

    return "\n".join(lines) + "\n"

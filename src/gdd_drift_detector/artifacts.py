"""Write dual Graph artifact and Drift report under the project root."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Finding, ScanResult
from .narrative import next_actions, priority_findings


def write_artifacts(root: Path, result: ScanResult) -> None:
    (root / "drift.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if result.summary.coverage_percent is None:
        coverage = "N/A"
    else:
        coverage = f"{result.summary.coverage_percent:.0f}%"
    if result.state == "PARTIAL":
        coverage += "; qualified by partial scan warnings"
    lines = [
        "# Drift report",
        "",
        f"State: {result.state}",
        f"Coverage: {result.summary.matched}/{result.summary.total} ({coverage})",
        "",
    ]
    priority = priority_findings(result)
    if priority:
        lines.extend(["## Priority findings", ""])
        for finding in priority:
            lines.append(f"- {finding.status}: {_finding_label(finding)}")
        lines.append("")
    lines.extend(["## Findings", ""])
    for finding in result.findings:
        lines.append(f"- {finding.status}: {_finding_label(finding)}")
        if finding.evidence:
            evidence = finding.evidence
            if evidence.gdd_path:
                lines.append(
                    f"  - GDD evidence: {evidence.gdd_path}:{evidence.gdd_line}"
                )
            if evidence.code_path:
                lines.append(
                    f"  - Code evidence: {evidence.code_path}:{evidence.code_line}"
                )
            if evidence.code_symbol_path:
                lines.append(f"  - Symbol: `{evidence.code_symbol_path}`")
            if evidence.containment_path:
                lines.append(
                    "  - Containment: " + " -> ".join(evidence.containment_path)
                )
            if evidence.gdd_excerpt:
                lines.append(f"  - GDD excerpt: `{evidence.gdd_excerpt}`")
            if evidence.code_excerpt:
                lines.append(f"  - Code excerpt: `{evidence.code_excerpt}`")
    if result.candidates:
        lines.extend(["", "## Candidates", ""])
        for candidate in result.candidates:
            lines.append(
                f"- CANDIDATE: {candidate.name} "
                f"({candidate.path}:{candidate.line}) — {candidate.guidance}"
            )
    if result.advisories:
        lines.extend(["", "## Advisories", ""])
        for advisory in result.advisories:
            lines.extend(
                [
                    f"- {advisory.path} [{advisory.code}]: {advisory.reason}",
                    f"  - Impact: {advisory.impact}",
                    f"  - Next action: {advisory.next_action}",
                ]
            )
    if result.warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in result.warnings:
            lines.extend(
                [
                    f"- {warning.path} [{warning.code}]: {warning.reason}",
                    f"  - Affected scope: {warning.impact}",
                    f"  - Next action: {warning.next_action}",
                ]
            )
    lines.extend(["", "## Next actions", ""])
    for action in next_actions(result):
        lines.append(f"- {action}")
    (root / "drift_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _finding_label(finding: Finding) -> str:
    if finding.tracked_entity:
        label = finding.tracked_entity.name
        evidence = f"{finding.tracked_entity.path}:{finding.tracked_entity.line}"
        if finding.code_entity:
            evidence += f"; code {finding.code_entity.path}:{finding.code_entity.line}"
        return f"{label} ({evidence})"
    if finding.code_entity:
        return (
            f"{finding.code_entity.name} "
            f"(code {finding.code_entity.path}:{finding.code_entity.line})"
        )
    return "Unknown (no evidence)"

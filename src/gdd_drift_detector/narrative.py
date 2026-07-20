"""Ownership and next-action narrative shared by Graph artifact and Drift report."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Finding, ScanResult

_PRIORITY_STATUSES = frozenset({"MISSING", "RENAMED?", "ORPHANED"})


def priority_findings(result: ScanResult) -> tuple[Finding, ...]:
    """Findings that belong in the priority section of both report surfaces."""

    return tuple(
        finding for finding in result.findings if finding.status in _PRIORITY_STATUSES
    )


def next_actions(result: ScanResult) -> list[str]:
    """Canonical ownership / remediation lines for JSON summary and Markdown."""

    actions: list[str] = []
    if result.warnings:
        actions.append("Resolve every warning, then rerun the local scan.")
    if result.advisories:
        actions.append(
            "Review scan advisories: put [entity: type] before each intended "
            "name, then rerun the local scan."
        )
    if not result.tracked_entities:
        actions.append(
            "Coverage is N/A: not marked yet; add "
            "[entity: type] before intended names, then rerun the local scan."
        )
    if any(finding.status == "MISSING" for finding in result.findings):
        actions.append(
            "MISSING ownership: implement or unmark/remove each tracked entity."
        )
    if any(finding.status == "RENAMED?" for finding in result.findings):
        actions.append(
            "RENAMED? ownership: add accepted_mappings or reject each candidate; "
            "do not count it as matched without accepted_mappings."
        )
    if any(finding.status == "ORPHANED" for finding in result.findings):
        actions.append(
            "ORPHANED ownership: track, exclude in drift.toml, or remove each "
            "top-level symbol."
        )
    if any(finding.status == "PLANNED" for finding in result.findings):
        actions.append(
            "PLANNED ownership: keep entity outside the current coverage slice "
            "until it is ready."
        )
    if not actions:
        actions.append("Review drift_report.md for full scan evidence.")
    return actions

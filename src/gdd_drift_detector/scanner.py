"""Detector engine orchestration: local scan façade over named internal seams."""

from __future__ import annotations

import time
from pathlib import Path

from .artifacts import write_artifacts
from .discovery import (
    make_warning,
    read_project_config,
    resolve_scan_config,
    validate_project,
)
from .gdd_parse import parse_gdd_sources
from .gdscript_parse import parse_gdscript
from .matching import findings
from .models import (
    CodeEntity,
    Relationship,
    ScanConfig,
    ScanFailure,
    ScanResult,
    ScanSummary,
    ScanWarning,
)
from .names import normalize_name

__all__ = ["normalize_name", "scan"]


def scan(project_root: Path, config: ScanConfig | None = None) -> ScanResult:
    """Scan a Godot project and write canonical root artifacts."""

    started = time.perf_counter()
    root = project_root.resolve()
    validate_project(root)
    config = config or ScanConfig()
    project_config = read_project_config(root)
    resolved_config, config_warnings = resolve_scan_config(root, config, project_config)
    tracked, candidates, gdd_warnings, gdd_advisories = parse_gdd_sources(
        root, resolved_config.gdd_paths
    )
    parsed_code: list[tuple[list[CodeEntity], list[Relationship]]] = []
    source_warnings: list[ScanWarning] = []
    for path in resolved_config.source_paths:
        try:
            parsed_code.append(parse_gdscript(root, path))
        except ScanFailure as error:
            if error.code not in {"UNSUPPORTED_SOURCE", "UNREADABLE_INPUT"}:
                raise
            source_warnings.append(
                make_warning(
                    error.path or root / path,
                    error.code,
                    error.message,
                    "Implementation entities from this file are excluded; matches "
                    "and orphan findings may be incomplete.",
                    "Fix GDScript syntax, then rerun the local scan.",
                )
            )
    code = tuple(entity for entities, _ in parsed_code for entity in entities)
    relationships = tuple(
        relationship
        for _, file_relationships in parsed_code
        for relationship in file_relationships
    )
    by_name: dict[str, tuple[CodeEntity, ...]] = {}
    for entity in code:
        by_name[entity.normalized_name] = (
            *by_name.get(entity.normalized_name, ()),
            entity,
        )
    mappings = project_config.accepted_mappings or {}
    matched_findings = findings(root, tracked, code, by_name, mappings)
    warnings = (*config_warnings, *gdd_warnings, *source_warnings)
    active_findings = tuple(
        finding
        for finding in matched_findings
        if finding.tracked_entity is not None and finding.status != "PLANNED"
    )
    matched = sum(finding.status == "MATCHED" for finding in active_findings)
    total = len(active_findings)
    summary = ScanSummary(
        matched=matched,
        total=total,
        coverage_percent=(matched / total * 100) if total else None,
    )
    result = ScanResult(
        schema_version="1.3",
        project_root=str(root),
        tracked_entities=tracked,
        code_entities=code,
        findings=matched_findings,
        candidates=candidates,
        relationships=relationships,
        state="PARTIAL" if warnings else "COMPLETE",
        warnings=warnings,
        advisories=gdd_advisories,
        summary=summary,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
    write_artifacts(root, result)
    return result

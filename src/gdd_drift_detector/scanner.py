"""Offline implementation of the local detector seam."""

from __future__ import annotations

import fnmatch
import json
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import tomli
from tree_sitter import Node, Parser
from tree_sitter_language_pack import get_language

from .models import (
    CandidateEntity,
    CodeEntity,
    Finding,
    ScanConfig,
    ScanFailure,
    ScanResult,
    ScanSummary,
    TrackedEntity,
)

_MARKER = re.compile(r"\[entity:\s*(?P<type>[^\]]+)\]\s*(?P<tail>.*)$", re.IGNORECASE)
_PLANNED = re.compile(r"\[planned\]", re.IGNORECASE)
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(?P<name>.+?)\s*#*\s*$")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?P<name>.+?)\s*$")
_GODOT_4_PROJECT = re.compile(r"^\s*config_version\s*=\s*5\s*$", re.MULTILINE)
_DEFAULT_GDD_PATTERNS = (
    "GDD.md",
    "design.md",
    "docs/gdd/**/*.md",
    "docs/design/**/*.md",
)


@dataclass(frozen=True)
class _ProjectConfig:
    gdd_patterns: tuple[str, ...] | None = None
    source_patterns: tuple[str, ...] | None = None
    exclusions: tuple[str, ...] = ()
    accepted_mappings: dict[str, str] | None = None


def normalize_name(value: str) -> str:
    """Normalize names for deterministic exact matching."""

    return re.sub(r"[^a-z0-9]+", "", value.lower())


def scan(project_root: Path, config: ScanConfig | None = None) -> ScanResult:
    """Scan a Godot project and write canonical root artifacts."""

    started = time.perf_counter()
    root = project_root.resolve()
    _validate_project(root)
    config = config or ScanConfig()
    project_config = _read_project_config(root)
    resolved_config = _resolve_scan_config(root, config, project_config)
    tracked, candidates = _parse_gdd_sources(root, resolved_config.gdd_paths)
    code = tuple(
        entity
        for path in resolved_config.source_paths
        for entity in _parse_gdscript(root, path)
    )
    by_name = {entity.normalized_name: entity for entity in code}
    mappings = project_config.accepted_mappings or {}
    findings = tuple(_find_entity(entity, by_name, mappings) for entity in tracked)
    active_findings = tuple(
        finding for finding in findings if finding.status != "PLANNED"
    )
    matched = sum(finding.status == "MATCHED" for finding in active_findings)
    total = len(active_findings)
    summary = ScanSummary(
        matched=matched,
        total=total,
        coverage_percent=(matched / total * 100) if total else None,
    )
    result = ScanResult(
        schema_version="1.1",
        project_root=str(root),
        tracked_entities=tracked,
        code_entities=code,
        findings=findings,
        candidates=candidates,
        summary=summary,
        duration_ms=int((time.perf_counter() - started) * 1000),
    )
    _write_artifacts(root, result)
    return result


def _validate_project(root: Path) -> None:
    project_file = root / "project.godot"
    if not root.is_dir() or not project_file.is_file():
        raise ScanFailure("INVALID_PROJECT", "project.godot is required", root)
    try:
        project_contents = project_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise ScanFailure(
            "INVALID_PROJECT", "project.godot must be readable", project_file
        ) from error
    if not _GODOT_4_PROJECT.search(project_contents):
        raise ScanFailure("INVALID_PROJECT", "Godot 4 project.godot is required", root)


def _read_project_config(root: Path) -> _ProjectConfig:
    path = root / "drift.toml"
    if not path.exists():
        return _ProjectConfig()
    try:
        contents = tomli.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomli.TOMLDecodeError) as error:
        raise ScanFailure(
            "INVALID_CONFIG", "could not parse drift.toml", path
        ) from error
    discovery = contents.get("discovery", {})
    mappings = contents.get("accepted_mappings", {})
    if not isinstance(discovery, dict) or not isinstance(mappings, dict):
        raise ScanFailure("INVALID_CONFIG", "drift.toml tables must be tables", path)
    gdd_patterns = _read_patterns(discovery, "gdd", path)
    source_patterns = _read_patterns(discovery, "sources", path)
    exclusions = _read_patterns(discovery, "exclude", path) or ()
    accepted_mappings: dict[str, str] = {}
    for gdd_name, code_name in mappings.items():
        if not isinstance(gdd_name, str) or not isinstance(code_name, str):
            raise ScanFailure(
                "INVALID_CONFIG", "accepted mappings must be strings", path
            )
        accepted_mappings[normalize_name(gdd_name)] = normalize_name(code_name)
    return _ProjectConfig(
        gdd_patterns=gdd_patterns,
        source_patterns=source_patterns,
        exclusions=exclusions,
        accepted_mappings=accepted_mappings,
    )


def _read_patterns(
    section: dict[str, object], key: str, path: Path
) -> tuple[str, ...] | None:
    value = section.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ScanFailure(
            "INVALID_CONFIG", f"discovery.{key} must be a string list", path
        )
    if any(Path(item).is_absolute() or ".." in Path(item).parts for item in value):
        raise ScanFailure(
            "INVALID_CONFIG", f"discovery.{key} must stay within project", path
        )
    return tuple(value)


def _resolve_scan_config(
    root: Path, config: ScanConfig, project_config: _ProjectConfig
) -> ScanConfig:
    gdd_paths = config.gdd_paths or _discover_paths(
        root,
        project_config.gdd_patterns or _DEFAULT_GDD_PATTERNS,
        project_config.exclusions,
    )
    source_paths = config.source_paths or _discover_paths(
        root, project_config.source_patterns or ("**/*.gd",), project_config.exclusions
    )
    _validate_inputs(root, gdd_paths, source_paths)
    return ScanConfig(gdd_paths=gdd_paths, source_paths=source_paths)


def _discover_paths(
    root: Path, patterns: tuple[str, ...], exclusions: tuple[str, ...]
) -> tuple[Path, ...]:
    paths = {
        path.relative_to(root)
        for pattern in patterns
        for path in root.glob(pattern)
        if path.is_file() and not _is_excluded(path.relative_to(root), exclusions)
    }
    return tuple(sorted(paths))


def _is_excluded(path: Path, exclusions: tuple[str, ...]) -> bool:
    value = path.as_posix()
    return any(fnmatch.fnmatchcase(value, pattern) for pattern in exclusions)


def _validate_inputs(
    root: Path, gdd_paths: tuple[Path, ...], source_paths: tuple[Path, ...]
) -> None:
    if not gdd_paths or not source_paths:
        raise ScanFailure(
            "INVALID_CONFIG", "at least one GDD path and one source path are required"
        )
    for relative_path in gdd_paths:
        if relative_path.suffix.lower() != ".md":
            raise ScanFailure(
                "UNSUPPORTED_INPUT",
                "GDD inputs must be Markdown files",
                root / relative_path,
            )
    for relative_path in source_paths:
        if relative_path.suffix.lower() != ".gd":
            raise ScanFailure(
                "UNSUPPORTED_INPUT",
                "source inputs must be GDScript files",
                root / relative_path,
            )
    for relative_path in (*gdd_paths, *source_paths):
        path = root / relative_path
        if not path.is_file() or not path.stat().st_mode & 0o444:
            raise ScanFailure(
                "UNREADABLE_INPUT", "configured input is not readable", path
            )


def _parse_gdd_sources(
    root: Path, paths: tuple[Path, ...]
) -> tuple[tuple[TrackedEntity, ...], tuple[CandidateEntity, ...]]:
    parsed = tuple(_parse_gdd(root, path) for path in paths)
    return (
        tuple(entity for entities, _ in parsed for entity in entities),
        tuple(candidate for _, candidates in parsed for candidate in candidates),
    )


def _parse_gdd(
    root: Path, relative_path: Path
) -> tuple[list[TrackedEntity], list[CandidateEntity]]:
    path = root / relative_path
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise ScanFailure(
            "UNREADABLE_INPUT", "could not read configured input", path
        ) from error
    entities: list[TrackedEntity] = []
    candidates: list[CandidateEntity] = []
    for line_number, line in enumerate(lines, start=1):
        marker = _MARKER.search(line)
        if marker:
            tail = marker.group("tail")
            name = _PLANNED.sub("", tail).split(" —", maxsplit=1)[0].strip()
            if name:
                entities.append(
                    TrackedEntity(
                        name=name,
                        normalized_name=normalize_name(name),
                        entity_type=marker.group("type").strip(),
                        path=str(relative_path),
                        line=line_number,
                        planned=bool(_PLANNED.search(line)),
                    )
                )
            continue
        name_match = _HEADING.match(line) or _LIST_ITEM.match(line)
        if name_match:
            name = name_match.group("name").strip()
            if name:
                candidates.append(
                    CandidateEntity(
                        name=name, path=str(relative_path), line=line_number
                    )
                )
    return entities, candidates


def _find_entity(
    entity: TrackedEntity,
    by_name: dict[str, CodeEntity],
    mappings: dict[str, str],
) -> Finding:
    if entity.planned:
        return Finding(status="PLANNED", tracked_entity=entity, code_entity=None)
    code_name = mappings.get(entity.normalized_name, entity.normalized_name)
    code_entity = by_name.get(code_name)
    return Finding(
        status="MATCHED" if code_entity else "MISSING",
        tracked_entity=entity,
        code_entity=code_entity,
    )


def _parse_gdscript(root: Path, relative_path: Path) -> list[CodeEntity]:
    path = root / relative_path
    try:
        source = path.read_bytes()
    except OSError as error:
        raise ScanFailure(
            "UNREADABLE_INPUT", "could not read configured input", path
        ) from error
    tree = Parser(get_language("gdscript")).parse(source)
    if tree.root_node.has_error:
        raise ScanFailure("UNSUPPORTED_SOURCE", "could not parse GDScript input", path)
    entities: list[CodeEntity] = []
    extends = next(
        (
            child
            for child in tree.root_node.children
            if child.type == "extends_statement"
        ),
        None,
    )
    if extends is not None:
        script_name = relative_path.stem
        entities.append(
            CodeEntity(
                name=script_name,
                normalized_name=normalize_name(script_name),
                kind="script",
                path=str(relative_path),
                line=extends.start_point.row + 1,
            )
        )
    for node in _walk(tree.root_node):
        if node.type not in {"class_definition", "class_name_statement"}:
            continue
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            name = source[name_node.start_byte : name_node.end_byte].decode("utf-8")
            entities.append(
                CodeEntity(
                    name=name,
                    normalized_name=normalize_name(name),
                    kind="class",
                    path=str(relative_path),
                    line=name_node.start_point.row + 1,
                )
            )
    return entities


def _walk(node: Node) -> Iterator[Node]:
    yield node
    for child in node.children:
        yield from _walk(child)


def _write_artifacts(root: Path, result: ScanResult) -> None:
    (root / "drift.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    coverage = (
        "N/A"
        if result.summary.coverage_percent is None
        else f"{result.summary.coverage_percent:.0f}%"
    )
    lines = [
        "# Drift report",
        "",
        f"Coverage: {result.summary.matched}/{result.summary.total} ({coverage})",
        "",
        "## Findings",
        "",
    ]
    for finding in result.findings:
        evidence = f"{finding.tracked_entity.path}:{finding.tracked_entity.line}"
        code_evidence = (
            f"; code {finding.code_entity.path}:{finding.code_entity.line}"
            if finding.code_entity
            else ""
        )
        lines.append(
            f"- {finding.status}: {finding.tracked_entity.name} "
            f"({evidence}{code_evidence})"
        )
    if result.candidates:
        lines.extend(["", "## Candidates", ""])
        for candidate in result.candidates:
            lines.append(
                f"- CANDIDATE: {candidate.name} "
                f"({candidate.path}:{candidate.line}) — {candidate.guidance}"
            )
    (root / "drift_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

"""Match tracked GDD entities to GDScript symbols and produce findings."""

from __future__ import annotations

from pathlib import Path

from .models import (
    CodeEntity,
    Finding,
    FindingEvidence,
    TrackedEntity,
)
from .names import name_tokens, normalize_name


def findings(
    root: Path,
    tracked: tuple[TrackedEntity, ...],
    code: tuple[CodeEntity, ...],
    by_name: dict[str, tuple[CodeEntity, ...]],
    mappings: dict[str, str],
) -> tuple[Finding, ...]:
    results: list[Finding] = []
    consumed: set[str] = set()
    for entity in tracked:
        finding = find_entity(root, entity, code, by_name, mappings, consumed)
        results.append(finding)
        if finding.code_entity and finding.status in {
            "MATCHED",
            "RENAMED?",
            "PLANNED",
        }:
            consumed.add(finding.code_entity.entity_id)
        if finding.status in {"MATCHED", "PLANNED"}:
            code_name = mappings.get(entity.normalized_name, entity.normalized_name)
            consumed.update(
                candidate.entity_id for candidate in by_name.get(code_name, ())
            )

    for code_entity in code:
        if (
            code_entity.parent_id is None
            and code_entity.kind in {"script", "class"}
            and code_entity.entity_id not in consumed
        ):
            results.append(
                Finding(
                    status="ORPHANED",
                    tracked_entity=None,
                    code_entity=code_entity,
                    evidence=evidence(root, None, code_entity, code),
                )
            )
    return tuple(results)


def find_entity(
    root: Path,
    entity: TrackedEntity,
    code: tuple[CodeEntity, ...],
    by_name: dict[str, tuple[CodeEntity, ...]],
    mappings: dict[str, str],
    consumed: set[str],
) -> Finding:
    code_name = mappings.get(entity.normalized_name, entity.normalized_name)
    exact_entities = tuple(
        candidate
        for candidate in by_name.get(code_name, ())
        if candidate.entity_id not in consumed
    )
    exact_entities = prioritize_entity_kind(entity, exact_entities)
    if entity.planned:
        return Finding(
            status="PLANNED",
            tracked_entity=entity,
            code_entity=exact_entities[0] if exact_entities else None,
            evidence=evidence(
                root, entity, exact_entities[0] if exact_entities else None, code
            ),
        )
    if exact_entities:
        code_entity = exact_entities[0]
        return Finding(
            status="MATCHED",
            tracked_entity=entity,
            code_entity=code_entity,
            evidence=evidence(root, entity, code_entity, code),
        )

    gdd_tokens = name_tokens(entity.name)
    scored = sorted(
        [
            (
                token_overlap(gdd_tokens, name_tokens(candidate.name)),
                candidate,
            )
            for candidate in code
            if candidate.entity_id not in consumed
        ],
        key=lambda item: item[0],
    )
    if scored:
        highest = scored[-1][0]
        candidates = [candidate for score, candidate in scored if score == highest]
        if highest > 0 and len(candidates) == 1:
            code_entity = candidates[0]
            return Finding(
                status="RENAMED?",
                tracked_entity=entity,
                code_entity=code_entity,
                evidence=evidence(root, entity, code_entity, code),
            )

    return Finding(
        status="MISSING",
        tracked_entity=entity,
        code_entity=None,
        evidence=evidence(root, entity, None, code),
    )


def token_overlap(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def prioritize_entity_kind(
    tracked: TrackedEntity, candidates: tuple[CodeEntity, ...]
) -> tuple[CodeEntity, ...]:
    expected_kind = {
        "class": "class",
        "function": "function",
        "method": "function",
        "signal": "signal",
        "variable": "exported_variable",
        "exportedvariable": "exported_variable",
        "script": "script",
    }.get(normalize_name(tracked.entity_type))
    if expected_kind is not None:
        typed = tuple(
            candidate for candidate in candidates if candidate.kind == expected_kind
        )
        if typed:
            return typed
    priority = {"class": 0, "script": 1}
    return tuple(
        sorted(candidates, key=lambda candidate: priority.get(candidate.kind, 2))
    )


def evidence(
    root: Path,
    tracked: TrackedEntity | None,
    code_entity: CodeEntity | None,
    code: tuple[CodeEntity, ...],
) -> FindingEvidence:
    return FindingEvidence(
        gdd_path=tracked.path if tracked else None,
        gdd_line=tracked.line if tracked else None,
        code_path=code_entity.path if code_entity else None,
        code_line=code_entity.line if code_entity else None,
        code_symbol_path=code_entity.symbol_path if code_entity else None,
        containment_path=containment_path(code_entity, code),
        gdd_excerpt=read_excerpt(root, tracked.path, tracked.line) if tracked else None,
        code_excerpt=(
            read_excerpt(root, code_entity.path, code_entity.line)
            if code_entity
            else None
        ),
    )


def read_excerpt(root: Path, relative_path: str, line: int) -> str | None:
    try:
        lines = (root / relative_path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return None


def containment_path(
    code_entity: CodeEntity | None, code: tuple[CodeEntity, ...]
) -> tuple[str, ...]:
    by_id = {entity.entity_id: entity for entity in code}
    path: list[str] = []
    current = code_entity
    while current is not None:
        path.append(current.symbol_path or current.name)
        current = by_id.get(current.parent_id or "")
    return tuple(reversed(path))

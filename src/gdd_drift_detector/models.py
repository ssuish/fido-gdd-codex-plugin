"""Typed domain values exposed by the detector boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

FindingStatus = Literal["MATCHED", "MISSING", "PLANNED"]
ScanFailureCode = Literal[
    "INVALID_PROJECT",
    "INVALID_CONFIG",
    "UNSUPPORTED_INPUT",
    "UNREADABLE_INPUT",
    "UNSUPPORTED_SOURCE",
]


@dataclass(frozen=True)
class ScanConfig:
    """Optional explicit local inputs, relative to the project root."""

    gdd_paths: tuple[Path, ...] = ()
    source_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class TrackedEntity:
    name: str
    normalized_name: str
    entity_type: str
    path: str
    line: int
    planned: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CodeEntity:
    name: str
    normalized_name: str
    kind: str
    path: str
    line: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class Finding:
    status: FindingStatus
    tracked_entity: TrackedEntity
    code_entity: CodeEntity | None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "tracked_entity": self.tracked_entity.to_dict(),
            "code_entity": self.code_entity.to_dict() if self.code_entity else None,
        }


@dataclass(frozen=True)
class ScanSummary:
    matched: int
    total: int
    coverage_percent: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ScanResult:
    schema_version: str
    project_root: str
    tracked_entities: tuple[TrackedEntity, ...]
    code_entities: tuple[CodeEntity, ...]
    findings: tuple[Finding, ...]
    candidates: tuple[CandidateEntity, ...]
    summary: ScanSummary
    duration_ms: int

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "scan": {
                "project_root": self.project_root,
                "duration_ms": self.duration_ms,
            },
            "tracked_entities": [entity.to_dict() for entity in self.tracked_entities],
            "code_entities": [entity.to_dict() for entity in self.code_entities],
            "findings": [finding.to_dict() for finding in self.findings],
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "summary": self.summary.to_dict(),
        }


@dataclass(frozen=True)
class CandidateEntity:
    """Advisory Markdown concept that does not affect authoritative coverage."""

    name: str
    path: str
    line: int
    guidance: str = "Add [entity: type] before this name to track it."
    status: Literal["CANDIDATE"] = "CANDIDATE"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ScanFailure(Exception):
    """A stable, typed invalid-input failure suitable for host adapters."""

    def __init__(
        self, code: ScanFailureCode, message: str, path: Path | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path

    def to_dict(self) -> dict[str, object]:
        error: dict[str, str] = {"code": self.code, "message": self.message}
        if self.path is not None:
            error["path"] = str(self.path)
        return {"error": error}

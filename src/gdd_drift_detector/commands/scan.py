"""Scan command handler for the detector CLI."""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from pathlib import Path

from ..models import ScanConfig, ScanFailure
from ..scanner import scan


def run_scan(
    project_root: Path,
    gdd: Sequence[Path] | None = None,
    source: Sequence[Path] | None = None,
) -> int:
    """Run a drift scan and print JSON to stdout; typed failures go to stderr."""
    try:
        result = scan(
            project_root,
            ScanConfig(tuple(gdd or ()), tuple(source or ())),
        )
    except ScanFailure as error:
        print(json.dumps(error.to_dict()), file=sys.stderr)
        return 2
    print(json.dumps(result.to_dict(), sort_keys=True))
    return 0

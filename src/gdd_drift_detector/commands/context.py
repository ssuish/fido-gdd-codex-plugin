"""Context command: print the scan-backed game design context block."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ..context_block import render_context_block
from ..models import ScanFailure
from ..scanner import scan


def run_context(project_root: Path) -> int:
    """Scan once and print the minimal context block to stdout."""
    try:
        result = scan(project_root)
    except ScanFailure as error:
        print(json.dumps(error.to_dict()), file=sys.stderr)
        return 2
    print(render_context_block(result), end="")
    return 0

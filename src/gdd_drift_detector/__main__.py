"""JSON command-line adapter for the detector engine."""

from __future__ import annotations

import argparse
from pathlib import Path

from .commands.scan import run_scan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--gdd", action="append", default=[], type=Path)
    parser.add_argument("--source", action="append", default=[], type=Path)
    parser.add_argument("--json", required=True, action="store_true")
    args = parser.parse_args()
    return run_scan(args.project_root, gdd=args.gdd, source=args.source)


if __name__ == "__main__":
    raise SystemExit(main())

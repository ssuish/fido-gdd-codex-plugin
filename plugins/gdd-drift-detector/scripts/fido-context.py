#!/usr/bin/env python3
"""Launch `fido context` through the standalone detector runtime."""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_detect_drift() -> Any:
    path = Path(__file__).with_name("detect-drift.py")
    spec = importlib.util.spec_from_file_location("detect_drift_launcher", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load launcher helpers from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_context(
    python: Path,
    source_root: Path,
    project_root: Path,
    context_args: list[str],
) -> int:
    environment_vars = os.environ.copy()
    environment_vars["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(source_root), environment_vars.get("PYTHONPATH")))
    )
    command = [
        str(python),
        "-m",
        "gdd_drift_detector",
        "context",
        "--project-root",
        str(project_root),
        *context_args,
    ]
    completed = subprocess.run(command, env=environment_vars, check=False)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--detector-root",
        type=Path,
        default=None,
        help="repository containing pyproject.toml and src/gdd_drift_detector",
    )
    args, unknown = parser.parse_known_args(argv)

    detect_drift = _load_detect_drift()
    plugin_root = _plugin_root()
    version = detect_drift._read_plugin_version(plugin_root)
    repository_root = detect_drift.resolve_detector_root(
        plugin_root, args.detector_root
    )
    if repository_root is None or not (repository_root / "pyproject.toml").is_file():
        print(
            "detector runtime unavailable; install the standalone plugin package "
            "(with pyproject.toml, uv.lock, and src/) or set GDD_DETECTOR_ROOT",
            file=sys.stderr,
        )
        return 2

    try:
        python = detect_drift.ensure_environment(repository_root, version)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    return run_context(
        python,
        repository_root / "src",
        args.project_root,
        list(unknown),
    )


if __name__ == "__main__":
    raise SystemExit(main())

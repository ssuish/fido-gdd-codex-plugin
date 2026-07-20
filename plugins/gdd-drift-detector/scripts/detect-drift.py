#!/usr/bin/env python3
"""Launch the shared detector through a versioned, cached environment."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_plugin_version(plugin_root: Path) -> str:
    manifest = plugin_root / ".codex-plugin" / "plugin.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"plugin.json missing version: {manifest}")
    return version


def resolve_detector_root(
    plugin_root: Path, explicit: Path | None = None
) -> Path | None:
    """Prefer plugin-local package root; GDD_DETECTOR_ROOT is fallback only."""
    if explicit is not None:
        return explicit.resolve()

    package_roots = (plugin_root, plugin_root.parents[1])
    for package_root in package_roots:
        if (package_root / "pyproject.toml").is_file() and (
            package_root / "src" / "gdd_drift_detector"
        ).is_dir():
            return package_root.resolve()

    env_root = os.environ.get("GDD_DETECTOR_ROOT")
    if env_root:
        return Path(env_root).resolve()

    return None


def normalize_detector_args(unknown: list[str]) -> list[str]:
    """Forward detector CLI flags; drop a leading `--` and duplicate `--json`."""
    args = list(unknown)
    if args and args[0] == "--":
        args = args[1:]
    return [arg for arg in args if arg != "--json"]


def ensure_environment(repository_root: Path, version: str) -> Path:
    """Return the cached venv Python, provisioning with uv on first run."""
    cache_root = (
        Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        / "gdd-drift-detector"
        / version
    )
    environment = cache_root / "venv"
    python = environment / "bin" / "python"
    if os.name == "nt":
        python = environment / "Scripts" / "python.exe"

    if python.is_file():
        return python

    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("first-run setup requires uv")
    cache_root.mkdir(parents=True, exist_ok=True)
    subprocess.run([uv, "venv", str(environment)], check=True)
    exported = subprocess.run(
        [
            uv,
            "export",
            "--locked",
            "--format",
            "requirements.txt",
            "--no-dev",
            "--no-emit-project",
        ],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    requirements = cache_root / "requirements.lock.txt"
    requirements.write_text(exported.stdout, encoding="utf-8")
    subprocess.run(
        [
            uv,
            "pip",
            "sync",
            "--python",
            str(python),
            "--require-hashes",
            str(requirements),
        ],
        check=True,
    )
    return python


def run_detector(
    python: Path,
    source_root: Path,
    project_root: Path,
    detector_args: list[str],
) -> int:
    environment_vars = os.environ.copy()
    environment_vars["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(source_root), environment_vars.get("PYTHONPATH")))
    )
    command = [
        str(python),
        "-m",
        "gdd_drift_detector",
        "--project-root",
        str(project_root),
        "--json",
        *detector_args,
    ]
    completed = subprocess.run(command, env=environment_vars, check=False)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument(
        "--detector-root",
        type=Path,
        default=None,
        help="repository containing pyproject.toml and src/gdd_drift_detector",
    )
    args, unknown = parser.parse_known_args(argv)
    detector_args = normalize_detector_args(unknown)

    plugin_root = _plugin_root()
    version = _read_plugin_version(plugin_root)
    repository_root = resolve_detector_root(plugin_root, args.detector_root)
    if repository_root is None or not (repository_root / "pyproject.toml").is_file():
        print(
            "detector runtime unavailable; install the standalone plugin package "
            "(with pyproject.toml, uv.lock, and src/) or set GDD_DETECTOR_ROOT",
            file=sys.stderr,
        )
        return 2

    try:
        python = ensure_environment(repository_root, version)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 2

    return run_detector(
        python,
        repository_root / "src",
        args.project_root,
        detector_args,
    )


if __name__ == "__main__":
    raise SystemExit(main())

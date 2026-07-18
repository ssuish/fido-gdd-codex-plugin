from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "gdd-drift-detector"


def test_plugin_manifest_and_marketplace_reference_shared_detector() -> None:
    manifest = json.loads(
        (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    marketplace = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "gdd-drift-detector"
    assert (PLUGIN / "skills" / "detect-drift" / "SKILL.md").is_file()
    assert (PLUGIN / "scripts" / "detect-drift.py").is_file()
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/gdd-drift-detector"


def test_launcher_help_does_not_provision_or_scan() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(PLUGIN / "scripts" / "detect-drift.py"),
            "--help",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "--project-root" in completed.stdout


def test_launcher_reports_missing_runtime_without_touching_target_project(
    tmp_path: Path,
) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(PLUGIN / "scripts" / "detect-drift.py"),
            "--project-root",
            str(tmp_path),
            "--detector-root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "detector runtime unavailable" in completed.stderr
    assert not (tmp_path / "drift.json").exists()

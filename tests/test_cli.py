from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from gdd_drift_detector.commands.scan import run_scan

FIXTURE = Path(__file__).parent / "fixtures" / "godot-project"


def copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE, root)
    return root


def test_run_scan_prints_sorted_json_on_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = copy_fixture(tmp_path)

    code = run_scan(
        root,
        gdd=[Path("GDD.md")],
        source=[Path("scripts/player_controller.gd")],
    )

    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    payload = json.loads(captured.out)
    assert payload["summary"]["coverage_percent"] == 100.0
    assert captured.out == json.dumps(payload, sort_keys=True) + "\n"


def test_run_scan_prints_typed_failure_json_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "not-a-project"

    code = run_scan(
        root,
        gdd=[Path("GDD.md")],
        source=[Path("script.gd")],
    )

    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "INVALID_PROJECT"

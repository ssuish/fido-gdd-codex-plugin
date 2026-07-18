from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
SITE = ROOT / "showcase" / "site"
FIXTURE = ROOT / "showcase" / "godot-deckbuilder"


def test_site_consumes_fixture_generated_artifact_without_synthetic_findings() -> None:
    site_report = json.loads((SITE / "public" / "drift.json").read_text())
    fixture_report = json.loads((FIXTURE / "drift.json").read_text())

    assert site_report == fixture_report
    app = (SITE / "src" / "App.tsx").read_text()
    assert 'fetch("./drift.json")' in app
    assert "selectedFinding" in app
    assert 'role="listbox"' in app
    assert "report.candidates" in app
    assert "game-fixture" in app
    assert (SITE / "public" / "marketplace.json").is_file()
    assert (SITE / "public" / "downloads" / "gdd-drift-detector.zip").is_file()


def test_site_declares_accessible_states_and_responsive_reduced_motion_rules() -> None:
    app = (SITE / "src" / "App.tsx").read_text()
    styles = (SITE / "src" / "styles.css").read_text()

    assert "Report unavailable" in app
    assert "Loading fixture report" in app
    assert 'aria-live="polite"' in app
    assert "@media (max-width: 767px)" in styles
    assert "prefers-reduced-motion" in styles
    assert "prefers-color-scheme" not in styles

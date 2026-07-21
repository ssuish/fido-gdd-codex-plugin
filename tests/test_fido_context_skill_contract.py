from __future__ import annotations

from pathlib import Path

PLUGIN = Path(__file__).parents[1] / "plugins" / "gdd-drift-detector"
SKILL = PLUGIN / "skills" / "fido-context" / "SKILL.md"
SETUP = PLUGIN / "skills" / "setup-gdd" / "SKILL.md"
DETECT = PLUGIN / "skills" / "detect-drift" / "SKILL.md"


def test_fido_context_skill_is_hero_entry_and_chains_cold_start() -> None:
    text = SKILL.read_text(encoding="utf-8")

    assert text.startswith("---\n")
    assert "name: fido-context" in text
    assert "fido context" in text
    assert "setup-gdd" in text
    assert "detect-drift" in text
    assert "AGENTS.md" in text
    assert "game design context" in text.lower() or "Game Design Context" in text


def test_setup_skill_hands_off_to_fido_context() -> None:
    text = SETUP.read_text(encoding="utf-8")

    assert "fido context" in text
    assert "fido-context" in text
    closing = text.lower().rsplit("when setup is done", 1)[-1]
    assert "fido context" in closing
    assert "detect-drift" not in closing or "audit" in closing


def test_detect_drift_skill_is_positioned_as_audit() -> None:
    text = DETECT.read_text(encoding="utf-8").lower()

    assert "audit" in text or "secondary" in text
    assert "fido context" in text or "fido-context" in text

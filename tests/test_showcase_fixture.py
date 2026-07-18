from __future__ import annotations

import json
from pathlib import Path

FIXTURE = Path(__file__).parents[1] / "showcase" / "godot-deckbuilder"


def test_showcase_fixture_is_traceable_and_declares_required_inputs() -> None:
    assert (FIXTURE / ".godot-version").read_text().strip() == "4.6.3"
    assert "config_version=5" in (FIXTURE / "project.godot").read_text()
    assert (FIXTURE / "GDD.md").is_file()
    assert (FIXTURE / "deck_builder.gd").is_file()
    assert (FIXTURE / "main.tscn").is_file()
    assert (FIXTURE / "export_presets.cfg").read_text().find('platform="Web"') >= 0
    assert (FIXTURE / "WEB_EXPORT.md").is_file()


def test_showcase_gameplay_contract_has_cards_energy_and_win_loss_states() -> None:
    source = (FIXTURE / "deck_builder.gd").read_text()
    main_source = (FIXTURE / "main.gd").read_text()

    assert 'deck = ["strike", "block"]' in source
    assert "starting_energy" in source
    assert "play_strike" in source
    assert "play_block" in source
    assert "const VICTORY" in source
    assert "const DEFEAT" in source
    assert "state = DEFEAT" in source
    assert "state = RUN_COMPLETE" in source
    assert "ENCOUNTERS" in source
    assert "_refresh_card(strike_card" in main_source
    assert "resolve_enemy_turn" in main_source
    assert 'ExtResource("2_deck")' in (FIXTURE / "main.tscn").read_text()


def test_generated_fixture_artifact_contains_required_statuses() -> None:
    artifact = json.loads((FIXTURE / "drift.json").read_text())
    statuses = {finding["status"] for finding in artifact["findings"]}

    assert {"MATCHED", "MISSING", "RENAMED?", "ORPHANED", "PLANNED"} <= statuses
    assert artifact["candidates"]

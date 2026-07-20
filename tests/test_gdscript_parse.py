"""GDScript parse regressions (tree-sitter binding workarounds)."""

from __future__ import annotations

from pathlib import Path

from gdd_drift_detector.gdscript_parse import parse_gdscript

SHOWCASE = Path(__file__).resolve().parents[1] / "showcase" / "godot-deckbuilder"


def test_parse_gdscript_is_stable_across_repeated_parses() -> None:
    """Reparse must not segfault on Python 3.10 tree-sitter GDScript bindings."""
    relative = Path("deck_builder.gd")

    first_entities, first_relationships = parse_gdscript(SHOWCASE, relative)
    second_entities, second_relationships = parse_gdscript(SHOWCASE, relative)

    first_snapshot = [
        (entity.name, entity.kind, entity.line) for entity in first_entities
    ]
    second_snapshot = [
        (entity.name, entity.kind, entity.line) for entity in second_entities
    ]
    assert first_snapshot == second_snapshot
    assert len(first_relationships) == len(second_relationships)
    assert ("start_run", "function", 38) in first_snapshot
    assert ("DeckBuilder", "class", 1) in first_snapshot

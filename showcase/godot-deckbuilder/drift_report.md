# Drift report

State: COMPLETE
Coverage: 3/5 (60%)

## Priority findings

- MISSING: Shield (GDD.md:6)
- RENAMED?: Enemy AI (GDD.md:7; code ai_controller.gd:1)
- ORPHANED: orphan_logger (code orphan_logger.gd:1)

## Findings

- MATCHED: DeckBuilder (GDD.md:3; code deck_builder.gd:1)
  - GDD evidence: GDD.md:3
  - Code evidence: deck_builder.gd:1
  - Symbol: `DeckBuilder`
  - Containment: DeckBuilder
  - GDD excerpt: `[entity: class] DeckBuilder — owns one deterministic three-encounter run.`
  - Code excerpt: `class_name DeckBuilder`
- MATCHED: draw_card (GDD.md:4; code deck_builder.gd:63)
  - GDD evidence: GDD.md:4
  - Code evidence: deck_builder.gd:63
  - Symbol: `DeckBuilder.draw_card`
  - Containment: DeckBuilder -> DeckBuilder.draw_card
  - GDD excerpt: `[entity: function] draw_card — moves next card into hand.`
  - Code excerpt: `func draw_card() -> String:`
- MATCHED: resolve_enemy_turn (GDD.md:5; code deck_builder.gd:102)
  - GDD evidence: GDD.md:5
  - Code evidence: deck_builder.gd:102
  - Symbol: `DeckBuilder.resolve_enemy_turn`
  - Containment: DeckBuilder -> DeckBuilder.resolve_enemy_turn
  - GDD excerpt: `[entity: function] resolve_enemy_turn — enemy acts after player turn.`
  - Code excerpt: `func resolve_enemy_turn() -> int:`
- MISSING: Shield (GDD.md:6)
  - GDD evidence: GDD.md:6
  - GDD excerpt: `[entity: card] Shield — deliberately missing implementation.`
- RENAMED?: Enemy AI (GDD.md:7; code ai_controller.gd:1)
  - GDD evidence: GDD.md:7
  - Code evidence: ai_controller.gd:1
  - Symbol: `ai_controller`
  - Containment: ai_controller
  - GDD excerpt: `[entity: system] Enemy AI — rename candidate for `ai_controller.gd`.`
  - Code excerpt: `extends Node`
- PLANNED: FutureRelic (GDD.md:8)
  - GDD evidence: GDD.md:8
  - GDD excerpt: `[entity: state] FutureRelic [planned] — outside showcase slice.`
- ORPHANED: orphan_logger (code orphan_logger.gd:1)
  - Code evidence: orphan_logger.gd:1
  - Symbol: `orphan_logger`
  - Containment: orphan_logger
  - Code excerpt: `extends Node`

## Candidates

- CANDIDATE: Showcase deck-builder (GDD.md:1) — Add [entity: type] before this name to track it.
- CANDIDATE: Visitor walkthrough (GDD.md:10) — Add [entity: type] before this name to track it.

## Next actions

- MISSING ownership: implement or unmark/remove each tracked entity.
- RENAMED? ownership: add accepted_mappings or reject each candidate; do not count it as matched without accepted_mappings.
- ORPHANED ownership: track, exclude in drift.toml, or remove each top-level symbol.
- PLANNED ownership: keep entity outside the current coverage slice until it is ready.

# Traceable Godot fixture

Godot 4.6.3 fixture (gl_compatibility, 960×540 base canvas, responsive Web-export friendly). The UI uses Godot canvas-item stretching with a preserved aspect ratio, so the complete composition scales and letterboxes cleanly in different iframe sizes without distorting card or icon artwork. A deterministic three-encounter showcase run:

1. Start a run. Each turn draws the fixed `strike`, then `block` deck.
2. Resolve encounters at 3 HP / 2 damage, 6 HP / 3 damage, and 9 HP / 4 damage.
3. After the first two victories choose Recover (+2 HP, capped at 6) or Empower (+1 Strike damage).
4. Reach `RUN_COMPLETE` after the third victory or `DEFEAT` when player HP reaches zero.

The showcase UI presents the run as a compact warm arcane/brass card layout. Cards are built from the pack's free emoji sprites and status icons while preserving visible names, costs, and numeric effects. The first enemy starts at 3 HP so the intentional walkthrough `Strike → Block → End turn` completes in one short visit; player HP remains 6, Strike still costs 1 and deals 3, and Block still grants 2.

The drift scenario is deliberately preserved: Shield remains missing, `ai_controller.gd` remains the rename candidate for “Enemy AI”, `FutureRelic` remains planned, and `orphan_logger.gd` remains unused. The supplied CC0 UI pack is under `assets/deck_builder`; `Status/PNG Small (64 px)/combat_small.png` is used for the block treatment.

`GDD.md`, GDScript sources, `drift.json`, and `drift_report.md` remain traceable
fixture artifacts. Discovery excludes `main.gd` via `drift.toml` (UI shell only;
the GDScript parser currently segfaults on that file). Expected detector statuses
include `MATCHED`, `MISSING`, `RENAMED?`, `ORPHANED`, `CANDIDATE`, and `PLANNED`;
the checked-in report is a baseline snapshot and is not hand-edited when the
detector is unavailable.

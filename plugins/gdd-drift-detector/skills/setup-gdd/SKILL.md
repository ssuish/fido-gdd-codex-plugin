---
name: setup-gdd
description: Prepare a GDD source set for Fido by bringing an existing design doc or grilling the design in chat until a draft is ready.
---

# Setup GDD conventions

Prepare a **GDD source set** for **Fido** (local design-fidelity checks). This skill is
chat-first authoring guidance. It does **not** run a drift scan, does **not**
invoke `detect-drift`, and must **not** silently create or modify repository
files (`GDD.md`, `drift.toml`, GDScript, or a Godot project).

Offer exactly one of two paths after asking which applies.

## Path A — Bring an existing GDD

1. Ask the user where their design doc lives, or whether they can place one at a
   default discovery path.
2. Default discovery paths (unless overridden later in `drift.toml`):
   - `GDD.md`
   - `design.md`
   - `docs/gdd/**/*.md`
   - `docs/design/**/*.md`
3. Explain authoritative tracking: only concepts marked with an **entity marker**
   affect coverage. Unmarked prose may surface as advisory candidates only.
4. Show the marker syntax and ask them to adopt it deliberately:
   - Tracked: `## Combat Loop [entity: system]`
   - Planned (excluded from coverage): `## Multiplayer [entity: system] [planned]`
5. Confirm whether they already have a Godot 4 + GDScript project. If yes, note
   that `/detect-drift` (or `$gdd-drift-detector:detect-drift`) can scan after
   they save the marked GDD themselves.
6. Stop when the user knows which files form the GDD source set and how markers
   work. Do not write files for them.

## Path B — Grill a new design draft

1. Interview the design like a grilling session: one focused question at a time.
2. Cover enough to draft a useful GDD source set:
   - Fantasy / pitch in one sentence
   - Core player verbs and loop
   - Key systems, characters, abilities, and resources
   - What is in the current slice versus intentionally `[planned]`
3. After enough answers, produce an **in-session Markdown draft** using entity
   markers. Example shape:

   ```markdown
   # Game Title

   ## Core Loop [entity: system]
   ...

   ## Player Character [entity: character]
   ...

   ## Seasonal Events [entity: system] [planned]
   ...
   ```

4. Ask the user to save the draft themselves into a discovery path (prefer
   `GDD.md` at the Godot project root). Do not write the file automatically.
5. Remind them that unmarked headings are not authoritative coverage inputs.

## Shared rules

- Never auto-write `GDD.md`, `drift.toml`, source files, or project scaffolding.
- Never run the detector or invent scan results during setup.
- Distinguish **tracked entities** (markers) from unmarked prose candidates.
- `drift.toml` is optional project config for accepted mappings and discovery
  overrides; describe it, do not create it unless the user explicitly asks you
  to draft text they will paste themselves.
- When setup is done, hand off explicitly: next step is the separate
  `detect-drift` skill / `/detect-drift` command after they save their GDD.

First-run detector provisioning (when they later scan) requires **`uv`**; scans
stay local and offline after that.

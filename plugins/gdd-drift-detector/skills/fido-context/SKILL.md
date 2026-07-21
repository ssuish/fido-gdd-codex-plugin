---
name: fido-context
description: Refresh the game design context block for this session so coding stays aligned to the GDD.
---

# Fido context

Primary **Fido** workflow: refresh the **game design context block** so this
session already knows the design intent, what's missing, coverage, and what
not to add. Prefer this over a full drift audit unless the user asks to scan.

Keep everything local; never upload GDD or source files.

1. Resolve the target Godot project root (cwd unless the user gives another
   path).
2. Run `fido context` for that root (or the bundled
   `scripts/fido-context.py --project-root <root>` when PATH `fido` is
   unavailable). For a PATH console script, install from the extracted
   standalone ZIP or git — **not** bare `uv tool install fido` (PyPI name
   clash): `uv tool install /absolute/path/to/extracted-fido` or
   `uv tool install git+https://github.com/ssuish/gdd-plugin.git`. Default
   write target is `AGENTS.md`.
3. If the command exits non-zero because no readable design text exists, or
   the project is untracked with no usable GDD yet, chain to **`setup-gdd`**
   instead of inventing documentation. After the user saves a GDD, re-run
   `fido context`.
4. Summarize the refreshed block briefly: what the game is, top missing items,
   coverage, and DO NOT ADD / planned scope. Point to `drift_report.md` only
   when the user wants deeper audit detail.
5. For an explicit design-fidelity audit (full findings, warnings, candidates),
   hand off to the secondary **`detect-drift`** skill — do not treat drift scan
   as the default CTA.

Useful flags when the user asks:

- `--print` — stdout only, no file write
- `--update-only` — refresh only if a Fido block already exists
- `--if-stale` — skip work when GDD/sources are unchanged
- `--fresh` — force a new local scan
- `--verbose` — add implementation table / suggested prompts

SessionStart already runs `fido context --update-only --if-stale` via the
plugin hook; use this skill for an intentional refresh or cold-start chain.

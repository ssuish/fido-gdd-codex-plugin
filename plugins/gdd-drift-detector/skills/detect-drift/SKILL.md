---
name: detect-drift
description: Run the local GDD-to-GDScript drift detector and summarize its report.
---

# Detect drift

Run detector from project root. Keep scan local; never upload GDD or source files.
This skill only scans. For GDD conventions or drafting, use the separate
`setup-gdd` skill first.

1. Resolve target Godot project root. Use current working directory unless user
   gives another path.
2. Confirm a GDD source set exists (marked entities in discovery paths). If the
   project is untracked or the user has no GDD yet, direct them to `setup-gdd`
   instead of inventing documentation.
3. Invoke bundled `scripts/detect-drift.py` from plugin root with
   `--project-root <root>`. The standalone plugin package embeds the detector
   beside the plugin; `GDD_DETECTOR_ROOT` is optional fallback only.
4. Read JSON result from stdout. Report state, coverage, priority findings,
   warnings, and next actions.
5. Point user to `<root>/drift_report.md` and `<root>/drift.json`.

Pass repeated `--gdd` and `--source` options when user gives explicit inputs.
Preserve `drift.toml`; accepted rename mappings live under `[accepted_mappings]`.
Never mutate GDD, source, or `drift.toml` — only generated report artifacts.

First run may provision the versioned cached environment with **`uv`** from the
embedded lock data. After provisioning, scans run without network or telemetry.
Launcher must run from plugin location, not target project location.

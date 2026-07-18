---
name: detect-drift
description: Run the local GDD-to-GDScript drift detector and summarize its report.
---

# Detect drift

Run detector from project root. Keep scan local; never upload GDD or source files.

1. Resolve target Godot project root. Use current working directory unless user gives another path.
2. Invoke bundled `scripts/detect-drift.py` from plugin root with `--project-root <root>`.
   Set `GDD_DETECTOR_ROOT` when plugin files and detector repository are installed separately.
3. Read JSON result from stdout. Report state, coverage, priority findings, warnings, and next actions.
4. Point user to `<root>/drift_report.md` and `<root>/drift.json`.

Pass repeated `--gdd` and `--source` options when user gives explicit inputs. Preserve
`drift.toml`; accepted rename mappings live under `[accepted_mappings]`.

First run may provision the versioned cached environment from repository lock data. After
provisioning, scans run without network or telemetry access. Launcher must run from plugin
location, not target project location.

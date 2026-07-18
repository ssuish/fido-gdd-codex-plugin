# GDD Drift Detector

Offline, local detector for drift between GDD entity markers and GDScript
implementation symbols. Current MVP ships four pieces: typed scan results,
evidence-rich Markdown/JSON reports, a Codex plugin adapter, and a linked
showcase backed by a traceable Godot deck-builder fixture.

## Quick start

```sh
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run python -m gdd_drift_detector --project-root /path/to/godot-project --json
npm run showcase:dev    # start linked showcase
npm run showcase:build  # build linked showcase
npm run showcase:lint
npm run showcase:test
```

The Python package needs Python 3.10+ and uses `uv.lock` for reproducible
development dependencies. The scan is read-only for inputs and never uses the
network. It writes only the generated `drift.json` and `drift_report.md`.

## Detector capability

Conventional scans discover `GDD.md`, `design.md`, `docs/gdd/**/*.md`,
`docs/design/**/*.md`, and GDScript inputs. Use repeated `--gdd` and `--source`
arguments for explicit inputs. The programmatic seam is
`scan(project_root, ScanConfig(...))`.

Findings use these statuses:

- `MATCHED`: tracked entity has an exact implementation match.
- `RENAMED?`: one unique fuzzy candidate exists; review required.
- `MISSING`: tracked entity has no implementation match.
- `PLANNED`: implementation symbol has no tracked entity yet.
- `ORPHANED`: top-level implementation is not represented by a tracked entity.

Reports include source/GDD paths, line anchors, symbols, excerpts, containment
relationships, summary coverage, priority findings, and next actions. A scan is
`COMPLETE` when all configured inputs parse; it is `PARTIAL` when an input is
unreadable or unparseable. `N/A` coverage is used when no comparable tracked
entities exist; partial-scan artifacts mark that result as qualified by explicit
warnings rather than implying complete coverage.

Optional version-controlled `drift.toml` supports project-local discovery and
accepted mappings. It is read but never modified:

```toml
[discovery]
gdd = ["design/**/*.md"]
sources = ["game/**/*.gd"]
exclude = ["game/generated/**"]

[accepted_mappings]
"Design Name" = "implementation_name"
```

`[accepted_mappings]` is the accepted latest-decision escape hatch: it maps a
tracked GDD name to its intentional implementation symbol before fuzzy matching.
The detector reads `drift.toml` and does not modify it.

## Detailed usage

Scan a Godot project and write JSON plus Markdown artifacts:

```sh
uv run python -m gdd_drift_detector \
  --project-root /path/to/godot-project \
  --json
```

Use explicit inputs when conventional discovery paths do not fit:

```sh
uv run python -m gdd_drift_detector \
  --project-root /path/to/godot-project \
  --gdd design/gameplay.md \
  --gdd docs/gdd/combat.md \
  --source game/player.gd \
  --source game/combat.gd \
  --json
```

Paths are relative to the project root. Each scan writes:

```text
/path/to/godot-project/drift.json
/path/to/godot-project/drift_report.md
```

The Python API remains available for integration:

```python
from pathlib import Path

from gdd_drift_detector import ScanConfig, scan

result = scan(
    Path("/path/to/godot-project"),
    ScanConfig(
        gdd_paths=(Path("design.md"),),
        source_paths=(Path("game/player.gd"),),
    ),
)

print(result.state)
print(result.summary.coverage_percent)
```

## Codex plugin

The local Codex plugin is in `plugins/gdd-drift-detector`. It is a **host
adapter** for Codex (not a Godot editor plugin). The launcher provisions a
versioned cache with **`uv`**, installs from the embedded lockfile, and runs the
detector without network access after dependencies are available.

**Install handoff** uses the **Standalone plugin package** at
`showcase/site/public/downloads/gdd-drift-detector.zip`. That ZIP embeds the
plugin, detector sources, `pyproject.toml`, and `uv.lock`, so users do not need
a monorepo checkout. `GDD_DETECTOR_ROOT` remains an optional fallback.

Rebuild the downloadable ZIP after plugin or detector packaging changes:

```sh
python3 scripts/build_standalone_plugin_zip.py
```

Repository marketplace metadata is in `marketplace.json`. Skills:

- `setup-gdd` — bring-or-grill GDD convention setup (chat-first; no silent writes)
- `detect-drift` — read-only local drift scan

Run the adapter from this repository or an extracted standalone package:

```sh
python3 plugins/gdd-drift-detector/scripts/detect-drift.py \
  --project-root /path/to/godot-project
```

The documented Codex surfaces are `$gdd-drift-detector:setup-gdd` and
`$gdd-drift-detector:detect-drift` (`/detect-drift` is the scan shorthand).
Cursor and MCP remain future host adapters, not MVP ship targets.

## Showcase and fixture

`showcase/godot-deckbuilder` is the deterministic Godot 4.6.3 fixture. Its GDD,
scripts, generated `drift.json`, and `drift_report.md` deliberately exercise all
required finding statuses, including `CANDIDATE` and `PLANNED`. The React/Vite
showcase loads that report and exposes
finding selection, evidence anchors, filters, theme switching, reduced-motion
support, and plugin installation metadata:

```sh
npm run showcase:dev
npm run showcase:build
npm run showcase:lint
npm run showcase:test
```

The site is linked to `showcase/site/public/drift.json`; regenerate it only when
the fixture report changes. The embedded Godot Web build lives at
`showcase/site/public/game/index.html` (Showcase Web export).

## Release verification

Run the commands in [`release/README.md`](release/README.md). The release
manifest pins package, artifact, plugin, fixture, and showcase paths. Headless
Godot is not an MVP gate (see `docs/adr/0037-showcase-validation-without-headless.md`);
WSL/CI may skip the optional headless test. The Showcase Web export is present at
`showcase/site/public/game/index.html`.

Known boundary: the downloadable ZIP is the **Standalone plugin package**
(plugin + detector + lock data). First-run provisioning requires `uv`; local
scans stay offline afterward. See ADR 0038.

## Future MVP completion plan

Issues #4–#6 are done. Remaining closure (grilled 2026-07-18); tracked in #13:

1. **Close #7** — frozen showcase sample: pin `4.6.3`, committed Web export, playable iframe. No headless requirement.
2. **Close #8** — ship the **Standalone plugin package** (plugin + detector in one ZIP; first run may use `uv` for pinned deps).
3. **#9 / epic #1** — add the bring-or-grill **Setup skill**; rerun WSL acceptance (`pytest`, ruff, mypy, showcase); confirm version alignment; publish when approved.
4. Docs may note Cursor/MCP as future **host adapters**; they are not MVP ship targets.

Out of MVP: headless/CI Godot, thawing the showcase game, browser a11y matrix, auto-writing GDD files from detect-drift.

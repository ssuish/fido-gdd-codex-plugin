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

The local plugin is in `plugins/gdd-drift-detector`. Its launcher provisions a
versioned cache, installs from the repository lockfile, and runs the detector
without network access after dependencies are available. The launcher expects
the detector repository root; set `GDD_DETECTOR_ROOT` when invoking it outside
this checkout. The repository marketplace metadata is in `marketplace.json`.

Run the adapter directly from the repository:

```sh
python3 plugins/gdd-drift-detector/scripts/detect-drift.py \
  --project-root /path/to/godot-project \
  --detector-root /path/to/codex-hackathon
```

When the plugin and detector repository are separate, set `GDD_DETECTOR_ROOT`
instead. The first run may provision a cached environment; later scans run
without network or telemetry. The documented Codex surface is
`$gdd-drift-detector:detect-drift` (`/detect-drift` is the product shorthand).

## Showcase and fixture

`showcase/godot-deckbuilder` is the deterministic Godot 4.3 fixture. Its GDD,
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
the fixture report changes. The optional embedded Godot Web game is a release
artifact, not a prerequisite for the detector or report viewer.

## Release verification

Run the commands in [`release/README.md`](release/README.md). The release
manifest pins package, artifact, plugin, fixture, and showcase paths. The
current environment has no Godot 4.3 editor, so headless Godot and Web-export
checks remain explicit expected skips until that export is generated.

Known boundary: the downloadable ZIP is the Codex plugin adapter and install
metadata. It uses this detector checkout (or `GDD_DETECTOR_ROOT`) as its runtime
source; it is not a standalone bundled detector distribution.

## Future MVP completion plan

The implementation plan for issues #4–#9 is complete. Remaining MVP closure:

1. Install Godot 4.3.
2. Run fixture headless validation.
3. Generate the Web export at `showcase/site/public/game/index.html`.
4. Rerun release acceptance checks.
5. Add and run browser-level checks for loading, selection, keyboard access,
   mobile layout, themes, and reduced motion.
6. Decide whether the plugin ZIP should remain a repository adapter or become a
   standalone detector package.
7. Publish `main` when external release approval is available.

The repository is ready for local detector and report use. Godot runtime and
Web-export validation remain explicitly pending.

# GDD Drift Detector

Offline, local detector for drift between GDD entity markers and GDScript
implementation symbols. Current MVP ships four pieces: typed scan results,
evidence-rich Markdown/JSON reports, a Codex plugin adapter, and a linked
showcase backed by a traceable Godot deck-builder fixture.

## Quick start

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run python -m gdd_drift_detector --project-root /path/to/godot-project --json
npm run showcase:dev    # start linked showcase
npm run showcase:build  # build linked showcase
```

The Python package needs Python 3.11+ and uses `uv.lock` for reproducible
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

## Codex plugin

The local plugin is in `plugins/gdd-drift-detector`. Its launcher provisions a
versioned cache, installs from the repository lockfile, and runs the detector
without network access after dependencies are available. The launcher expects
the detector repository root; set `GDD_DETECTOR_ROOT` when invoking it outside
this checkout. The repository marketplace metadata is in `marketplace.json`.

## Showcase and fixture

`showcase/godot-deckbuilder` is the deterministic Godot 4.3 fixture. Its GDD,
scripts, generated `drift.json`, and `drift_report.md` deliberately exercise all
five finding statuses. The React/Vite showcase loads that report and exposes
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

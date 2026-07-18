# GDD Drift Detector

An offline, local detector for explicit GDD entity markers and GDScript class
declarations.

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run python -m gdd_drift_detector --project-root /path/to/godot-project --json
```

Conventional scans discover `GDD.md`, `design.md`, `docs/gdd/**/*.md`,
`docs/design/**/*.md`, and GDScript inputs. Use repeated `--gdd` and `--source`
arguments for explicit inputs. The Python seam is `scan(project_root, ScanConfig(...))`.
Successful scans write
`drift_report.md` and `drift.json` to the supplied project root.

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

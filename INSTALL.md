# Install Fido

Fido keeps coding sessions aligned to your GDD via **context refresh**, with an
optional explicit drift audit. Install the Codex plugin (recommended), the
`fido` CLI, or both. Scans and context refresh stay local: Fido does not upload
your GDD or source files.

**Do not run `uv tool install fido`.** On PyPI that name is a different package
(Yelp’s HTTP client). Fido is not published there yet — install from the
standalone ZIP path or from git (below).

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- A Godot 4 + GDScript project
- For the in-session workflow: OpenAI Codex with plugin support

## Codex plugin (standalone ZIP)

The ZIP includes the plugin, both local marketplace files, and the detector
runtime used by the launcher. First context refresh or scan provisions the
embedded detector environment with `uv`.

1. Download
   [`gdd-drift-detector.zip`](https://fido.quidor-adrean.workers.dev/downloads/gdd-drift-detector.zip)
   from the [live showcase](https://fido.quidor-adrean.workers.dev) (Install /
   docs), or from
   [`showcase/site/public/downloads/gdd-drift-detector.zip`](showcase/site/public/downloads/gdd-drift-detector.zip)
   in this repo.
2. Extract it to a durable directory.

### Codex CLI

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
codex plugin marketplace add /absolute/path/to/extracted-fido
codex
# run /plugins, select Fido, install
```

Replace `/absolute/path/to/extracted-fido` with the directory containing the
extracted ZIP. In the Codex session, run `/plugins`, choose the local Fido
marketplace, and install Fido. Start a new Codex session before using its
bundled skills.

No `GDD_DETECTOR_ROOT` setting is required for the standalone package layout.

### ChatGPT desktop

1. Extract the ZIP to a durable directory.
2. Restart ChatGPT.
3. Open ChatGPT Work mode or Codex, then open **Plugins**.
4. Select the local Fido marketplace and install **Fido**.
5. Start a new chat before asking Fido to refresh context or audit a project.

### After install

Prefer **`fido-context`** / `fido context` so the session already knows design
intent, gaps, and coverage. SessionStart runs
`fido context --update-only --if-stale` when the plugin is installed. Use
`setup-gdd` if the project is untracked, then re-run `fido context`. Run
`detect-drift` / `fido scan` only when you want a full audit report.

## CLI (from ZIP or git)

After extracting the standalone ZIP, install the console script from that
directory (the folder that contains `pyproject.toml`):

```sh
# Do NOT run: uv tool install fido  (PyPI name clash)
uv tool install /absolute/path/to/extracted-fido
fido context
```

Alternatives:

```sh
# From a git clone of this repo
uv tool install .
# or without a global tool:
uv sync
uv run fido context

# Direct from GitHub
uv tool install git+https://github.com/ssuish/gdd-plugin.git
```

`fido context` refreshes the game design context block in `AGENTS.md` (use
`--print` for stdout only). Optional cold start: `fido init`. For an explicit
design-fidelity audit: `fido scan --project-root . --json` (or the Codex
`detect-drift` skill).

The import package remains `gdd_drift_detector`
(`python -m gdd_drift_detector` routes to the same CLI).

## Launcher fallback

When PATH `fido` is unavailable, use the bundled scripts from an extracted ZIP
or checkout:

```sh
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/fido-context.py \
  --project-root /path/to/godot-project
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/detect-drift.py \
  --project-root /path/to/godot-project
```

## Mark your GDD

Only concepts with an **entity marker** count toward coverage. Unmarked prose
may appear as advisory candidates only — guidance is
`Add [entity: type] before this name to track it.`

Put design docs on a discovery path (or configure `drift.toml` later):

- `GDD.md` or `design.md` at the project root
- `docs/gdd/**/*.md` or `docs/design/**/*.md`

Marker syntax:

```markdown
[entity: system] Combat Loop

Core draw → spend energy → resolve cards.

[entity: system] [planned] Multiplayer Lobby

Intentionally out of scope for the current slice.
```

- `[entity: type] Name` — tracked; name must follow marker (affects coverage)
- `[planned]` — tracked but excluded from the coverage denominator

Markers are prefix-only in this MVP. A marker placed after a heading name has
no tracked name and produces a Scan advisory; it does not affect coverage.

If you do not have a GDD yet, use the **`setup-gdd`** skill in Codex (bring an
existing doc, or grill a draft in chat). The skill does not silently write files;
you save the draft yourself, then re-run `fido context`.

## Read the results

| Status | Meaning |
|--------|---------|
| `MATCHED` | Tracked entity has an exact (or accepted) implementation match |
| `MISSING` | Tracked entity has no implementation match |
| `RENAMED?` | One unique fuzzy candidate — review before treating as matched |
| `ORPHANED` | Top-level script/class not represented by a tracked entity |
| `PLANNED` | Marked `[planned]` — outside the current coverage slice |

Ownership next actions:

| Status | Owner action |
|--------|--------------|
| `MISSING` | Implement or unmark/remove the tracked entity |
| `RENAMED?` | Add `accepted_mappings` or reject the candidate; mapping required for a match |
| `ORPHANED` | Track, exclude in `drift.toml`, or remove the implementation symbol |
| `PLANNED` | Keep outside current coverage slice until ready |

**Accepted renames** live in optional project-local `drift.toml` (read-only for
the detector — edit it yourself). Paste this starter only when you need discovery
overrides or accepted mappings. Fido never creates or edits it:

```toml
[discovery]
gdd = ["GDD.md"]
sources = ["**/*.gd"]
exclude = [".godot/**"]

[accepted_mappings]
# "GDD Name" = "implementation_name"
```

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| First run fails / missing deps | Install [`uv`](https://docs.astral.sh/uv/) and retry; provisioning needs network once |
| Coverage `N/A` or “untracked” | Not marked yet; put `[entity: type]` before intended names, or run `setup-gdd` then save a GDD on a discovery path |
| Empty-marker advisory | Put `[entity: type]` before the intended name; heading-suffix markers are not tracked |
| Wrong files scanned | Pass `--gdd` / `--source`, or set `[discovery]` in `drift.toml` |
| Want rename to count as matched | Add an entry under `[accepted_mappings]` in `drift.toml` |

# Fido

**Local design-fidelity checks for your game designs.**

Fido keeps AI coding sessions aligned to your marked game design document (GDD)
by refreshing a **game design context block**, and can run an explicit
design-fidelity audit when you need full findings. Today that means **Godot 4 +
GDScript** via a **Codex plugin** and a `fido` CLI; more engines are planned.
Work runs on your machine. After a one-time `uv` provision, the detector does
not upload project files or call the network.

The distributable Python package and console command are **`fido`**. Technical
plugin id and paths remain `gdd-drift-detector` (ZIP name,
`$gdd-drift-detector:…` skill prefixes, import package `gdd_drift_detector`).

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- A Godot 4 project with GDScript sources
- For the in-session workflow: [OpenAI Codex](https://openai.com/codex/) with
  plugin support

## Who this is for

- Game developers who keep (or want) a marked Markdown GDD next to the project
- **Godot 4 + GDScript** projects (current supported stack)
- Users who want session context via `fido context` / `fido-context`, with
  `/detect-drift` available as an explicit audit

This is **not** a Godot editor plugin. Cursor and MCP hosts are future adapters.

---

## For game developers

### Install the Codex plugin

**Option A — Standalone ZIP (recommended)**

1. Download
   [`gdd-drift-detector.zip`](https://fido.quidor-adrean.workers.dev/downloads/gdd-drift-detector.zip)
   from the [live showcase](https://fido.quidor-adrean.workers.dev), or from
   [`showcase/site/public/downloads/gdd-drift-detector.zip`](showcase/site/public/downloads/gdd-drift-detector.zip)
   in this repo.
2. Extract it to a durable directory.
3. Install Codex CLI if needed, then add the extracted directory as a local
   marketplace:

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
codex plugin marketplace add /absolute/path/to/extracted-fido
codex
# run /plugins, select Fido, install
```

Replace the placeholder with the extracted ZIP directory. First context refresh
or scan may take a moment while `uv` provisions a cached environment from the
embedded lockfile. Start a new Codex session after installing.

**ChatGPT desktop — local marketplace**

1. Extract the ZIP to a durable directory and restart ChatGPT.
2. Open ChatGPT Work mode or Codex, then open **Plugins**.
3. Select the local Fido marketplace and install **Fido**.
4. Start a new chat before using the plugin.

The ZIP is discovered through its local marketplace metadata. The full handoff
is in [`INSTALL.md`](INSTALL.md).

**Option B — From this repository**

Clone the repo and add the root marketplace manifest:

```sh
git clone <this-repo-url>
cd codex-hackathon
codex plugin marketplace add /absolute/path/to/codex-hackathon
```

`GDD_DETECTOR_ROOT` is an optional fallback if you run the launcher outside the
standalone package layout; most users do not need it.

### Install the CLI

**Do not run `uv tool install fido`.** On PyPI that name is a different package.
Install from the extracted ZIP (directory with `pyproject.toml`), a clone, or
git:

```sh
uv tool install /absolute/path/to/extracted-fido
# or: uv tool install .
# or: uv tool install git+https://github.com/ssuish/gdd-plugin.git
```

Then from your Godot project root:

```sh
fido context          # refresh AGENTS.md game design context block
fido init             # bootstrap AGENTS.md delimiters (optional cold start)
fido scan --project-root . --json   # explicit drift audit (secondary)
```

`fido context` is the default daily path: it writes or refreshes the delimited
context block in `AGENTS.md` so coding sessions already know design intent,
gaps, and coverage. Prefer it over a full drift audit unless you need deep
findings. Full handoff: [`INSTALL.md`](INSTALL.md).

### Refresh session context

In Codex, with your Godot project as the working context:

1. Prefer `$gdd-drift-detector:setup-gdd` once if the project is untracked (no
   usable GDD yet).
2. Run `$gdd-drift-detector:fido-context` (or ask Codex to refresh Fido context).
   SessionStart already runs `fido context --update-only --if-stale` when the
   plugin is installed.

From the CLI peer:

```sh
fido context --project-root /path/to/godot-project
```

Useful flags: `--print` (stdout only), `--update-only`, `--if-stale`, `--fresh`,
`--verbose`.

### Mark your GDD

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

### Run an explicit drift audit

When you want full findings (not just session context), use the secondary audit
path:

1. In Codex: `$gdd-drift-detector:detect-drift` (shorthand: `/detect-drift`).
2. Or CLI: `fido scan --project-root /path/to/godot-project --json`.

The scan is read-only for GDD, GDScript, and `drift.toml`. It writes only:

```text
<project-root>/drift_report.md
<project-root>/drift.json
```

### Read the results

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

Reports include paths, line anchors, short excerpts, containment context,
coverage summary, priority findings, and next actions.

**Accepted renames** live in optional project-local `drift.toml` (read-only for
the detector — edit it yourself):

```toml
[discovery]
gdd = ["design/**/*.md"]
sources = ["game/**/*.gd"]
exclude = ["game/generated/**"]

[accepted_mappings]
"Design Name" = "implementation_name"
```

Paste this starter into your project as `drift.toml` only when you need
discovery overrides or accepted mappings. Fido never creates or edits it:

```toml
[discovery]
gdd = ["GDD.md"]
sources = ["**/*.gd"]
exclude = [".godot/**"]

[accepted_mappings]
# "GDD Name" = "implementation_name"
```

### CLI peer path

After `uv tool install /absolute/path/to/extracted-fido` (or git/clone
install), the console script is on your `PATH`. From a checkout without a tool
install:

```sh
uv sync
uv run fido context --project-root /path/to/godot-project
uv run fido scan --project-root /path/to/godot-project --json
```

From an extracted standalone ZIP, the bundled launchers still work when PATH
`fido` is unavailable:

```sh
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/fido-context.py \
  --project-root /path/to/godot-project
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/detect-drift.py \
  --project-root /path/to/godot-project
```

The import package remains `gdd_drift_detector` (`python -m gdd_drift_detector`
is equivalent to the `fido` router). Explicit inputs when defaults do not fit:

```sh
fido scan \
  --project-root /path/to/godot-project \
  --gdd design/gameplay.md \
  --source game/player.gd \
  --json
```

Python API:

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
print(result.state, result.summary.coverage_percent)
```

### Troubleshooting

| Problem | What to try |
|---------|-------------|
| First run fails / missing deps | Install [`uv`](https://docs.astral.sh/uv/) and retry; provisioning needs network once |
| Coverage `N/A` or “untracked” | Not marked yet; put `[entity: type]` before intended names, or run `setup-gdd` then save a GDD on a discovery path |
| Empty-marker advisory | Put `[entity: type]` before the intended name; heading-suffix markers are not tracked |
| Wrong files scanned | Pass `--gdd` / `--source`, or set `[discovery]` in `drift.toml` |
| Want rename to count as matched | Add an entry under `[accepted_mappings]` in `drift.toml` |

---

## Try the showcase

This repo ships a frozen Godot 4.6.3 deck-builder fixture and a linked React
site that walks through real Fido findings beside a playable Web export.

Live site: [https://fido.quidor-adrean.workers.dev](https://fido.quidor-adrean.workers.dev).
Or run locally:

```sh
npm run showcase:dev
```

Artifacts live under `showcase/site/public/` (`drift.json`, `game/`, downloads).
On the live site, `game/` is served from R2 via Worker `fido` (wasm exceeds the
Workers static-asset size limit); local dev still uses `public/game/` directly.
The fixture project is `showcase/godot-deckbuilder/`. Operator notes for
Cloudflare Workers + R2 deploy live in [`release/README.md`](release/README.md).

---

## For contributors

High-level layout:

| Path | Role |
|------|------|
| `src/gdd_drift_detector/` | Shared detector engine (CLI + `scan()`) |
| `plugins/gdd-drift-detector/` | Codex host adapter for Fido (skills + launcher) |
| `showcase/` | Demo site + Godot fixture |
| `tests/` | Automated tests |
| `release/` | Version pins and release verification |

Development setup, checks, ZIP rebuild, and PR expectations are in
[**CONTRIBUTING.md**](CONTRIBUTING.md). Product vocabulary lives in
[`CONTEXT.md`](CONTEXT.md). Please follow the
[Code of Conduct](CODE_OF_CONDUCT.md). Security reports:
[SECURITY.md](SECURITY.md).

Rebuild the downloadable standalone plugin package after packaging changes:

```sh
python3 scripts/build_standalone_plugin_zip.py
```

---

## License

Licensed under the [Apache License 2.0](LICENSE).

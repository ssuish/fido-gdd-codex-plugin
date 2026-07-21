# Install Fido

Fido keeps coding sessions aligned to your GDD via **context refresh**, with an
optional explicit drift audit. Install the `fido` CLI, the Codex plugin, or
both. Scans and context refresh stay local: Fido does not upload your GDD or
source files.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your `PATH`
- A Godot 4 + GDScript project
- For the in-session workflow: OpenAI Codex with plugin support

## CLI (`uv tool install`)

```sh
uv tool install fido
fido context
```

`fido context` refreshes the game design context block in `AGENTS.md` (use
`--print` for stdout only). Optional cold start: `fido init`. For an explicit
design-fidelity audit: `fido scan --project-root . --json` (or the Codex
`detect-drift` skill).

From a checkout without a tool install: `uv sync` then `uv run fido …`. The
import package remains `gdd_drift_detector`
(`python -m gdd_drift_detector` routes to the same CLI).

## Codex plugin (standalone ZIP)

The ZIP includes the plugin, both local marketplace files, and the detector
runtime used by the launcher. First context refresh or scan provisions the
embedded detector environment with `uv`.

### Codex CLI

Extract the ZIP to a durable directory, then run:

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

## Launcher fallback

When PATH `fido` is unavailable, use the bundled scripts from an extracted ZIP
or checkout:

```sh
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/fido-context.py \
  --project-root /path/to/godot-project
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/detect-drift.py \
  --project-root /path/to/godot-project
```

See README for prefix-only Entity markers, pasteable `drift.toml`, advisory
guidance, and ownership next actions.

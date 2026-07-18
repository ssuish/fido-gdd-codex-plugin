# MVP release verification

Run from repository root:

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
npm run showcase:build
# Run the plugin-creator validator when that skill is installed:
python3 "$CODEX_PLUGIN_CREATOR_ROOT/scripts/validate_plugin.py" plugins/gdd-drift-detector
```

`release/manifest.json` pins detector, plugin, fixture, and showcase versions. Godot Web
export must be generated with the pinned `showcase/godot-deckbuilder/.godot-version` before
publishing. Set `CODEX_PLUGIN_CREATOR_ROOT` to the plugin-creator skill directory for the
optional validator command. Acceptance tests skip Godot runtime checks when Godot is not
installed and skip Web validation until `public/game/index.html` exists.

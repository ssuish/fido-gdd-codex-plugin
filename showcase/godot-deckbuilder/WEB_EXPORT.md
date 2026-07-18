# Web export

Godot version: `4.6.3`.

After installing that pinned editor and matching Web export templates, export the
fixture into the showcase site (canonical embed path):

```sh
godot --headless --path showcase/godot-deckbuilder \
  --export-release godot-showcase showcase/site/public/game/godot-showcase.html
cp showcase/site/public/game/godot-showcase.html \
  showcase/site/public/game/index.html
```

The site iframe loads `index.html`; keep it as a copy of the Godot HTML shell so
asset basenames stay `godot-showcase.*`. Do not keep a second export tree under
`showcase/godot-deckbuilder/web/`.

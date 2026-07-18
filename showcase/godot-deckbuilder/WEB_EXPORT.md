# Web export

Godot version: `4.6.3` (**Fixture Godot pin**).

The showcase game is a **frozen sample**. MVP showcase validation is pin
metadata, this committed **Showcase Web export**, and a playable iframe
encounter — not headless Godot (see `docs/adr/0037-showcase-validation-without-headless.md`).

When the frozen sample must change, use a disposable Windows **Godot build
sandbox**, then sync intentional outputs back into this monorepo. After
installing the pinned editor and matching Web export templates, export into the
showcase site (canonical embed path):

```sh
godot --path showcase/godot-deckbuilder \
  --export-release godot-showcase showcase/site/public/game/godot-showcase.html
cp showcase/site/public/game/godot-showcase.html \
  showcase/site/public/game/index.html
```

The site iframe loads `index.html`; keep it as a copy of the Godot HTML shell so
asset basenames stay `godot-showcase.*`. Do not keep a second export tree under
`showcase/godot-deckbuilder/web/`.

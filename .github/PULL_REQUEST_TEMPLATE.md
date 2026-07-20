## Summary

<!-- What changed and why it matters. Prefer Fido product language; keep
     technical id gdd-drift-detector for package/plugin paths. -->

-

## Test plan

- [ ] `uv run pytest`
- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy`
- [ ] Showcase touched: `npm run showcase:lint` / `showcase:test` / `showcase:build`
- [ ] Packaging/plugin/lockfile touched: rebuilt and committed
      `showcase/site/public/downloads/gdd-drift-detector.zip`
- [ ] Release-facing change: updated `CHANGELOG.md` under `[Unreleased]` (or
      dated version section when cutting a release)

## Notes

<!-- Link related issue. Call out release manifest, security, or Install
     handoff impact. Screenshots for visible showcase UI changes. -->

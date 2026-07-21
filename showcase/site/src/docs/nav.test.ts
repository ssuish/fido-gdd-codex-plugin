import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DOCS_NAV, nextTabIndex, resolveActiveSection } from "./nav.ts";

describe("docs nav helpers", () => {
  it("resolves the earliest visible nav section", () => {
    assert.equal(resolveActiveSection(["after-install", "cli"]), "cli");
    assert.equal(resolveActiveSection([]), DOCS_NAV[0].id);
  });

  it("cycles tab indices for keyboard navigation", () => {
    assert.equal(nextTabIndex(0, "ArrowRight", 3), 1);
    assert.equal(nextTabIndex(2, "ArrowRight", 3), 0);
    assert.equal(nextTabIndex(0, "ArrowLeft", 3), 2);
    assert.equal(nextTabIndex(1, "Home", 3), 0);
    assert.equal(nextTabIndex(1, "End", 3), 2);
  });
});

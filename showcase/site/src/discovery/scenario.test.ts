import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it } from "node:test";
import {
  RELATED_FINDING_NAME,
  RELATED_FINDING_STATUS,
  SHOW_RELATED_FINDING_LABEL,
  findRelatedFindingIndex,
} from "./scenario.ts";
import type { Finding } from "../types.ts";

const root = join(dirname(fileURLToPath(import.meta.url)), "../../public");
const report = JSON.parse(readFileSync(join(root, "drift.json"), "utf8")) as {
  findings: Finding[];
};

describe("showcase scenario", () => {
  it("resolves Shield MISSING from fixture-generated drift.json", () => {
    const index = findRelatedFindingIndex(report.findings);
    assert.ok(index >= 0);
    const finding = report.findings[index];
    assert.equal(finding.status, RELATED_FINDING_STATUS);
    assert.equal(finding.tracked_entity?.name, RELATED_FINDING_NAME);
    assert.equal(finding.evidence?.gdd_path, "GDD.md");
    assert.equal(finding.code_entity, null);
  });

  it("exports the manual related-finding label", () => {
    assert.equal(SHOW_RELATED_FINDING_LABEL, "Show related finding");
  });

  it("returns -1 when the fixture row is absent", () => {
    assert.equal(findRelatedFindingIndex([]), -1);
  });
});

/**
 * Showcase scenario mapping for guided discovery.
 *
 * The frozen Godot Web export does not expose a reliable interaction bridge
 * (no postMessage / JS bridge). The website therefore owns an honest manual
 * "Show related finding" handoff. The connection is a curated showcase
 * scenario, not an automatically detected live game event.
 *
 * Related finding is resolved only from fixture-generated drift.json fields.
 */
import type { Finding } from "../types.ts";

/** Fixture-tracked card that is deliberately missing from implementation. */
export const RELATED_FINDING_NAME = "Shield";
export const RELATED_FINDING_STATUS = "MISSING";

export const SHOW_RELATED_FINDING_LABEL = "Show related finding";

export const SCENARIO_CAPTION =
  "Showcase scenario: the GDD tracks Shield, but this slice ships Block instead. The link is curated for the demo, not a live game event.";

export const HINT_COPY = {
  invite: "Play the encounter freely. Cards in this slice are the design under test.",
  related: "A related drift finding exists for this showcase scenario.",
  route: "Use Show related finding to open the Shield evidence.",
} as const;

export type HintKey = keyof typeof HINT_COPY;

/**
 * Resolve the related showcase finding from fixture report findings only.
 * Returns -1 when the expected fixture row is absent.
 */
export function findRelatedFindingIndex(findings: Finding[]): number {
  return findings.findIndex(
    (finding) =>
      finding.status === RELATED_FINDING_STATUS &&
      finding.tracked_entity?.name === RELATED_FINDING_NAME,
  );
}

export function findingLabel(finding: Finding): string {
  return finding.tracked_entity?.name ?? finding.code_entity?.name ?? "Unknown";
}

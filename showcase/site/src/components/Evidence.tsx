import type { Finding } from "../types";
import { statusCopy } from "../types";

function EvidenceLine({
  label,
  value,
  excerpt,
  anchor,
}: {
  label: string;
  value: string;
  excerpt: string | null;
  anchor: string;
}) {
  return (
    <div id={anchor} className="evidence-line">
      <span>{label}</span>
      <div>
        <a href={`#${anchor}`}>
          <strong>{value}</strong>
        </a>
        {excerpt && <code>{excerpt}</code>}
      </div>
    </div>
  );
}

export function Evidence({ finding, revealed }: { finding: Finding; revealed: boolean }) {
  const evidence = finding.evidence;
  return (
    <div
      id="finding-evidence"
      className={`evidence ${revealed ? "evidence-revealed" : ""}`}
      aria-live="polite"
    >
      <h3>{statusCopy[finding.status] ?? finding.status}</h3>
      {evidence?.gdd_path && (
        <EvidenceLine
          label="GDD"
          value={`${evidence.gdd_path}:${evidence.gdd_line}`}
          excerpt={evidence.gdd_excerpt}
          anchor="gdd-evidence"
        />
      )}
      {evidence?.code_path && (
        <EvidenceLine
          label="CODE"
          value={`${evidence.code_path}:${evidence.code_line}`}
          excerpt={evidence.code_excerpt}
          anchor="implementation-evidence"
        />
      )}
      {!evidence?.code_path && finding.status === "MISSING" && (
        <div className="evidence-line">
          <span>CODE</span>
          <div>
            <strong>No matching implementation</strong>
            <code>Tracked in GDD; absent from the current GDScript slice.</code>
          </div>
        </div>
      )}
      {evidence?.containment_path.length ? (
        <div className="containment">
          <span>CONTAINMENT</span>
          <a href="#game-fixture">
            <strong>{evidence.containment_path.join(" / ")}</strong>
            <small>Show related game concept</small>
          </a>
        </div>
      ) : null}
    </div>
  );
}

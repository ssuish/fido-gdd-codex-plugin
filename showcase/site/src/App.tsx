import { useEffect, useMemo, useState } from "react";

type Evidence = {
  gdd_path: string | null;
  gdd_line: number | null;
  code_path: string | null;
  code_line: number | null;
  code_symbol_path: string | null;
  containment_path: string[];
  gdd_excerpt: string | null;
  code_excerpt: string | null;
};

type Finding = {
  status: string;
  tracked_entity: { name: string; entity_type: string } | null;
  code_entity: { name: string; kind: string; path: string } | null;
  evidence: Evidence | null;
};

type Report = {
  state: "COMPLETE" | "PARTIAL";
  findings: Finding[];
  candidates: { name: string; path: string; line: number }[];
  summary: {
    coverage_percent: number | null;
    matched: number;
    total: number;
    priority_findings: { status: string; name: string }[];
  };
  warnings: { path: string; reason: string; impact: string }[];
};

const statusCopy: Record<string, string> = {
  MATCHED: "Implementation found",
  MISSING: "Tracked concept has no exact implementation",
  "RENAMED?": "Possible implementation rename",
  ORPHANED: "Implementation is not represented in GDD",
  PLANNED: "Intentionally outside current slice",
};

function App() {
  const [report, setReport] = useState<Report | null>(null);
  const [selected, setSelected] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [gameAvailable, setGameAvailable] = useState(false);

  useEffect(() => {
    fetch("./drift.json")
      .then((response) => {
        if (!response.ok) throw new Error(`Report request failed: ${response.status}`);
        return response.json() as Promise<Report>;
      })
      .then(setReport)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    fetch("./game/index.html", { method: "HEAD" })
      .then((response) => setGameAvailable(response.ok))
      .catch(() => setGameAvailable(false));
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  const findings = useMemo(() => report?.findings ?? [], [report]);
  const selectedFinding = findings[selected] ?? null;

  if (error) return <StateMessage title="Report unavailable" body={error} />;
  if (!report) return <StateMessage title="Loading fixture report" body="Reading generated drift.json..." loading />;

  const coverage = report.summary.coverage_percent === null ? "N/A" : `${report.summary.coverage_percent.toFixed(0)}%`;

  return (
    <main className="site-shell">
      <header className="topbar">
        <a className="wordmark" href="./">Fido</a>
        <nav aria-label="Primary navigation">
          <a href="#walkthrough">Walkthrough</a>
          <a href="#install">Install</a>
          <button className="theme-button" type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
        </nav>
      </header>

      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow">LOCAL / EVIDENCE FIRST</p>
          <h1 id="hero-title">Fido</h1>
          <p className="hero-lede">Local design-fidelity checks for your game designs. Today: Godot 4 + GDScript via Codex, on your machine.</p>
          <a className="primary-button" href="#install">Install the plugin</a>
        </div>
        <div className="hero-signal" aria-label="Current fixture scan summary">
          <div className="signal-line"><span>FIXTURE</span><strong>DECK BUILDER / THREE ENCOUNTERS</strong></div>
          <div className="signal-number">{coverage}</div>
          <div className="signal-caption">active tracked coverage</div>
          <div className="signal-meta"><span>{report.summary.matched} matched</span><span>{report.summary.total} evaluated</span><span>{report.state}</span></div>
        </div>
      </section>

      <section id="walkthrough" className="walkthrough" aria-labelledby="walkthrough-title">
        <div className="section-heading">
          <p className="eyebrow">THE PROOF</p>
          <h2 id="walkthrough-title">Play the slice. Inspect the finding.</h2>
          <p>Every panel below comes from the same Godot fixture. Select a result to see the source locations that make it useful.</p>
        </div>
        <div className="proof-grid">
          <article id="game-fixture" className="game-panel panel">
            <div className="panel-header"><span>SHOWCASE GAME</span><span className="live-state">GODOT WEB</span></div>
            {gameAvailable ? (
              <iframe className="game-embed" src="./game/index.html" title="Playable Godot deck-builder fixture" />
            ) : (
              <div className="game-frame game-placeholder">
                <div className="game-title">DECK BUILDER</div>
                <p>Web export is not present in this development build.</p>
                <code>godot --headless --export-release Web</code>
              </div>
            )}
          </article>

          <article className="report-panel panel">
            <div className="panel-header"><span>GENERATED DRIFT REPORT</span><span className={`state-badge ${report.state.toLowerCase()}`}>{report.state}</span></div>
            <div id="implementation-evidence" className="finding-list" role="listbox" aria-label="Drift findings">
              {findings.map((finding, index) => (
                <button className={`finding-row ${selected === index ? "selected" : ""}`} key={`${finding.status}-${finding.tracked_entity?.name ?? finding.code_entity?.name}`} type="button" role="option" aria-selected={selected === index} onClick={() => setSelected(index)}>
                  <span className={`status status-${finding.status.toLowerCase().replace("?", "")}`}>{finding.status}</span>
                  <span className="finding-name">{finding.tracked_entity?.name ?? finding.code_entity?.name}</span>
                  <span className="finding-kind">{finding.tracked_entity?.entity_type ?? finding.code_entity?.kind}</span>
                </button>
              ))}
            </div>
            {report.candidates.length > 0 && <div className="candidate-strip"><span>CANDIDATE</span>{report.candidates.map((candidate) => <strong key={`${candidate.path}:${candidate.line}`}>{candidate.name}</strong>)}</div>}
            {report.warnings.length > 0 && <div className="warning-banner">{report.warnings.length} warning(s) qualify this scan. Read full report.</div>}
            {selectedFinding ? <Evidence finding={selectedFinding} /> : <div className="empty-state">No priority findings in this scan.</div>}
          </article>
        </div>
      </section>

      <section className="install-section" id="install" aria-labelledby="install-title">
        <div>
          <p className="eyebrow">LOCAL INSTALL</p>
          <h2 id="install-title">Keep project content on your machine.</h2>
          <p>Download the standalone Codex plugin ZIP (requires <code>uv</code> on first run), use <code>setup-gdd</code> to prepare a GDD source set, then run <code>detect-drift</code> for a local report you can commit beside your work.</p>
        </div>
        <div className="install-command">
          <code>codex plugin marketplace add ./marketplace.json</code>
          <div className="install-actions">
            <a className="download-link" href="./downloads/gdd-drift-detector.zip" download>Download plugin ZIP</a>
            <a className="manifest-link" href="./marketplace.json" download>Download marketplace manifest</a>
            <button type="button" onClick={() => navigator.clipboard?.writeText("codex plugin marketplace add ./marketplace.json")}>Copy command</button>
          </div>
        </div>
      </section>

      <footer><span>Fido</span><span>Local design-fidelity checks for your game designs.</span></footer>
    </main>
  );
}

function Evidence({ finding }: { finding: Finding }) {
  const evidence = finding.evidence;
  return (
    <div className="evidence" aria-live="polite">
      <h3>{statusCopy[finding.status] ?? finding.status}</h3>
      {evidence?.gdd_path && <EvidenceLine label="GDD" value={`${evidence.gdd_path}:${evidence.gdd_line}`} excerpt={evidence.gdd_excerpt} anchor="gdd-evidence" />}
      {evidence?.code_path && <EvidenceLine label="CODE" value={`${evidence.code_path}:${evidence.code_line}`} excerpt={evidence.code_excerpt} anchor="implementation-evidence" />}
      {evidence?.containment_path.length ? <div className="containment"><span>CONTAINMENT</span><a href="#game-fixture"><strong>{evidence.containment_path.join(" / ")}</strong><small>Show related game concept</small></a></div> : null}
    </div>
  );
}

function EvidenceLine({ label, value, excerpt, anchor }: { label: string; value: string; excerpt: string | null; anchor: string }) {
  return <div id={anchor} className="evidence-line"><span>{label}</span><div><a href={`#${anchor}`}><strong>{value}</strong></a>{excerpt && <code>{excerpt}</code>}</div></div>;
}

function StateMessage({ title, body, loading = false }: { title: string; body: string; loading?: boolean }) {
  return <main className="state-message"><div className={loading ? "loader" : "error-mark"}>{loading ? "" : "!"}</div><h1>{title}</h1><p>{body}</p></main>;
}

export default App;

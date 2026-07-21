/**
 * Compact GDD → evidence route for the landing hero.
 * Stable hooks: data-trace-route, data-trace-marker, data-trace-node, data-trace-metric.
 * Visible by default; LandingMotion only hides then animates when motion is allowed.
 */
export function FidelityTrace() {
  return (
    <svg
      className="fidelity-trace"
      viewBox="0 0 360 220"
      role="img"
      aria-labelledby="fidelity-trace-title fidelity-trace-desc"
      focusable="false"
    >
      <title id="fidelity-trace-title">Fidelity trace</title>
      <desc id="fidelity-trace-desc">
        Route from GDD intent through a local scan to GDScript evidence.
      </desc>

      <g className="fidelity-trace-node" data-trace-node="gdd">
        <rect x="12" y="72" width="88" height="56" rx="8" className="fidelity-trace-card" />
        <text x="56" y="96" textAnchor="middle" className="fidelity-trace-label">
          GDD
        </text>
        <text x="56" y="114" textAnchor="middle" className="fidelity-trace-sub">
          intent
        </text>
      </g>

      <path
        data-trace-route
        className="fidelity-trace-route"
        d="M100 100 C 150 100, 160 40, 210 40 S 270 100, 272 100"
        fill="none"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={0}
      />

      <g className="fidelity-trace-node" data-trace-node="scan">
        <circle cx="210" cy="40" r="18" className="fidelity-trace-card" />
        <text x="210" y="44" textAnchor="middle" className="fidelity-trace-label">
          scan
        </text>
      </g>

      <g className="fidelity-trace-node" data-trace-node="code">
        <rect x="260" y="72" width="88" height="56" rx="8" className="fidelity-trace-card" />
        <text x="304" y="96" textAnchor="middle" className="fidelity-trace-label">
          code
        </text>
        <text x="304" y="114" textAnchor="middle" className="fidelity-trace-sub">
          evidence
        </text>
      </g>

      <circle
        data-trace-marker
        className="fidelity-trace-marker"
        cx="100"
        cy="100"
        r="5"
        opacity={0}
      />

      <g className="fidelity-trace-metrics" aria-hidden="true">
        <text data-trace-metric x="56" y="168" textAnchor="middle" className="fidelity-trace-metric">
          tracked
        </text>
        <text
          data-trace-metric
          x="180"
          y="198"
          textAnchor="middle"
          className="fidelity-trace-metric"
        >
          matched
        </text>
        <text
          data-trace-metric
          x="304"
          y="168"
          textAnchor="middle"
          className="fidelity-trace-metric"
        >
          findings
        </text>
      </g>
    </svg>
  );
}

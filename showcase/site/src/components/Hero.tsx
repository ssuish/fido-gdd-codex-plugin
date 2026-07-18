type HeroProps = {
  coverage: string;
  matched: number;
  total: number;
  state: string;
};

export function Hero({ coverage, matched, total, state }: HeroProps) {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-copy">
        <h1 id="hero-title">Fido</h1>
        <p className="hero-promise">Your game changed. Did the design stay in sync?</p>
        <p className="hero-lede">
          Local design-fidelity checks for Godot GDScript teams still iterating on design and code.
        </p>
        <div className="hero-actions">
          <a className="primary-button" href="#walkthrough">
            Play the showcase
          </a>
          <a className="secondary-button" href="#install">
            Install the plugin
          </a>
        </div>
      </div>
      <aside className="hero-signal" aria-label="Current fixture scan summary">
        <div className="signal-line">
          <span>FIXTURE</span>
          <strong>DECK BUILDER / THREE ENCOUNTERS</strong>
        </div>
        <div className="signal-number">{coverage}</div>
        <div className="signal-caption">active tracked coverage</div>
        <div className="signal-meta">
          <span>{matched} matched</span>
          <span>{total} evaluated</span>
          <span className="live-scan">{state}</span>
        </div>
      </aside>
    </section>
  );
}

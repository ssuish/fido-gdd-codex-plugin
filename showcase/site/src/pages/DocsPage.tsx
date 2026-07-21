import { SiteHeader } from "../components/SiteHeader";
import { SiteFooter } from "../components/SiteFooter";
import { DocsSidebar } from "../components/docs/DocsSidebar";
import { CodeBlock } from "../components/docs/CodeBlock";
import { CodeTabs } from "../components/docs/CodeTabs";
import { DocsDisclosure } from "../components/docs/DocsDisclosure";
import { marketplaceCommand } from "../discovery/state";
import { useTheme } from "../hooks/useTheme";

const CLI_INSTALL = `uv tool install fido
fido context`;

const CLI_CHECKOUT = `uv sync
uv run fido context`;

const CODEX_CLI = `curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex
codex plugin marketplace add /absolute/path/to/extracted-fido
codex
# run /plugins, select Fido, install`;

const LAUNCHER_FALLBACK = `python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/fido-context.py \\
  --project-root /path/to/godot-project
python /absolute/path/to/extracted-fido/plugins/gdd-drift-detector/scripts/detect-drift.py \\
  --project-root /path/to/godot-project`;

export function DocsPage() {
  const { theme, toggleTheme } = useTheme();

  return (
    <main className="site-shell docs-shell">
      <a className="skip-link" href="#docs-content">
        Skip to content
      </a>
      <SiteHeader
        theme={theme}
        onToggleTheme={toggleTheme}
        homeHref="../"
        navItems={[
          { href: "../#walkthrough", label: "Proof" },
          { href: "./", label: "Install", current: true },
        ]}
      />

      <header className="docs-hero">
        <p className="eyebrow">INSTALLATION GUIDE</p>
        <h1>Install Fido</h1>
        <p className="hero-lede">
          Fido keeps coding sessions aligned to your GDD via context refresh, with an optional
          explicit drift audit. Install the <code>fido</code> CLI, the Codex plugin, or both.
          Scans and context refresh stay local: Fido does not upload your GDD or source files.
        </p>
      </header>

      <div className="docs-layout" id="docs-content">
        <DocsSidebar />
        <DocsSidebar variant="mobile" />

        <div className="docs-main">
          <section className="docs-section" id="prerequisites" aria-labelledby="prerequisites-title">
            <h2 id="prerequisites-title">Prerequisites</h2>
            <div className="docs-prose">
              <ul>
                <li>
                  <a href="https://docs.astral.sh/uv/" target="_blank" rel="noreferrer">
                    uv
                  </a>{" "}
                  on your PATH
                </li>
                <li>A Godot 4 + GDScript project</li>
                <li>For the in-session workflow: OpenAI Codex with plugin support</li>
              </ul>
            </div>
          </section>

          <section className="docs-section" id="cli" aria-labelledby="cli-title">
            <h2 id="cli-title">CLI</h2>
            <div className="docs-prose">
              <p>
                Install the distributable package, then refresh game design context.{" "}
                <code>fido context</code> refreshes the game design context block in{" "}
                <code>AGENTS.md</code> (use <code>--print</code> for stdout only). Project cold
                start: <code>fido init</code>. For an explicit design-fidelity audit:{" "}
                <code>fido scan --project-root . --json</code> (or the Codex{" "}
                <code>detect-drift</code> skill).
              </p>
            </div>
            <CodeTabs
              label="CLI install path"
              tabs={[
                {
                  id: "tool-install",
                  label: "uv tool install",
                  code: CLI_INSTALL,
                },
                {
                  id: "checkout",
                  label: "From checkout",
                  code: CLI_CHECKOUT,
                },
              ]}
            />
            <div className="docs-prose">
              <p>
                The import package remains <code>gdd_drift_detector</code> (
                <code>python -m gdd_drift_detector</code> routes to the same CLI).
              </p>
            </div>
          </section>

          <section className="docs-section" id="plugin-zip" aria-labelledby="plugin-zip-title">
            <h2 id="plugin-zip-title">Codex plugin (standalone ZIP)</h2>
            <div className="docs-prose">
              <p>
                The ZIP includes the plugin, both local marketplace files, and the detector
                runtime used by the launcher. First context refresh or scan provisions the
                embedded detector environment with <code>uv</code>.
              </p>
              <p>
                Download the package from the showcase, extract it to a durable directory, then
                add that directory as a local Codex marketplace.
              </p>
            </div>
            <p>
              <a className="primary-button" href="../downloads/gdd-drift-detector.zip" download>
                Download plugin ZIP
              </a>
            </p>
            <CodeBlock code={marketplaceCommand()} label="marketplace" />
          </section>

          <section className="docs-section" id="codex-cli" aria-labelledby="codex-cli-title">
            <h2 id="codex-cli-title">Codex CLI</h2>
            <div className="docs-prose">
              <p>
                Extract the ZIP to a durable directory, then run the marketplace add command with
                the absolute path to that directory. In the Codex session, run{" "}
                <code>/plugins</code>, choose the local Fido marketplace, and install Fido. Start
                a new Codex session before using its bundled skills.
              </p>
              <p>No <code>GDD_DETECTOR_ROOT</code> setting is required for the standalone package layout.</p>
            </div>
            <CodeBlock code={CODEX_CLI} label="shell" />
          </section>

          <section
            className="docs-section"
            id="chatgpt-desktop"
            aria-labelledby="chatgpt-desktop-title"
          >
            <h2 id="chatgpt-desktop-title">ChatGPT desktop</h2>
            <div className="docs-prose">
              <ol>
                <li>Extract the ZIP to a durable directory.</li>
                <li>Restart ChatGPT.</li>
                <li>
                  Open ChatGPT Work mode or Codex, then open <strong>Plugins</strong>.
                </li>
                <li>Select the local Fido marketplace and install <strong>Fido</strong>.</li>
                <li>
                  Start a new chat before asking Fido to refresh context or audit a project.
                </li>
              </ol>
            </div>
            <CodeTabs
              label="Install surface"
              tabs={[
                {
                  id: "cli-surface",
                  label: "Codex CLI",
                  code: marketplaceCommand(),
                  language: "shell",
                },
                {
                  id: "desktop-surface",
                  label: "ChatGPT desktop",
                  code: `# After extracting the ZIP and restarting ChatGPT:
# Open ChatGPT Work mode or Codex → Plugins
# Select the local Fido marketplace → Install Fido
# Start a new chat before using skills`,
                  language: "notes",
                },
              ]}
            />
          </section>

          <section className="docs-section" id="after-install" aria-labelledby="after-install-title">
            <h2 id="after-install-title">After install</h2>
            <div className="docs-prose">
              <p>
                Prefer <code>fido-context</code> / <code>fido context</code> so the session already
                knows design intent, gaps, and coverage. SessionStart runs{" "}
                <code>fido context --update-only --if-stale</code> when the plugin is installed.
                Use <code>setup-gdd</code> if the project is untracked, then re-run{" "}
                <code>fido context</code>. Run <code>detect-drift</code> / <code>fido scan</code>{" "}
                only when you want a full audit report.
              </p>
              <p>
                Mark concepts with the marker before the name:{" "}
                <code>[entity: system] Combat Loop</code>.
              </p>
              <p>
                Fuller repository notes live in{" "}
                <a
                  href="https://github.com/ssuish/gdd-plugin/blob/main/INSTALL.md"
                  target="_blank"
                  rel="noreferrer"
                >
                  INSTALL.md
                </a>
                .
              </p>
            </div>
          </section>

          <section
            className="docs-section"
            id="launcher-fallback"
            aria-labelledby="launcher-fallback-title"
          >
            <h2 id="launcher-fallback-title">Launcher fallback</h2>
            <div className="docs-prose">
              <p>
                When PATH <code>fido</code> is unavailable, use the bundled scripts from an
                extracted ZIP or checkout:
              </p>
            </div>
            <CodeBlock code={LAUNCHER_FALLBACK} label="shell" />
          </section>

          <section
            className="docs-section"
            id="troubleshooting"
            aria-labelledby="troubleshooting-title"
          >
            <h2 id="troubleshooting-title">Troubleshooting</h2>
            <div className="docs-prose">
              <p>Essential steps stay visible above. Expand only if something fails.</p>
            </div>
            <DocsDisclosure title="uv is missing from PATH">
              <div className="docs-prose">
                <p>
                  Install uv from{" "}
                  <a href="https://docs.astral.sh/uv/" target="_blank" rel="noreferrer">
                    docs.astral.sh/uv
                  </a>
                  , then open a new shell so PATH updates. First plugin context refresh or scan
                  needs uv to provision the embedded detector environment.
                </p>
              </div>
            </DocsDisclosure>
            <DocsDisclosure title="Marketplace path rejected">
              <div className="docs-prose">
                <p>
                  Use the absolute path to the extracted ZIP directory that contains the plugin
                  and marketplace files. Relative paths and paths to the ZIP archive itself will
                  fail.
                </p>
              </div>
            </DocsDisclosure>
            <DocsDisclosure title="Skills unavailable after install">
              <div className="docs-prose">
                <p>
                  Start a new Codex or ChatGPT chat after installing. SessionStart and bundled
                  skills load for new sessions, not the one that performed the install.
                </p>
              </div>
            </DocsDisclosure>
          </section>

          <nav className="docs-pager" aria-label="Docs pagination">
            <a href="../">← Back to showcase</a>
            <a href="../#install">Conversion CTA →</a>
          </nav>
        </div>
      </div>

      <SiteFooter docsHref="./" homeHref="../" />
    </main>
  );
}

export default DocsPage;

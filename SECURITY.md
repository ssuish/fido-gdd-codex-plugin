# Security Policy

## Supported versions

Security fixes are accepted against the latest published release of **Fido**
(technical package/plugin id `gdd-drift-detector`) and the current default
branch. Older tags may not receive backports.

## What this project does

Fido runs **local** design-fidelity checks. After a one-time `uv` provision of
pinned detector dependencies, scans do not upload project files or call the
network. Prefer reporting issues that could compromise that trust boundary.

## In scope

Please report vulnerabilities that affect:

- The detector engine (`src/gdd_drift_detector/`) or CLI
- The Codex plugin, skills, or launcher (`plugins/gdd-drift-detector/`)
- The downloadable standalone plugin package (ZIP layout, embedded lockfile,
  first-run `uv` provision)
- Supply-chain risks in pinned Python dependencies shipped with the detector
- The showcase site only when the issue affects how users obtain or trust the
  Install handoff (for example a compromised download link or misleading
  install instructions)

## Out of scope

- Bugs in **Godot**, **OpenAI Codex**, or other third-party hosts/tools
- Local misconfiguration of a user's game project or GDD
- Theoretical issues that require an already-compromised developer machine
  with no additional project-specific impact
- Social-engineering reports without a concrete technical vulnerability

## Reporting a vulnerability

**Do not** open a public GitHub Issue for security reports.

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on [ssuish/gdd-plugin](https://github.com/ssuish/gdd-plugin) when enabled
(**Security** → **Report a vulnerability**).

If private reporting is unavailable, contact a repository maintainer privately
and include:

1. A short description of the issue and its impact
2. Steps to reproduce (or a proof of concept)
3. Affected version, commit, or ZIP if known
4. Any suggested fix or mitigation

We aim to acknowledge reports within **7 days** and to share a remediation plan
or status update within **30 days**. Please give us a reasonable window to fix
and publish before any public disclosure.

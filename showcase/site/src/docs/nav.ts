export type DocsNavItem = {
  id: string;
  label: string;
};

export const DOCS_NAV: DocsNavItem[] = [
  { id: "prerequisites", label: "Prerequisites" },
  { id: "cli", label: "CLI" },
  { id: "plugin-zip", label: "Plugin ZIP" },
  { id: "codex-cli", label: "Codex CLI" },
  { id: "chatgpt-desktop", label: "ChatGPT desktop" },
  { id: "after-install", label: "After install" },
  { id: "launcher-fallback", label: "Launcher fallback" },
  { id: "troubleshooting", label: "Troubleshooting" },
];

export function resolveActiveSection(
  visibleIds: string[],
  nav: DocsNavItem[] = DOCS_NAV,
): string {
  if (visibleIds.length === 0) return nav[0]?.id ?? "";
  for (const item of nav) {
    if (visibleIds.includes(item.id)) return item.id;
  }
  return visibleIds[0] ?? nav[0]?.id ?? "";
}

export function nextTabIndex(
  current: number,
  key: "ArrowRight" | "ArrowLeft" | "Home" | "End",
  length: number,
): number {
  if (length <= 0) return 0;
  if (key === "Home") return 0;
  if (key === "End") return length - 1;
  if (key === "ArrowRight") return (current + 1) % length;
  return (current - 1 + length) % length;
}

/**
 * First-party, privacy-preserving event hooks.
 * Dispatches a CustomEvent only. No network, no visitor identity, no project content.
 */
export type ShowcaseEventName =
  | "game_related_finding_reveal"
  | "plugin_zip_click"
  | "marketplace_command_copy"
  | "hint_dismiss";

export function trackShowcaseEvent(name: ShowcaseEventName, detail: Record<string, string> = {}): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent("fido:showcase", {
      detail: { name, ...detail },
    }),
  );
}

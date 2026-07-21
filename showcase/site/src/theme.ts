export type Theme = "dark" | "light";

const STORAGE_KEY = "fido-showcase-theme";

export function readStoredTheme(): Theme {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    if (value === "dark" || value === "light") return value;
  } catch {
    // Ignore storage failures; default to dark.
  }
  return "dark";
}

export function writeStoredTheme(theme: Theme): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Ignore storage failures.
  }
}

export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
}

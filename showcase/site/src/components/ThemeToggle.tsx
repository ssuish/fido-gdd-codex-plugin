import type { Theme } from "../theme";

type ThemeToggleProps = {
  theme: Theme;
  onToggle: () => void;
};

export function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button className="theme-button" type="button" onClick={onToggle}>
      {theme === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}

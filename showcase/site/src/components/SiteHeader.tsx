import { ThemeToggle } from "./ThemeToggle";
import type { Theme } from "../theme";

export type NavItem = {
  href: string;
  label: string;
  current?: boolean;
};

type SiteHeaderProps = {
  theme: Theme;
  onToggleTheme: () => void;
  navItems: NavItem[];
  homeHref?: string;
};

export function SiteHeader({
  theme,
  onToggleTheme,
  navItems,
  homeHref = "./",
}: SiteHeaderProps) {
  return (
    <header className="topbar">
      <a className="wordmark" href={homeHref}>
        Fido
      </a>
      <nav aria-label="Primary navigation">
        {navItems.map((item) => (
          <a
            key={`${item.href}-${item.label}`}
            href={item.href}
            aria-current={item.current ? "page" : undefined}
          >
            {item.label}
          </a>
        ))}
        <ThemeToggle theme={theme} onToggle={onToggleTheme} />
      </nav>
    </header>
  );
}

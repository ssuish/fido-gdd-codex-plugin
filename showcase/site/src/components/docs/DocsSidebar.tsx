import { useEffect, useRef, useState } from "react";
import { DOCS_NAV, resolveActiveSection } from "../../docs/nav";

type DocsSidebarProps = {
  variant?: "desktop" | "mobile";
};

export function DocsSidebar({ variant = "desktop" }: DocsSidebarProps) {
  const [activeId, setActiveId] = useState(DOCS_NAV[0]?.id ?? "");
  const mobileNavRef = useRef<HTMLDetailsElement>(null);

  useEffect(() => {
    const nodes = DOCS_NAV.map((item) => document.getElementById(item.id)).filter(
      (node): node is HTMLElement => Boolean(node),
    );
    if (nodes.length === 0) return;

    const visible = new Set<string>();
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) visible.add(entry.target.id);
          else visible.delete(entry.target.id);
        }
        setActiveId(resolveActiveSection([...visible]));
      },
      { rootMargin: "-20% 0px -55% 0px", threshold: [0, 0.25, 0.6] },
    );

    for (const node of nodes) observer.observe(node);
    return () => observer.disconnect();
  }, []);

  function closeMobileNav() {
    const details = mobileNavRef.current;
    if (details?.open) details.open = false;
  }

  const links = DOCS_NAV.map((item) => (
    <a
      key={item.id}
      href={`#${item.id}`}
      className={activeId === item.id ? "is-active" : undefined}
      aria-current={activeId === item.id ? "location" : undefined}
      onClick={variant === "mobile" ? closeMobileNav : undefined}
    >
      {item.label}
    </a>
  ));

  if (variant === "mobile") {
    return (
      <details ref={mobileNavRef} className="docs-mobile-nav">
        <summary className="docs-mobile-nav-trigger">
          <span>On this page</span>
          <span className="docs-mobile-nav-marker" aria-hidden="true" />
        </summary>
        <nav className="docs-mobile-links" aria-label="On this page">
          <p className="docs-sidebar-title">ON THIS PAGE</p>
          {links}
        </nav>
      </details>
    );
  }

  return (
    <nav className="docs-sidebar docs-sidebar--desktop" aria-label="On this page">
      <p className="docs-sidebar-title">ON THIS PAGE</p>
      {links}
    </nav>
  );
}

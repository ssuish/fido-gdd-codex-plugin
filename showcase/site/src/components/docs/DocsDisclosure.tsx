import { useId, useState, type ReactNode } from "react";

type DocsDisclosureProps = {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
};

export function DocsDisclosure({
  title,
  children,
  defaultOpen = false,
}: DocsDisclosureProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const panelId = useId();

  return (
    <div className="docs-disclosure">
      <button
        type="button"
        className="docs-disclosure-trigger"
        aria-expanded={isOpen}
        aria-controls={panelId}
        onClick={() => setIsOpen((current) => !current)}
      >
        <span>{title}</span>
        <span className="docs-disclosure-marker" aria-hidden="true">
          {isOpen ? "−" : "+"}
        </span>
      </button>
      <div
        id={panelId}
        role="region"
        className={`docs-disclosure-panel${isOpen ? " is-open" : ""}`}
        // Keep children mounted so CSS grid-row collapse can run; inert when closed.
        inert={!isOpen}
      >
        <div className="docs-disclosure-inner">{children}</div>
      </div>
    </div>
  );
}

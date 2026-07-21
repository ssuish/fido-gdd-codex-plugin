import { useId, useRef, useState, type KeyboardEvent } from "react";
import { CodeBlock } from "./CodeBlock";
import { nextTabIndex } from "../../docs/nav";

export type CodeTab = {
  id: string;
  label: string;
  code: string;
  language?: string;
};

type CodeTabsProps = {
  tabs: CodeTab[];
  label?: string;
};

export function CodeTabs({ tabs, label = "Environment" }: CodeTabsProps) {
  const baseId = useId();
  const [activeIndex, setActiveIndex] = useState(0);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const active = tabs[activeIndex] ?? tabs[0];

  function activate(index: number) {
    setActiveIndex(index);
    tabRefs.current[index]?.focus();
  }

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (
      event.key !== "ArrowRight" &&
      event.key !== "ArrowLeft" &&
      event.key !== "Home" &&
      event.key !== "End"
    ) {
      return;
    }
    event.preventDefault();
    const next = nextTabIndex(activeIndex, event.key, tabs.length);
    activate(next);
  }

  if (!active) return null;

  return (
    <div className="code-tabs">
      <div className="code-tablist" role="tablist" aria-label={label}>
        {tabs.map((tab, index) => {
          const selected = index === activeIndex;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`${baseId}-tab-${tab.id}`}
              aria-selected={selected}
              aria-controls={`${baseId}-panel-${tab.id}`}
              tabIndex={selected ? 0 : -1}
              className="code-tab"
              ref={(el) => {
                tabRefs.current[index] = el;
              }}
              onClick={() => activate(index)}
              onKeyDown={onKeyDown}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
      {tabs.map((tab, index) => {
        const selected = index === activeIndex;
        return (
          <div
            key={tab.id}
            role="tabpanel"
            id={`${baseId}-panel-${tab.id}`}
            aria-labelledby={`${baseId}-tab-${tab.id}`}
            hidden={!selected}
          >
            {selected ? (
              <CodeBlock code={tab.code} label={tab.language ?? "shell"} />
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

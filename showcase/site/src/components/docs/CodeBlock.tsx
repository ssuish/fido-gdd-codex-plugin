import { useState } from "react";
import { copyText } from "../../platform/clipboard";
import { copyConfirmationMessage } from "../../discovery/state";

type CodeBlockProps = {
  code: string;
  label?: string;
  id?: string;
};

export function CodeBlock({ code, label = "shell", id }: CodeBlockProps) {
  const [copyStatus, setCopyStatus] = useState("");
  const isCopied = copyStatus.toLowerCase().includes("copied");

  async function handleCopy() {
    const result = await copyText(code);
    setCopyStatus(copyConfirmationMessage(result));
  }

  return (
    <div className={`code-block${isCopied ? " is-copied" : ""}`} id={id}>
      <div className="code-block-header">
        <span>{label}</span>
        <button
          type="button"
          className={`copy-button${isCopied ? " is-copied" : ""}`}
          onClick={handleCopy}
        >
          {isCopied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre>
        <code>{code}</code>
      </pre>
      <p className="copy-status" aria-live="polite">
        {copyStatus}
      </p>
    </div>
  );
}

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import DocsPage from "./pages/DocsPage";
import "./styles/shared.css";
import "./styles/docs.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <DocsPage />
  </StrictMode>,
);

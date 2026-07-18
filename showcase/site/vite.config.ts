import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Godot Web exports often require cross-origin isolation for WASM features.
const godotHeaders = {
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Embedder-Policy": "require-corp",
};

export default defineConfig({
  plugins: [react()],
  base: "./",
  server: {
    headers: godotHeaders,
  },
  preview: {
    headers: godotHeaders,
  },
});

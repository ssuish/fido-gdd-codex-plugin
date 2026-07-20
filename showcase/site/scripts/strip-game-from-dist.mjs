#!/usr/bin/env node
/**
 * Remove dist/game before wrangler deploy so the 35 MiB wasm is not uploaded
 * as Workers static assets (25 MiB/file limit). Game is served from R2.
 */
import { rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const SITE_ROOT = fileURLToPath(new URL("..", import.meta.url));
const GAME_DIR = join(SITE_ROOT, "dist", "game");

if (!existsSync(GAME_DIR)) {
  console.log("dist/game already absent; nothing to strip");
  process.exit(0);
}

rmSync(GAME_DIR, { recursive: true, force: true });
console.log("Stripped dist/game (served from R2 at deploy time)");

#!/usr/bin/env node
/**
 * Upload dist/game/ to R2 bucket fido-showcase-game.
 * Object keys mirror URL paths (game/index.html, game/godot-showcase.wasm, …).
 */
import { spawnSync } from "node:child_process";
import { readdirSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const BUCKET = "fido-showcase-game";
const SITE_ROOT = fileURLToPath(new URL("..", import.meta.url));
const GAME_DIR = join(SITE_ROOT, "dist", "game");

const CONTENT_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".wasm": "application/wasm",
  ".png": "image/png",
  ".pck": "application/octet-stream",
};

function wrangler(args, { allowFail = false } = {}) {
  const result = spawnSync("npx", ["wrangler", ...args], {
    cwd: SITE_ROOT,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    env: process.env,
  });
  const stderr = result.stderr ?? "";
  const stdout = result.stdout ?? "";
  if (result.status !== 0 && !allowFail) {
    process.stderr.write(stdout);
    process.stderr.write(stderr);
    process.exit(result.status ?? 1);
  }
  return { status: result.status ?? 1, stdout, stderr };
}

function listFiles(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    const st = statSync(path);
    if (st.isDirectory()) {
      out.push(...listFiles(path));
    } else if (st.isFile()) {
      out.push(path);
    }
  }
  return out;
}

function contentTypeFor(filePath) {
  const ext = extname(filePath).toLowerCase();
  return CONTENT_TYPES[ext] ?? "application/octet-stream";
}

function ensureBucket() {
  const created = wrangler(["r2", "bucket", "create", BUCKET], {
    allowFail: true,
  });
  if (created.status === 0) {
    console.log(`Created R2 bucket ${BUCKET}`);
    return;
  }
  const combined = `${created.stdout}\n${created.stderr}`.toLowerCase();
  if (
    combined.includes("already exists") ||
    combined.includes("409") ||
    combined.includes("bucket already")
  ) {
    console.log(`R2 bucket ${BUCKET} already exists`);
    return;
  }
  process.stderr.write(created.stdout);
  process.stderr.write(created.stderr);
  process.exit(created.status);
}

function main() {
  let st;
  try {
    st = statSync(GAME_DIR);
  } catch {
    console.error(
      `Missing ${GAME_DIR}. Run npm run build first so dist/game exists.`,
    );
    process.exit(1);
  }
  if (!st.isDirectory()) {
    console.error(`Expected directory: ${GAME_DIR}`);
    process.exit(1);
  }

  ensureBucket();

  const files = listFiles(GAME_DIR);
  if (files.length === 0) {
    console.error(`No files under ${GAME_DIR}`);
    process.exit(1);
  }

  for (const filePath of files) {
    const rel = relative(join(SITE_ROOT, "dist"), filePath).replaceAll(
      "\\",
      "/",
    );
    const key = rel; // game/...
    const contentType = contentTypeFor(filePath);
    console.log(`Uploading ${key} (${contentType})`);
    wrangler([
      "r2",
      "object",
      "put",
      `${BUCKET}/${key}`,
      `--file=${filePath}`,
      `--content-type=${contentType}`,
      "--remote",
    ]);
  }

  console.log(`Synced ${files.length} file(s) to r2://${BUCKET}/game/`);
}

main();

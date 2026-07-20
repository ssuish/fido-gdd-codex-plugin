/**
 * Serve /game/* from R2 (Godot Web export exceeds the 25 MiB Workers assets
 * limit). Site shell stays on static assets; isolation headers on /game/*
 * mirror public/_headers (assets _headers do not apply to R2 responses).
 */

const ISOLATION_HEADERS: Record<string, string> = {
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Embedder-Policy": "require-corp",
  "Cross-Origin-Resource-Policy": "same-origin",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "X-Frame-Options": "SAMEORIGIN",
};

const CONTENT_TYPES: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".wasm": "application/wasm",
  ".png": "image/png",
  ".pck": "application/octet-stream",
};

export interface Env {
  ASSETS: Fetcher;
  GAME: R2Bucket;
}

function contentTypeForKey(key: string): string {
  const dot = key.lastIndexOf(".");
  if (dot < 0) {
    return "application/octet-stream";
  }
  const ext = key.slice(dot).toLowerCase();
  return CONTENT_TYPES[ext] ?? "application/octet-stream";
}

function gameObjectKey(pathname: string): string | null {
  if (!pathname.startsWith("/game/")) {
    return null;
  }
  // Strip leading slash so R2 keys match sync-game-r2.mjs (game/...).
  return pathname.slice(1);
}

async function serveGame(
  request: Request,
  env: Env,
  key: string,
): Promise<Response> {
  const object = await env.GAME.get(key);
  if (object === null) {
    return new Response("Not Found", { status: 404 });
  }

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("etag", object.httpEtag);
  headers.set("Content-Type", contentTypeForKey(key));
  for (const [name, value] of Object.entries(ISOLATION_HEADERS)) {
    headers.set(name, value);
  }

  if (request.method === "HEAD") {
    return new Response(null, { status: 200, headers });
  }

  return new Response(object.body, { status: 200, headers });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const key = gameObjectKey(url.pathname);

    if (key !== null) {
      if (request.method !== "GET" && request.method !== "HEAD") {
        return new Response("Method Not Allowed", {
          status: 405,
          headers: { Allow: "GET, HEAD" },
        });
      }
      return serveGame(request, env, key);
    }

    return env.ASSETS.fetch(request);
  },
};

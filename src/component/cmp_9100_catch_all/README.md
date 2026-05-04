# Catch All — `catch_all_0yt2sa`

Fallback routing component. Serves static files from `public/` and renders 404
error pages for all unmatched routes.

## Overview

This component is the application's safety net. Loaded last via its `cmp_9xxx`
prefix, it catches any request that no other component has handled:

1. **Static files** — If the requested path has a file extension and the file
   exists in `Config.STATIC_FOLDER`, it is served with cache headers.
2. **Everything else** — A 404 error page is rendered via the `http_errors`
   component.

## Routes

| Route | Description |
|-------|-------------|
| `/<anyext:asset_path>` | Serve static files with rate limiting and cache control |
| `/<path:_path_value>` | Fallback — always returns a 404 error page |

## Configuration

| Config Key | Purpose |
|------------|---------|
| `Config.STATIC_FOLDER` | Absolute path to the public static files directory |
| `Config.STATIC_LIMITS` | Rate limit for static file requests (e.g., `"100/hour"`) |
| `Config.STATIC_CACHE_CONTROL` | `Cache-Control` header value for static files |

## Security

- All routes are public (no authentication).
- Rate limiting on the static file route prevents abuse.
- `send_from_directory()` prevents directory traversal attacks.
- Directory listing is explicitly blocked.

## Load Order

This component uses the `cmp_9xxx` prefix intentionally. Components are loaded
alphabetically, so this component registers its routes last. All other components
get a chance to handle requests first.

## Dependencies

- `http_errors` (`http_errors_0yt2sa`) — provides the 404 error page rendering.
- Flask `limiter` — rate limiting on the static file route.

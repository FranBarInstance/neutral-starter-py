# Image Delivery Component

Serves public image variants and profile thumbnails.

## Overview

Provides endpoints for retrieving stored image variants by ID and profile thumbnails by username. Returns WebP images with server-side caching and rate limiting.

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/p/<username>` | GET | No | Profile thumbnail (always returns image) |
| `/v/<image_id>/<variant>` | GET | No | Image variant by ID (404 if missing) |
| `/*` | GET | No | 404 fallback |

## Structure

```
├── manifest.json              # UUID: image_0yt2sa, route: /i
├── schema.json                # Route URL publication
├── route/
│   ├── __init__.py            # Blueprint init
│   └── routes.py              # 3 route handlers
└── static/
    ├── 404.webp               # Not-found placeholder (~12KB)
    └── profile.webp           # Default profile (~5KB)
```

## Schema Data

Published in `current.site` for cross-component URL building:

| Key | Value |
|-----|-------|
| `image_link` | `[:;data->image_0yt2sa->manifest->route:]` |
| `image_link_profile` | `[:;data->image_0yt2sa->manifest->route:]/p` |
| `image_link_variant` | `[:;data->image_0yt2sa->manifest->route:]/v` |

**Template usage:**
```
<img src="{:;current->site->image_link_profile:}/username">
<img src="{:;current->site->image_link_variant:}/image-id/thumb">
```

## Response Behavior

- **Format**: `image/webp` for all responses
- **Headers**: `X-Image-Width`, `X-Image-Height`, `Cache-Control`
- **Rate limiting**: `Config.STATIC_LIMITS`
- **Caching**: `Config.CACHE_IMG`
- **Profile** (`/p/*`): Always returns HTTP 200 (user image or default placeholder)
- **Variant** (`/v/*`): Returns HTTP 404 with placeholder if variant missing

## Dependencies

- Core `Image` class (variant retrieval)
- Core `User` class (profile lookup)
- Flask-Caching, Flask-Limiter

## Notes

- Profile endpoint only serves `thumb` variant
- WebP format only (no JPEG/PNG fallback)
- Images are public (no authentication required)

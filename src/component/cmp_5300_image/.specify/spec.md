# Component: image_0yt2sa

## Executive Summary

Image variant delivery component serving public image variants and profile thumbnails. Provides two primary endpoints: profile images by username (always returns a valid image — either the user's thumb variant or a default profile placeholder) and generic image variants by ID (returns the variant or a 404 placeholder). Publishes route URLs in schema data for cross-component use. Uses server-side caching, rate limiting, and WebP format for all responses.

## Identity

- **UUID**: `image_0yt2sa`
- **Base Route**: `/i`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes are publicly accessible (images must be reachable without auth)
- Rate limiting applied via `@limiter.limit(Config.STATIC_LIMITS)`
- Server-side caching via `@cache.cached(timeout=Config.CACHE_IMG)`
- No user input validation beyond path parameters (image IDs and variants are validated by core `Image` class)

## Architecture

### Component Type
**Infrastructure/Utility** component. Provides:
- Public image variant serving
- Profile thumbnail delivery by username
- Default placeholder images (404, profile)
- Route URL publication via schema data
- Caching and rate limiting for image endpoints

### Directory Structure

```
src/component/cmp_NNNN_image/
├── manifest.json                          # Identity and security
├── schema.json                            # Route URL publication
├── README.md                              # Operational documentation
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   └── routes.py                          # Route definitions (3 handlers)
└── static/
    ├── 404.webp                           # Not-found placeholder
    └── profile.webp                       # Default profile placeholder
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Rate Limit | Cache | Purpose |
|-------|--------|---------|------------|-------|---------|
| `/p/<username>` | GET | `get_username_image()` | Yes | Yes | Profile thumbnail by username |
| `/v/<image_id>/<variant>` | GET | `get_image_variant()` | Yes | Yes | Image variant by ID |
| `/` (and any subpath) | GET | `serve_dynamic_content()` | No | No | 404 fallback |

### Route Handlers

**`get_username_image(username)`**
- Returns user's `thumb` variant as profile image
- If user has no image or variant unavailable → returns default `profile.webp` (HTTP 200)
- Uses `User.get_public_profile_by_username()` to lookup user
- Uses `Image.get_variant()` to retrieve specific variant
- Headers: `Content-Type: image/webp`, `Cache-Control`, `X-Image-Width`, `X-Image-Height`

**`get_image_variant(image_id, variant)`**
- Returns any stored image variant by ID and variant name
- If variant unavailable → returns `404.webp` (HTTP 404)
- Uses `Image.get_public_variant()` for retrieval
- Same headers as profile endpoint with different cache control

**`serve_dynamic_content(_path_value)`**
- Catch-all for unmatched routes
- Always returns `404.webp` with HTTP 404

### Placeholder Images (`static/`)

| File | Size | Use |
|------|------|-----|
| `404.webp` | ~12KB | Not-found response for missing variants |
| `profile.webp` | ~5KB | Default profile when user has no image |

Both are WebP format for consistency with generated variants.

### Dependencies

- **Depends on**: Core `Image` (variant retrieval), core `User` (profile lookup), Flask-Caching, Flask-Limiter, `Config` (cache/limits settings)
- **Used by**: Any component needing to display images (album, user profiles, etc.)

## Data and Models

### Schema Data Publication (`schema.json`)

The component publishes its routes via `data.current.site` for cross-component use:

| Key | Value | Purpose |
|-----|-------|---------|
| `image_link` | `[:;data->image_0yt2sa->manifest->route:]` | Base route URL |
| `image_link_profile` | `[:;data->image_0yt2sa->manifest->route:]/p` | Profile endpoint prefix |
| `image_link_variant` | `[:;data->image_0yt2sa->manifest->route:]/v` | Variant endpoint prefix |

**Usage in templates:**
```
<img src="{:;current->site->image_link_profile:}/username">
<img src="{:;current->site->image_link_variant:}/image-id/thumb">
```

This decouples image URL construction from the actual route value.

### Configuration Used

| Config Key | Purpose |
|------------|---------|
| `Config.STATIC_LIMITS` | Rate limit for image endpoints |
| `Config.CACHE_IMG` | Cache timeout for image responses |
| `Config.STATIC_CACHE_IMG_PROFILE_CONTROL` | Cache-Control header for profile images |
| `Config.STATIC_CACHE_IMG_CONTROL` | Cache-Control header for variants |
| `Config.DB_PWA` / `Config.DB_PWA_TYPE` | Database for user profile lookups |

## Technical Rationale

- **Separate profile and variant endpoints**: Profile images have different fallback behavior (always return valid image) vs variants (return 404 when missing)
- **WebP format**: Consistent format for all image responses, smaller size than JPEG/PNG
- **Server-side caching**: Images are immutable (variants are generated once), so aggressive caching is safe
- **Rate limiting**: Prevents abuse of image serving endpoints
- **Dimension headers**: `X-Image-Width` and `X-Image-Height` allow client-side layout calculations
- **Schema URL publication**: Other components build URLs without hardcoding routes, enabling route flexibility

## Known Limitations

- Only WebP format supported (no JPEG/PNG fallback for older browsers)
- Profile endpoint only serves `thumb` variant (no configurable variant)
- No authentication on image routes (all images are effectively public)

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/p/<username>` returns user's thumb variant as WebP
- [x] `/p/<username>` returns default profile image if user has no image (HTTP 200)
- [x] `/v/<image_id>/<variant>` returns specified variant as WebP (HTTP 200)
- [x] `/v/<image_id>/<variant>` returns 404 placeholder if variant missing (HTTP 404)
- [x] All unmatched routes return 404 placeholder (HTTP 404)

### Technical
- [x] All responses are `image/webp` Content-Type
- [x] Rate limiting applied to image endpoints
- [x] Server-side caching applied to image endpoints
- [x] `X-Image-Width` and `X-Image-Height` headers included
- [x] `Cache-Control` headers set per response type
- [x] Placeholder images served from component `static/` directory

### Integration
- [x] `current.site.image_link` published in schema
- [x] `current.site.image_link_profile` published in schema
- [x] `current.site.image_link_variant` published in schema
- [x] Other components can build URLs using BIF references

### Dependencies
- [x] Uses core `Image` class for variant retrieval
- [x] Uses core `User` class for profile lookup
- [x] Respects `Config` cache and limit settings

---

*Last updated: 2026-05-04*

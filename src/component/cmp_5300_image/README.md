# Image Delivery Component (`image_0yt2sa`)

Component responsible for serving public image variants and profile thumbnails.

## What It Does

- Serves stored image variants by image id and variant name.
- Serves profile thumbnail images by username.
- Returns built-in WebP placeholders when the requested image is missing.
- Publishes image delivery routes in schema data through `current.site.image_link`, `current.site.image_link_profile`, and `current.site.image_link_variant`.

## Runtime Data

This component sets in the schema:

- `current.site.image_link = [:;data->image_0yt2sa->manifest->route:]`
- `current.site.image_link_profile = [:;data->image_0yt2sa->manifest->route:]/p`
- `current.site.image_link_variant = [:;data->image_0yt2sa->manifest->route:]/v`

Other components can use those values to build public image URLs without hardcoding the route.

## Routes

- `<manifest.route>` is defined in `manifest.json`.
- `GET <manifest.route>/p/<username>`
  - Returns the user's `thumb` profile image variant.
  - Returns the default profile image when the user has no profile image or the `thumb` variant is not available.
- `GET <manifest.route>/v/<image_id>/<variant>`
  - Returns one stored image variant.
  - Falls back to `static/404.webp` with HTTP `404` when the variant does not exist.
- `GET <manifest.route>/` and any unmatched subroute
  - Returns `static/404.webp` with HTTP `404`.

## Response Behavior

- Successful image responses are returned as `image/webp`.
- Variant responses include `X-Image-Width` and `X-Image-Height`.
- The component applies rate limiting through `Config.STATIC_LIMITS`.
- The component applies server-side caching through `Config.CACHE_IMG`.
- A username lookup without a usable image is not treated as an error response.
- Cache headers are set with:
  - `Config.STATIC_CACHE_IMG_PROFILE_CONTROL` for profile responses
  - `Config.STATIC_CACHE_IMG_CONTROL` for generic variant responses

## Key Files

- `/manifest.json`
- `/schema.json`
- `/route/routes.py`
- `/static/profile.webp`
- `/static/404.webp`

## Usage Examples

```html
<img src="{:;current->site->image_link_profile:}/john" alt="Profile image">
<img src="{:;current->site->image_link_variant:}/abc123/thumb" alt="Thumbnail image">
<img src="{:;current->site->image_link_variant:}/abc123/medium" alt="Medium image">
<img src="{:;current->site->image_link_variant:}/abc123/full" alt="Full image">
```

In practice, other components should build those URLs from `current.site.image_link_profile` and `current.site.image_link_variant`.

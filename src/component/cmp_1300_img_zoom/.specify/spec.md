# Component: img_zoom_0yt2sa

## Executive Summary

Generic utility component that opens an image in a full-screen overlay when the user clicks an element marked as zoomable. Provides app-wide image zoom behavior through global CSS/JS injection.

## Identity

- **UUID**: `img_zoom_0yt2sa`
- **Base Route**: `/img-zoom`
- **Version**: `0.0.1`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

## Architecture

### Component Type
**Utility** component. Provides:
- Static routes serving CSS and JavaScript files
- Global CSS/JS injection via `component-init.ntpl`
- App-wide image zoom behavior

### Directory Structure

```
src/component/cmp_NNNN_img_zoom/
├── manifest.json              # Identity and security
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving routes
├── neutral/
│   └── component-init.ntpl    # Global CSS/JS injection
└── static/
    ├── img-zoom.css           # Zoom styles
    └── img-zoom.js            # Zoom interactivity
```

### Routes (`route/routes.py`)

**`/img-zoom.css`** (GET)
- Serves `img-zoom.css` from component's `static/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

**`/img-zoom.js`** (GET)
- Serves `img-zoom.js` from component's `static/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

### Global Asset Injection (`neutral/component-init.ntpl`)

**`img_zoom_0yt2sa-head` snippet (moved to `/head`):**
- Zoom CSS (`img-zoom.css`) with version query parameter

**`img_zoom_0yt2sa-body` snippet (moved to `/body`):**
- Zoom JavaScript (`img-zoom.js`) with version query parameter

**CSP Compliance:** All resources use `{:;CSP_NONCE:}` placeholder.

### How It Works

- Uses delegated click handling for elements added dynamically via AJAX
- Creates lightweight overlay on demand without modifying original DOM
- Reuses single backdrop (`.img-zoom-backdrop`) and overlay image (`.img-zoom-overlay-img`)
- Locks body scrolling while overlay is visible
- Clicking outside closes the overlay

### Supported Triggers

| Trigger | Attribute | Behavior |
|---------|-----------|----------|
| Image with zoom | `class="img-zoomable"` | Uses `src` for overlay |
| Thumbnail to full | `data-zoom-src` | Uses `data-zoom-src` URL instead of `src` |
| Non-image element | `class="img-zoomable"` + `data-zoom-src` | Button/link triggers zoom |

### Dependencies

- **No dependencies**: Self-contained utility
- **Used by**: All components needing image zoom functionality

## Data and Models

No schema data. This component is a pure utility provider.

## Technical Rationale

- **Delegated Events**: Works with dynamically added content via AJAX
- **Lightweight Overlay**: Creates elements on demand, doesn't pollute DOM
- **Body Scroll Lock**: Prevents background scrolling while zoomed
- **Single Instance**: Reuses backdrop and overlay elements for performance
- **Cache Busting**: Version query parameter ensures fresh assets on updates

---

## Acceptance Criteria (SDD)

### Functional
- [x] `component-init.ntpl` injects CSS into page head on every render
- [x] `component-init.ntpl` injects JavaScript at end of body
- [x] Zoom triggers on elements with `.img-zoomable` class
- [x] Supports `data-zoom-src` for higher resolution images
- [x] Body scroll locked while overlay is visible
- [x] Click outside overlay closes zoom

### Technical
- [x] Route exposed at `/img-zoom` (base route from manifest)
- [x] Static routes for CSS and JS assets
- [x] Static file serving with proper cache headers
- [x] No authentication required for asset access
- [x] CSP-compliant script and style injection

### Integration
- [x] Global injection affects all pages
- [x] Works with AJAX-loaded content via delegated events
- [x] Route paths derived from `manifest->route` BIF
- [x] Version query parameter for cache busting

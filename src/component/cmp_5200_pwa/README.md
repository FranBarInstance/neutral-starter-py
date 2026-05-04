# PWA Component

Progressive Web App support for Neutral TS Starter Py.

## Overview

Provides service worker registration, web app manifest, offline page, and install prompt. Injects PWA meta tags into HTML head and conditionally displays install button in navbar.

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/service-worker.js` | GET | No | Service worker JavaScript |
| `/pwa/manifest.json` | GET | No | Web app manifest (NTPL) |
| `/pwa/offline.html` | GET | No | Offline fallback page |
| `/pwa/*` | GET | No | Static assets (icons) |

## Structure

```
├── manifest.json              # UUID: pwa_0yt2sa, route: ""
├── schema.json                # Menu entries, translations
├── route/
│   ├── __init__.py            # Blueprint init
│   └── routes.py              # 4 route handlers
├── neutral/
│   ├── component-init.ntpl    # Conditional snippet loading
│   ├── snippets.ntpl          # Meta tags, SW registration, install JS
│   └── route/pwa/
│       ├── manifest.json      # Manifest template
│       └── offline.html       # Offline page template
├── static/
│   └── service-worker.js      # Service worker (cache, fetch, push)
└── tests/
    └── test_routes.py         # Route tests
```

## Configuration

| Key | Default | Purpose |
|-----|---------|---------|
| `enable` | `true` | Toggle PWA features |
| `static-dir` | `"pwa"` | Asset directory name |
| `theme_color` | `"#375A7F"` | Theme/meta color |
| `background_color` | `"#ffffff"` | Background color |
| `navbar_times` | `2` | Install prompt display limit |
| `public-has-*` | `false` | Override to `public/` directory |

Override via `custom.json` in component root.

## Snippets

- `pwa_0yt2sa-head` — Meta tags (moved to `/head`)
- `pwa_0yt2sa-body-end` — Service worker registration + install JS (moved to `/body`)
- `pwa_0yt2sa-main-navbar-bottom-install` — Install button (conditional)

## Translations

6 languages: EN, ES, DE, FR, AR, ZH

Key strings: "Install APP", "Internet connection required", "No connection"

## Menu Integration

- **Main menu**: "Install APP" entry with `x-icon-webapp`
- Hidden by default (`d-none`), shown via JS when installable
- Available for both anonymous and authenticated users

## Notes

- Must use root route (`""`) for service worker scope
- Install prompt uses `pwa_0yt2sa_count` cookie for limiting
- Push notification support included (requires server-side integration)
- CSP nonces on all inline scripts/styles

# Component: pwa_0yt2sa

## Executive Summary

Progressive Web App (PWA) component providing service worker registration, dynamic web app manifest generation, offline page support, and installation prompt integration. Injects PWA meta tags into HTML head, registers service worker at page load, and conditionally displays an install button in the navbar based on browser support and cookie-based frequency limiting.

## Identity

- **UUID**: `pwa_0yt2sa`
- **Base Route**: `/` (root — required for `/service-worker.js` to function)
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes are publicly accessible (PWA assets must be reachable without auth)
- Rate limiting applied to static asset routes via `@limiter.limit(Config.STATIC_LIMITS)`
- CSP nonces required on all inline scripts and styles
- Directory traversal protection in static file serving (path validation)

## Architecture

### Component Type
**Infrastructure/Feature** component. Provides:
- Service worker registration and caching
- Web app manifest with dynamic variable substitution
- Offline fallback page
- PWA icons (32px, 192px, 512px, 512px maskable)
- Install prompt integration
- Meta tag injection for PWA support
- Menu entry for app installation
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_NNNN_pwa/
├── manifest.json                          # Identity, security, config
├── schema.json                            # Menu entries, translations
├── custom.json                            # Local overrides (optional)
├── README.md                              # Operational documentation
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   └── routes.py                          # Route definitions (4 handlers)
├── neutral/
│   ├── component-init.ntpl              # Conditional snippet inclusion
│   ├── snippets.ntpl                      # Head meta tags, body-end JS, install button
│   └── route/
│       └── pwa/
│           ├── manifest.json              # Web app manifest template
│           └── offline.html               # Offline page template
├── static/
│   ├── service-worker.js                  # Service worker (cache, fetch, push)
│   └── pwa/                               # Icons (if not using public/)
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Rate Limit | Purpose |
|-------|--------|---------|------------|---------|
| `/service-worker.js` | GET | `service_worker()` | No | Service worker JS file |
| `/pwa/manifest.json` | GET | `pwa_manifest_json()` | Yes | Web app manifest (NTPL) |
| `/pwa/offline.html` | GET | `pwa_offline()` | Yes | Offline fallback page (NTPL) |
| `/pwa/<relative_route>` | GET | `pwa_static()` | Yes | Static assets (icons, etc.) |

### Route Handlers

**`service_worker()`**
- Serves `service-worker.js` from component `static/` or `public/` (if `public-has-service-worker`)
- Sets `Cache-Control` header via `Config.STATIC_CACHE_CONTROL`

**`pwa_manifest_json()`**
- Renders manifest template with variable substitution via `RequestHandler`
- Supports override to `public/pwa/manifest.json` (if `public-has-manifest`)
- Returns JSON with `Content-Type: application/json`

**`pwa_offline()`**
- Renders offline page template with variable substitution
- Supports override to `public/pwa/offline.html` (if `public-has-offline`)

**`pwa_static()`**
- Serves arbitrary static files from `/pwa/*` path
- Validates file exists and is not a directory
- Returns 404 via `RequestHandler.render_error()` if not found
- Path traversal protection via `os.path.exists()` check

### Service Worker (`static/service-worker.js`)

**Events handled:**
1. **`install`** — Caches `/pwa/offline.html` in "offline" cache
2. **`fetch`** — Network-first strategy: tries fetch, falls back to cached offline page
3. **`push`** — Displays notification with title, body, icon, image, actions
4. **`notificationclick`** — Closes notification, focuses existing window or opens new URL

### NTPL Snippets (`neutral/snippets.ntpl`)

| Snippet | Purpose | Target |
|---------|---------|--------|
| `pwa_0yt2sa-head` | Meta tags (theme-color, apple-mobile-web-app, icons, manifest link) | `/head` |
| `pwa_0yt2sa-body-end` | Service worker registration + install prompt JS | `/body` |
| `pwa_0yt2sa-main-navbar-bottom-install` | Install button HTML | Navbar (conditional) |

**Install Prompt Logic:**
- Listens for `beforeinstallprompt` event
- Shows install button when app is installable
- Tracks display count via `pwa_0yt2sa_count` cookie
- Respects `navbar_times` config (stops showing after N times)
- Hides button after successful `appinstalled` event

### Component Init (`neutral/component-init.ntpl`)

Conditional inclusion: only loads snippets if `pwa_0yt2sa->manifest->config->enable` is true.

### Dependencies

- **Depends on**: Core `RequestHandler`, Flask `send_from_directory`, `Config.STATIC_CACHE_CONTROL`, `Config.STATIC_LIMITS`, rate limiter
- **Used by**: Base layout (head/body snippets), navbar system

## Data and Models

### Configuration (`manifest.json` config section)

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `enable` | boolean | `true` | Globally toggle PWA features |
| `static-dir` | string | `"pwa"` | Directory name for PWA assets |
| `theme_color` | string | `"#375A7F"` | Theme color for manifest/meta |
| `background_color` | string | `"#ffffff"` | Background color for manifest |
| `navbar_times` | integer | `2` | Times to show install prompt |
| `public-has-icons` | boolean | `false` | Use `public/pwa/` for icons |
| `public-has-manifest` | boolean | `false` | Use `public/pwa/manifest.json` |
| `public-has-service-worker` | boolean | `false` | Use `public/service-worker.js` |
| `public-has-offline` | boolean | `false` | Use `public/pwa/offline.html` |

### Manifest Template (`neutral/route/pwa/manifest.json`)

Dynamic fields via BIF:
- `short_name`: `{:;current->site->name:}`
- `name`: `{:;current->site->title:}`
- `description`: `{:;current->site->description:}`
- `theme_color`: `{:;pwa_0yt2sa->manifest->config->theme_color:}`
- `background_color`: `{:;pwa_0yt2sa->manifest->config->background_color:}`

Static fields:
- `id`: `/?pwa=1`
- `start_url`: `/?pwa=1`
- `display`: `standalone`
- `scope`: `/`
- `icons`: 32px, 192px, 512px, 512px-maskable

### Translations (`inherit.locale.trans`)

6 languages (EN, ES, DE, FR, AR, ZH):

| Key | EN | ES |
|-----|----|----|
| Install APP | Install APP | Instalar APP |
| The application | The application | La aplicación |
| Internet connection required | Internet connection required | Conexión a Internet requerida |
| No connection | No connection | Sin conexión |

### Menu Integration (`schema.json`)

Menu entry for both anonymous (`session:`) and authenticated (`session:true`) users:

| Entry | Text | Link | Icon | Classes |
|-------|------|------|------|---------|
| pwa | Install APP | `#` | `x-icon-webapp` | `pwa_0yt2sa-install-show pwa_0yt2sa-install-click d-none` |

Classes control visibility (shown via JS when installable, hidden by default with `d-none`).

## Technical Rationale

- **Root route requirement**: `/service-worker.js` must be at root for proper scope; hence component uses empty base route
- **Dual source support**: `public-has-*` flags allow project-level overrides without modifying component
- **Cookie-based limiting**: Prevents install prompt fatigue by tracking display count client-side
- **Network-first caching**: Offline page only shown when network fails, ensuring fresh content when possible
- **Push notification support**: Service worker handles push events with customizable notifications
- **NTPL manifest**: Allows dynamic manifest based on site configuration (name, colors)
- **CSP compliance**: All inline scripts use `{:;CSP_NONCE:}` placeholder

## Known Limitations

- Install prompt behavior varies by browser (Chrome/Edge support `beforeinstallprompt`, Safari does not)
- Cookie-based limiting is client-side and can be reset by clearing cookies
- Push notifications require additional server-side integration (not included in this component)

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/service-worker.js` returns service worker JavaScript
- [x] `/pwa/manifest.json` returns valid web app manifest with dynamic values
- [x] `/pwa/offline.html` returns offline fallback page
- [x] `/pwa/*.png` serves icon files (or 404 if not present)
- [x] Meta tags injected in HTML head (theme-color, manifest link, icons)
- [x] Service worker registered on page load
- [x] Install button appears when browser supports PWA installation
- [x] Install button hidden after successful installation
- [x] Install prompt respects `navbar_times` cookie limit

### Technical
- [x] All routes public (no auth required)
- [x] Rate limiting on static routes
- [x] CSP nonces on inline scripts and styles
- [x] Cache-Control headers on all static responses
- [x] 404 returned for non-existent static files
- [x] Path traversal prevented in static file serving

### Configuration
- [x] `enable` config toggles snippet injection
- [x] `public-has-*` flags support override to public/ directory
- [x] `theme_color` and `background_color` configurable
- [x] `navbar_times` controls install prompt frequency
- [x] `static-dir` configures asset path

### Integration
- [x] Snippets injected via `{:moveto; /head ...}` and `{:moveto; /body ...}`
- [x] Menu entry with install button for all users
- [x] Translations in 6 languages
- [x] Component-init conditional loading

### Quality
- [x] Tests cover all routes, cache headers, security
- [x] Offline page displays site name and "No connection" message
- [x] Manifest includes all required PWA fields

---

*Last updated: 2026-05-04*

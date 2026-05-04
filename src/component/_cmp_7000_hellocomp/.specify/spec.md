# Component: hellocomp_0yt2sa

## Executive Summary

Visual and architectural reference component demonstrating how to combine routes, global snippets, component snippets, route data, translations, AJAX endpoints, Bootstrap modals, Neutral objects, private libraries, and static asset delivery. A complete implementation example for teaching framework patterns — UI decisions and demonstration routes exist for educational purposes, not business functionality.

## Identity

- **UUID**: `hellocomp_0yt2sa`
- **Base Route**: `<manifest.route>`
- **Version**: `0.0.0`

## Functional Scope

The component must demonstrate:

- component initialization with private library exposure;
- menu and drawer for anonymous and logged-in users;
- global translations in `/schema.json`;
- global snippet loaded from `/neutral/component-init.ntpl`;
- snippets available to all component routes from `/neutral/route/index-snippets.ntpl`;
- specific snippet for the root route;
- page routes, AJAX routes, and component catch-all;
- use of custom handler on a specific route;
- use of Neutral objects with Python and PHP engines;
- simple Bootstrap modals, with AJAX, and with GET form;
- translated content via language-specific templates;
- static asset served from `/static/` through the component's catch-all;
- tests that derive the route from `/manifest.json`.

## Non-Objectives

- Should not manage persistent data.
- Should not create own models.
- Should not implement productive AJAX forms; the example modal form uses `GET` to teach simple submission.
- Should not replace specs for functional components like authentication, PWA, or images.

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes are publicly accessible (example/demo component)
- AJAX endpoints require `Requested-With-Ajax` header
- Asset delivery limited to component's `/static/` directory via `send_from_directory`

## Architecture

### Component Type
**Example** component. Provides:
- Complete framework pattern demonstrations
- Routes, snippets, data, translations integration
- AJAX endpoints with header protection
- Bootstrap modals
- Neutral objects (Python and PHP engines)
- Private library exposure pattern
- Static asset delivery pattern

### Routes

| Method | Route | Handler | Auth | Purpose |
|--------|-------|---------|------|---------|
| `GET` | `<manifest.route>/` | `RequestHandler` | No | Main showcase page |
| `GET` | `<manifest.route>/test1` | `HelloCompRequestHandler` | No | Custom handler with local data |
| `GET` | `<manifest.route>/ajax/example` | `RequestHandler` | No | AJAX partial content (requires header) |
| `GET` | `<manifest.route>/ajax/modal-content` | `RequestHandler` | No | AJAX modal content (requires header) |
| `GET` | `<manifest.route>/<path>` | `RequestHandler` or `send_from_directory` | No | Template routes or static assets |

**Additional demonstration routes (catch-all):**
- `/test2` — GET form data demonstration
- `/translating-content` — Language-specific templates
- `/redirect` — Redirection demonstration
- `/error-500` — Controlled error demonstration
- `/comp.webp` — Static asset example
- Non-existent routes — 404 handling

### Route Handlers

**`/route/__init__.py`** — Component initialization:
- Exposes `/lib` in `sys.path` for importing `hellocomp_0yt2sa`
- Path calculated from component's own file
- No duplication in `sys.path`

**`/route/routes.py`** — Route definitions:
- Imports private library exposed by `init_component`
- Defines `/test1` before catch-all
- Protects AJAX endpoints with `require_header_set`
- Loads `schema_local_data["message"]` from `hellocomp()`
- Serves assets from `/static/` via `send_from_directory`
- Applies `Config.STATIC_CACHE_CONTROL` to assets

**`/route/hellocomp_handler.py`** — Custom handler:
- Extends `RequestHandler`
- Adds local data in `schema_local_data`
- Encapsulates route logic in `test1()` method
- Keeps final render in `render_route()`

### Templates

**`/neutral/component-init.ntpl`** — Global snippet available throughout application:
- `hellocomp_0yt2sa-global-snippet`
- Auto-loaded by component system

**`/neutral/route/index-snippets.ntpl`** — Shared snippets for all routes:
- Loads `/neutral/route/data.json` and `locale-*.json`
- Defines `hellocomp_0yt2sa-route-snippet`
- Defines `hellocomp_0yt2sa:modals` with Bootstrap modals
- Moves modals to end of body via `{:moveto; ... :}`
- Demonstrates `{:obj; ... :}` with Python and PHP engines
- Shows translation references via object locale

**`/neutral/route/root/content-snippets.ntpl`** — Root route:
- Loads `/neutral/route/root/data.json`
- Defines local route snippet
- Renders `current:template:body-main-content`
- Shows global, component, and local snippets
- Includes image from `<manifest.route>/comp.webp`
- AJAX and modal buttons

**Demonstration routes under `/neutral/route/root/`:**
- `/test1/` — Custom handler result
- `/test2/` — GET form data
- `/ajax/example/` — AJAX partial
- `/ajax/modal-content/` — Modal content
- `/translating-content/` — Language selection
- `/redirect/` — Redirection
- `/error-500/` — Error handling

### Neutral Objects

**Python object** (`/neutral/obj/comp.json`):
- Engine: `"Python"`
- File: `/src/comp.py`
- Callback: `"main"`
- Venv: resolved with `VENV_DIR`

**PHP object** (`/neutral/obj/comp-php.json`):
- Engine: `"php"`
- File: `/src/comp.php`
- Callback: `"main"`

Both return JSON-compatible structures under `data`.

### Static Assets

**`/static/comp.webp`** — Served via catch-all when route matches physical file in `/static/`.

Requested from template as `<manifest.route>/comp.webp`. Pattern demonstrates internal component assets (not published in `public/`).

## Data and Models

### Translations

| Location | Purpose |
|----------|---------|
| `/schema.json` | Global menu/drawer translations |
| `/neutral/route/locale-*.json` | Shared route translations |
| `/neutral/route/root/test1/locale.json` | Test1-specific translations |
| `/neutral/route/root/test2/locale.json` | Test2-specific translations |
| `/neutral/route/root/translating-content/content-*.ntpl` | Language-specific templates |
| `/neutral/obj/locale-obj-comp.json` | Object translations |

All visible text uses `{:trans; ... :}` (except technical literals).

### Menu Integration

Same entries for `session:` and `session:true`:
- Home (`/`)
- Test1 (`/test1`)
- Test2 (`/test2`)
- Translating Content (`/translating-content`)
- Non-existent route (`/non-existent-route`)
- Error 500 (`/error-500`)
- Redirect (`/redirect`)

Links use schema references to `hellocomp_0yt2sa->manifest->route`.

---

## Acceptance Criteria (SDD)

### Functional
- [x] Root route renders visual showcase
- [x] Global snippet available on any route when enabled
- [x] Component snippet available on all routes under `<manifest.route>`
- [x] `/test1` uses custom handler with local data
- [x] `/comp.webp` served from `/static/`
- [x] Non-existent static routes return 404

### Technical
- [x] AJAX routes require `Requested-With-Ajax` header
- [x] Full-page templates end with `{:^;:}`
- [x] All translations use `{:trans; ... :}`
- [x] Tests derive `<manifest.route>` from `/manifest.json`

## Technical Rationale

- **Private library pattern**: `/lib` in `sys.path` with UUID-namespaced package (`hellocomp_0yt2sa`)
- **Custom handler pattern**: `HelloCompRequestHandler` extends `RequestHandler` with local data
- **Multiple engines**: Demonstrates both Python and PHP Neutral objects
- **Asset delivery**: Internal assets via component route (not `public/`)

## Known Limitations

- Routes intentionally cause errors/redirections — understand before copying
- Modal form uses `GET` (demonstration only, not for mutable operations)
- Private library must use UUID namespace to avoid collisions
- Component routes for assets differ from `public/` contract

### Testing

```bash
source .venv/bin/activate && pytest -q <component-root>/tests
```

---

*Last updated: 2026-05-04*

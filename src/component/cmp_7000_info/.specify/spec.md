# Component: info_0yt2sa

## Executive Summary

Information pages component providing skeleton content for standard informational pages: About, Contact, Help, and Legal. All pages share a common layout snippet with placeholder content and are publicly accessible. The component also registers session and drawer menu entries for navigation to these pages.

## Identity

- **UUID**: `info_0yt2sa`
- **Base Route**: `/info`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

**Security properties:**
- All routes are public (no authentication required)
- No forms, mutations, or sensitive data
- Read-only content delivery

## Architecture

### Component Type

**Static content** component. Provides:
- Skeleton informational pages (About, Contact, Help, Legal)
- Shared layout snippet with placeholder content
- Session menu entries (anonymous + authenticated)
- Drawer menu entries (anonymous + authenticated)
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_7000_info/
├── manifest.json                          # Identity and security
├── schema.json                            # Menus, translations, inheritance
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   └── routes.py                          # Route definitions
├── neutral/
│   └── route/
│       ├── index-snippets.ntpl            # Locale loader + shared snippet include
│       ├── snippets.ntpl                  # Shared placeholder content (info:sample-body-main-content)
│       ├── locale-{lang}.json             # Translations (6 languages)
│       └── root/
│           ├── about/
│           │   ├── data.json              # Route metadata
│           │   └── content-snippets.ntpl  # Page content
│           ├── contact/
│           │   ├── data.json
│           │   └── content-snippets.ntpl
│           ├── help/
│           │   ├── data.json
│           │   └── content-snippets.ntpl
│           └── legal/
│               ├── data.json
│               └── content-snippets.ntpl
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/info/<path:route>` | GET | `info_catch_all` | Catch-all for all `/info/*` subroutes |

**Handler logic:**
- Single catch-all route delegates to `RequestHandler(g.pr, route, bp.neutral_route)`
- `RequestHandler.render_route()` resolves the subroute to the corresponding `content-snippets.ntpl` under `neutral/route/root/<subroute>/`
- If no matching subroute exists, the handler returns a rendered 404

### Key Business Logic

- **Catch-all routing**: The single route `/info/<path:route>` handles all subpaths. The `RequestHandler` maps the path segment to a directory under `neutral/route/root/`.
- **Shared content**: All four pages include the same `info:sample-body-main-content` snippet from `snippets.ntpl`, wrapped in a theme container div.
- **Locale loading**: `index-snippets.ntpl` loads the locale file for the current language, falling back to `locale-en.json`.

### Dependencies

- **Depends on**: `RequestHandler` core for route rendering
- **Depends on**: `http_errors` component for 404 rendering on unmatched subroutes
- **Menu integration**: Session menu and drawer menu entries reference this component's route via `[:;data->info_0yt2sa->manifest->route:]` BIF

## Data and Models

### Route Data (`data.json`)

Each subroute defines standard metadata:

| Route | title | description | h1 |
|-------|-------|-------------|-----|
| `/info/about` | About Neutral TS PWA | About Neutral TS PWA Skeleton for PWA in Python | About |
| `/info/contact` | Contact Neutral TS PWA | Contact Neutral TS PWA Skeleton for PWA in Python | Contact |
| `/info/help` | Help Neutral TS PWA | Help Neutral TS PWA Skeleton for PWA in Python | Help |
| `/info/legal` | Legal Neutral TS PWA | Legal Neutral TS PWA Skeleton for PWA in Python | Legal |

### Translations (`inherit.locale.trans`)

6 languages with page title translations:

| Key | EN | ES | FR | DE | AR | ZH |
|-----|----|----|----|----|----|-----|
| Information | — | Información | Informations | Informationen | معلومات | 信息 |
| About | — | Acerca de | À propos | Über | حول | 关于 |
| Help | — | Ayuda | Aide | Hilfe | مساعدة | 帮助 |
| Contact | — | Contacto | Contact | Kontakt | اتصل | 联系 |
| Legal | — | Aviso legal | Mentions légales | Impressum | معلومات قانونية | 法律信息 |

Full locale files in `neutral/route/locale-{lang}.json` also include translated route titles and descriptions for each subpage.

### Session Menu (`data.current.menu`)

Menu entries for both anonymous (`session:`) and authenticated (`session:true`) users:

| Entry | Text | Link | Icon |
|-------|------|------|------|
| about | About | `[:;data->info_0yt2sa->manifest->route:]/about` | `x-icon-about` |
| help | Help | `[:;data->info_0yt2sa->manifest->route:]/help` | `x-icon-help` |
| contact | Contact | `[:;data->info_0yt2sa->manifest->route:]/contact` | `x-icon-contact` |
| legal | Legal | `[:;data->info_0yt2sa->manifest->route:]/legal` | `x-icon-legal` |

### Drawer Menu (`data.current.drawer.menu`)

| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| info | Information | info | `x-icon-help` |

Present for both anonymous (`session:`) and authenticated (`session:true`) users.

## Configuration

No component-specific configuration keys. Relies on core `RequestHandler` and theme system.

## Technical Rationale

- **Catch-all route**: A single route handles all subpaths, delegating to `RequestHandler` for template resolution. This avoids repetitive route definitions for each static page.
- **Shared snippet**: All pages use the same `info:sample-body-main-content` placeholder, making it easy to swap content later without changing route logic.
- **BIF route references**: Menu links use `[:;data->info_0yt2sa->manifest->route:]` so they remain correct even if the base route changes.
- **Locale fallback**: `index-snippets.ntpl` falls back to `locale-en.json` when no language-specific locale file exists.
- **Placeholder content**: Pages contain Lorem Ipsum-style skeleton content intended to be replaced with real content during project customization.

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/info/about` renders the About page with shared placeholder content
- [x] `/info/contact` renders the Contact page with shared placeholder content
- [x] `/info/help` renders the Help page with shared placeholder content
- [x] `/info/legal` renders the Legal page with shared placeholder content
- [x] Unmatched `/info/*` subroutes return a rendered 404
- [x] Session menu entries appear for both anonymous and authenticated users
- [x] Drawer menu entry appears for both anonymous and authenticated users

### Technical
- [x] Single catch-all route handles all `/info/*` subpaths
- [x] All subroute content uses `current:template:body-main-content` snippet contract
- [x] Route data provides `title`, `description`, and `h1` for each subroute
- [x] Translations provided in 6 languages (EN, ES, FR, DE, AR, ZH)
- [x] Menu links use BIF `[:;data->info_0yt2sa->manifest->route:]` for route resolution
- [x] Tests cover all 4 subroutes and the catch-all behavior

### Security
- [x] All routes are public (`"/": false`)
- [x] No forms or state mutations
- [x] No sensitive data exposure

# Component: home_0yt2sa

## Executive Summary

Home page component providing the landing page for Neutral TS Starter Py. Displays a hero section with project overview, feature cards highlighting key capabilities (modular architecture, NTPL templating, PWA support, security, i18n, Flask), and call-to-action links to GitHub and documentation. Serves as the primary entry point for visitors and provides navigation menu integration for both anonymous and authenticated users.

## Identity

- **UUID**: `home_0yt2sa`
- **Base Route**: `/`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- Route is publicly accessible without authentication
- No sensitive operations or data access
- Static content only with external links to GitHub and documentation

## Architecture

### Component Type
**Landing page** component. Provides:
- Public home page at root URL
- Hero section with project branding
- Feature showcase cards (6 features)
- Call-to-action buttons
- Navigation menu entries for all users
- Drawer menu integration
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_NNNN_home/
├── manifest.json                          # Identity and security
├── schema.json                            # Menus, translations
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   └── routes.py                          # Route definitions
└── neutral/
    └── route/
        ├── index-snippets.ntpl            # Auto-loaded snippets
        ├── data.json                      # Route metadata (title, description, h1)
        ├── locale-{lang}.json             # Translations (6 languages)
        └── root/
            └── content-snippets.ntpl      # Home page content
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/` | GET | `RequestHandler` | Home page (landing) |

### Request Handlers

Uses the base `RequestHandler` class from `core.request_handler`. No custom handlers required — the route simply renders the NTPL template through the standard dispatch mechanism.

### Key Features

#### Hero Section (`body-hero` snippet)
- Project badges (Neutral TS, Flask, Open Source, PWA)
- Main headline and description
- Two call-to-action buttons (Get Started, Documentation)

#### Feature Cards (6 cards in grid)
1. **Modular Architecture** — Plug-and-play component system
2. **NTPL Templating** — Schema-driven snippet composition
3. **PWA Support** — Service worker, offline page, web manifest
4. **Security First** — CSP, headers, tokens, rate limiting
5. **Internationalization** — Full i18n with locale files
6. **Flask Powered** — Application factory, Python 3.10–3.14

#### Call-to-Action Section
- GitHub repository link with icon
- Secondary heading encouraging users to start building

### Dependencies

- **Depends on**: Core `RequestHandler`, base layout templates
- **Used by**: Navigation system (menu/drawer), catch-all route component

## Data and Models

### Template Data Structure (`neutral/route/data.json`)

```json
{
  "data": {
    "current": {
      "route": {
        "title": "Neutral TS Starter Py - Modern PWA Starter Kit",
        "description": "A modular, opinionated starter kit for building Progressive Web Applications...",
        "h1": "Welcome to Neutral TS Starter Py"
      }
    }
  }
}
```

### Translations (`inherit.locale.trans` and `neutral/route/locale-*.json`)

**Schema translations (6 languages):**
| Key | EN | ES |
|-----|----|----|
| Home | Home | Inicio |
| Main | Main | Principal |

**Route translations include:**
- Project title and description
- Feature headings and descriptions
- Call-to-action labels
- Button texts

Full translations in EN, ES, DE, FR, AR, ZH.

### Session Menu (`data.current.menu`)

Menu entries for both anonymous (`session:`) and authenticated (`session:true`) users:

| Entry | Text | Link | Icon |
|-------|------|------|------|
| home | Home | `/` | `x-icon-home` |

### Drawer Menu (`data.current.drawer.menu`)

| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| main | Main | main | `x-icon-home` |

## Configuration

No component-specific configuration keys. The component uses:
- `current->theme->color` for hero background
- `current->theme->class->container` for content container

## Technical Rationale

- **Simple RequestHandler**: No custom handlers needed for static landing content
- **Hero snippet pattern**: Uses `current:template:body-hero` for hero section
- **Body content pattern**: Uses `current:template:body-main-content` for main content
- **Theme integration**: Leverages theme variables for consistent styling
- **Full i18n**: All user-facing text is translatable
- **No forms or AJAX**: Pure informational page with external links only

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/` displays home page with hero section
- [x] Hero shows project badges, title, description, and CTA buttons
- [x] 6 feature cards display with icons, titles, and descriptions
- [x] Call-to-action section links to GitHub repository
- [x] All text is translatable via locale files
- [x] Page renders correctly in all 6 supported languages

### Technical
- [x] Route uses base `RequestHandler` class
- [x] Template defines `current:template:body-hero` snippet
- [x] Template defines `current:template:body-main-content` snippet
- [x] No authentication required (`routes_auth: {"/": false}`)
- [x] Public access for all roles (`routes_role: {"/": ["*"]}`)

### Integration
- [x] Session menu entry for anonymous users
- [x] Session menu entry for authenticated users
- [x] Drawer menu entry for both user states
- [x] Menu links point to `/`
- [x] Uses `x-icon-home` icon consistently

### Quality
- [x] Translations complete in 6 languages
- [x] Theme integration (color, container classes)
- [x] No inline styles (all via CSS classes)
- [x] External links use proper `target="_blank"` where applicable

---

*Last updated: 2026-05-04*

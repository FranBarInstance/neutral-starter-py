# Component: materialicons_0yt2sa

## Executive Summary

Provides Material Design Icons (MDI) for the application. Serves the CSS stylesheet and font files via dedicated routes and automatically injects the stylesheet into every page through global snippet injection.

## Identity

- **UUID**: `materialicons_0yt2sa`
- **Base Route**: `/materialicons`
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

## Architecture

### Component Type
**Icon font provider** component. Provides:
- Static routes serving Material Design Icons CSS and fonts
- Global stylesheet injection via `component-init.ntpl`
- Icon variable definitions via `schema.json` for framework-agnostic usage
- Icon gallery snippet via `icons-snippets.ntpl`

### Directory Structure

```
src/component/cmp_NNNN_materialicons/
├── manifest.json              # Identity and security
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving routes
├── neutral/
│   ├── component-init.ntpl    # Global stylesheet injection
│   └── icons-snippets.ntpl    # Icon gallery snippet
├── schema.json                # Icon variable definitions
└── static/
    ├── materialdesignicons.min.css  # MDI stylesheet
    └── fonts/                       # MDI font files (woff2, etc.)
```

### Routes (`route/routes.py`)

**`/materialdesignicons.min.css`** (GET)
- Serves `materialdesignicons.min.css` from component's `static/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

**`/fonts/<filename>`** (GET)
- Serves font files from `static/fonts/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

### Global Stylesheet Injection (`neutral/component-init.ntpl`)

Automatically injects Material Design Icons CSS into every page:

```ntpl
{:snip; materialicons_0yt2sa-head >>
    <link nonce="{:;CSP_NONCE:}" rel="stylesheet" href="{:;materialicons_0yt2sa->manifest->route:}/materialdesignicons.min.css" />
:}

{:moveto; /head >> {:snip; materialicons_0yt2sa-head :} :}
```

**CSP Compliance:** Uses `{:;CSP_NONCE:}` placeholder for nonce attribute.

### Icon Variables (schema.json)

The component defines 84 icon variables in `data.x-icons` that map semantic names to MDI classes. This allows framework-agnostic icon usage:

```json
{
  "data": {
    "x-icons": {
      "x-icon-help": "x-icon mdi mdi-help-circle-outline",
      "x-icon-home": "x-icon mdi mdi-home-variant-outline",
      "x-icon-menu": "x-icon mdi mdi-menu",
      ...
    }
  }
}
```

**Benefits:**
- Icons can be referenced by semantic name (`x-icon-home`) rather than framework-specific class (`mdi mdi-home-variant-outline`)
- If the icon font changes, only the mapping needs updating
- Consistent naming across the application

### Icon Gallery Snippet (icons-snippets.ntpl)

**`current:list-x-icons`** - Renders a visual grid of all available icons with their variable names.

Features:
- Responsive CSS grid layout
- Hover effects with shadow
- Displays both icon and variable name
- Uses `x-icons` data from schema

### Dependencies

- **No dependencies**: Self-contained icon font component
- **Used by**: All components needing Material Design Icons

## Data and Models

### Icon Variables (`data.x-icons`)

84 semantic icon variables mapping to MDI classes:

| Variable | MDI Class | Usage |
|----------|-----------|-------|
| `x-icon-home` | `mdi mdi-home-variant-outline` | Home navigation |
| `x-icon-menu` | `mdi mdi-menu` | Menu toggle |
| `x-icon-setting` | `mdi mdi-cog-outline` | Settings |
| `x-icon-user` | `mdi mdi-account-outline` | User profile |
| `x-icon-sign-in` | `mdi mdi-login` | Login action |
| `x-icon-sign-out` | `mdi mdi-logout` | Logout action |
| `x-icon-edit` | `mdi mdi-square-edit-outline` | Edit action |
| `x-icon-trash` | `mdi mdi-trash-can-outline` | Delete action |
| ... | ... | ... |

See `schema.json` for complete list.

## Technical Rationale

- **Global Availability**: By injecting via `component-init.ntpl`, MDI is available on every page without manual inclusion
- **CDN Alternative**: Self-hosted fonts avoid external CDN dependencies
- **CSP Compliant**: Uses nonce placeholder for inline link tag
- **Cache Control**: Proper HTTP cache headers for static assets
- **Font Serving**: Dedicated route for font files referenced by the CSS
- **Framework Agnostic**: Icon variables allow swapping icon fonts without changing templates

---

## Acceptance Criteria (SDD)

### Functional
- [x] `route/routes.py` serves `materialdesignicons.min.css` at `/materialicons/materialdesignicons.min.css`
- [x] `route/routes.py` serves font files at `/materialicons/fonts/<filename>`
- [x] `component-init.ntpl` injects stylesheet into page head on every render
- [x] `icons-snippets.ntpl` provides `current:list-x-icons` gallery snippet
- [x] `schema.json` defines 84 icon variables in `data.x-icons`
- [x] Link uses CSP nonce placeholder

### Technical
- [x] Route exposed at `/materialicons` (base route from manifest)
- [x] Static file serving with proper cache headers
- [x] No authentication required for icon access
- [x] CSP-compliant stylesheet injection

### Integration
- [x] Global stylesheet injection affects all pages
- [x] Icons accessible via MDI classes (e.g., `mdi mdi-home`)
- [x] Icons accessible via variables (e.g., `x-icon-home`)
- [x] Route path derived from `manifest->route` BIF
- [x] Font files properly referenced by CSS

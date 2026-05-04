# Component: site_0yt2sa

## Executive Summary

Provides site-level data (name, title, description, branding assets) and translations for the application. Overrides default values from `cmp_0100_default` with project-specific branding and reserves the language selector menu position.

## Identity

- **UUID**: `site_0yt2sa`
- **Base Route**: `` (no routes - provides configuration only)
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
**Pure configuration** component (no routes, no handlers, no templates).
Provides site branding data and locale translations through `schema.json`.

### Directory Structure

```
src/component/cmp_NNNN_site/
├── manifest.json          # Identity and security
└── schema.json            # Site data, translations, and menu placeholders
```

### Dependencies

- **Depends on**: `cmp_0100_default` (for base site structure)
- **Used by**: All components that reference site data or translations

## Data and Models

### Site Data (`data.current.site`)

| Key | Value | Purpose |
|-----|-------|---------|
| `name` | `Neutral TS !` | Site name for branding |
| `title` | `Neutral TS PWA !` | Page title suffix |
| `description` | `Neutral TS Skeleton...` | SEO meta description |
| `cover` | `/img/cover.jpg` | Default cover image path |
| `logo` | `/img/logo.jpg` | Logo image path |
| `static` | `/` | Static assets base path |
| `home_link` | `/` | Home page link |

### Translations (`inherit.locale.trans`)

Provides translations for 6 languages:
- **en** - English
- **es** - Spanish
- **de** - German
- **fr** - French
- **ar** - Arabic
- **zh** - Chinese

Translation keys match the site data values with `!` suffix for disambiguation.

### Menu Placeholders

Reserves navbar language menu positions:
- `data.navbar.menu.session:language` - For anonymous users
- `data.navbar.menu.session:true:language` - For authenticated users

## Acceptance Criteria (SDD)

### Functional
- [x] `schema.json` provides site branding data
- [x] Translations cover all 6 base languages (en, es, de, fr, ar, zh)
- [x] Translation keys use `!` suffix pattern for disambiguation
- [x] Navbar language menu placeholders reserved in both session states

### Technical
- [x] No routes, handlers, or templates
- [x] Loads after `cmp_0100_default` (prefix 0300 > 0100) to override defaults
- [x] Uses `inherit.locale` for translation inheritance (Neutral TS specific)

### Integration
- [x] Site data accessible via `current->site->*` in templates
- [x] Translations accessible via `trans` BIF
- [x] Menu placeholders available for language selector components

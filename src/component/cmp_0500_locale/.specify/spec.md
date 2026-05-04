# Component: locale_0yt2sa

## Executive Summary

Provides complete internationalization (i18n) infrastructure including language configuration, directionality (LTR/RTL), locale translations, and dynamic language selector menus. This component builds the language menu at runtime based on configured languages and creates dropdown items for each available language.

## Identity

- **UUID**: `locale_0yt2sa`
- **Base Route**: `` (no routes - provides configuration and runtime menus)
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
**I18n configuration** component. Provides:
- Language configuration via `schema.json`
- Runtime language menu generation via `__init__.py`
- Locale name translations for the selector UI

### Directory Structure

```
src/component/cmp_NNNN_locale/
├── manifest.json          # Identity, security, and menu config
├── __init__.py            # Runtime menu generation
├── schema.json            # Languages config, translations, menus
└── neutral/
    └── (snippets if needed)
```

### Runtime Menu Generation (`__init__.py`)

The `init_component()` function runs at application startup and dynamically builds language menus:

**`menu_drawer()` function:**
- Reads `site.languages` array from schema
- Creates language dropdown menu in the configured drawer tab
- Links use query parameter format: `?lang={code}`
- Menu text uses `ref:locale:{lang}` translation keys
- Disabled if fewer than 2 languages or `menu-drawer-enable` is false

**`menu_navbar()` function:**
- Creates language dropdown in navbar for both session states
- Same structure as drawer menu but positioned in top navigation
- Disabled if fewer than 2 languages or `menu-navbar-enable` is false

### Dependencies

- **Depends on**: `cmp_0300_site` (for `site.languages` configuration)
- **Used by**: All components (language selector appears globally)

## Data and Models

### Language Configuration (`data.current.site`)

| Key | Type | Description |
|-----|------|-------------|
| `languages` | string[] | Available language codes: `["en", "es", "de", "fr", "ar", "zh"]` |
| `languages_dir` | object | Text direction per language: `{"en": "ltr", "ar": "rtl"}` |

### Locale Translations (`inherit.locale.trans`)

**Language Names (reference keys):**
- `ref:locale:en` → "English"
- `ref:locale:es` → "Español"
- `ref:locale:de` → "Deutsch"
- `ref:locale:fr` → "Français"
- `ref:locale:ar` → "العربية"
- `ref:locale:zh` → "中文"

**UI Translations per language:**
- "Language", "Open", "Close", "Menu", "Back"

### Menu Structure

**Drawer (`data.current.drawer.menu`):**
- Configurable tab (default: `setting`) with icon `x-icon-setting`
- Language dropdown with all configured languages

**Navbar (`data.navbar.menu`):**
- `language` dropdown for both `session:` and `session:true`

## Configuration (`manifest.json`)

| Config Key | Type | Default | Purpose |
|------------|------|---------|---------|
| `menu-drawer-tab` | string | `setting` | Drawer tab ID for language menu |
| `menu-drawer-tab-name` | string | `Setting` | Display name for the tab |
| `menu-drawer-tab-icon` | string | `x-icon-setting` | Icon class for the tab |
| `menu-drawer-enable` | boolean | `true` | Enable language menu in drawer |
| `menu-navbar-enable` | boolean | `true` | Enable language menu in navbar |

## Technical Rationale

- **Dynamic Generation**: Menus are built at runtime based on `site.languages`, allowing language changes without code modification
- **Query Parameter**: Language switching uses `?lang={code}` format (reads `Config.LANG_KEY`)
- **Reference Keys**: Language names use `ref:` prefix so they can be referenced consistently across the application
- **Conditional Display**: Automatically hides language selector if only one language is configured

---

## Acceptance Criteria (SDD)

### Functional
- [x] `schema.json` defines 6 supported languages with LTR/RTL directionality
- [x] Translations provided for all language names in 6 languages
- [x] UI translations ("Language", "Open", "Close", "Menu", "Back") in 5 non-English languages
- [x] `__init__.py` generates drawer language menu dynamically
- [x] `__init__.py` generates navbar language menu dynamically
- [x] Menu links use query parameter format with `Config.LANG_KEY`

### Technical
- [x] No routes exposed (empty base route)
- [x] `__init__.py` reads `site.languages` from component_schema at runtime
- [x] Conditional menu generation based on language count and config flags
- [x] Uses `ref:locale:{lang}` pattern for language name references

### Integration
- [x] Depends on `cmp_0300_site` for language configuration
- [x] Menu structure compatible with drawer and navbar systems
- [x] Loads after `cmp_0300_site` (prefix 0500 > 0300)

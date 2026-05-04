# Component: theme_0yt2sa

## Executive Summary

Provides the complete theming system for the application, including CSS/JS asset injection, theme configuration, dark mode support, and settings UI. This component is critical as it affects every page render through global asset injection and provides the visual foundation for the entire application.

## Identity

- **UUID**: `theme_0yt2sa`
- **Base Route**: `` (no routes - provides global assets and configuration)
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
**Global theming** component. Provides:
- Global CSS/JS injection via `component-init.ntpl`
- Theme configuration data via `schema.json`
- Runtime menu configuration via `__init__.py`

### Directory Structure

```
src/component/cmp_NNNN_theme/
├── manifest.json              # Identity, security, and config
├── __init__.py                # Conditional menu initialization
├── schema.json                # Theme data, translations, menus
└── neutral/
    └── component-init.ntpl    # Global CSS/JS injection snippets
```

### Global Asset Injection (`component-init.ntpl`)

The `component-init.ntpl` automatically injects theme assets into every page:

**`theme_0yt2sa-head` snippet (moved to `/head`):**
- Bootstrap 5 CSS (`bootstrap.min.css`)
- Theme preset CSS (`{theme}.min.css`)
- Dark mode CSS (`dark.min.css` with `media="not all"`)
- Custom CSS (`neutral-custom.min.css`)
- BTDT JS (`btdt.min.js`) with dark mode configuration via data attributes

**`theme_0yt2sa-body-end` snippet (moved to `theme-script`):**
- Bootstrap 5 JS bundle

**CSP Compliance:** All inline styles and scripts use `{:;CSP_NONCE:}` placeholder.

### Runtime Configuration (`__init__.py`)

The `init_component()` function runs at application startup:

```python
if not component['manifest']['config']['menu-drawer-enable']:
    # Remove darkmode menu items from both session states
    component_schema['data']['current']['menu']['session:']['setting']['darkmode'] = None
    component_schema['data']['current']['menu']['session:true']['setting']['darkmode'] = None
```

This allows disabling the theme menu via `manifest.json` config without modifying code.

### Dependencies

- **Depends on**: `cmp_0300_site` (for `current->site->static` path)
- **Used by**: All components (global asset injection affects every page)

## Data and Models

### Theme Configuration (`data.current.theme`)

| Key | Type | Purpose |
|-----|------|---------|
| `theme` | string | Active theme identifier (references preset file) |
| `color` | string | Active color variant |
| `class` | object | CSS class mappings for containers, buttons, etc. |
| `spin` | string | Spinner CSS class |
| `theme_allowed` | string[] | List of available themes |
| `color_allowed` | string[] | List of available colors |

### Translations (`inherit.locale.trans`)

Provides translations for settings UI:
- "Setting" / "Configuración" / "Einstellung" / etc.
- "Dark mode" / "Modo oscuro" / "Dark Mode" / etc.

Languages: ES, DE, FR, AR, ZH

### Menu Structure

**Navbar (`data.current.menu`):**
- `setting.darkmode` - Dark mode toggle in navbar settings menu (both session states)

**Drawer (`data.current.drawer.menu`):**
- `setting` tab - Settings navigation tab with icon and translations

### Carousel (`inherit.data.current.carousel`)

Empty array placeholder for carousel configuration inheritance.

## Configuration (`manifest.json`)

| Config Key | Type | Default | Purpose |
|------------|------|---------|---------|
| `menu-drawer-enable` | boolean | `true` | Enable/disable theme menu items |

## Technical Rationale

- **Global Injection**: `component-init.ntpl` runs for every component, ensuring consistent styling
- **Conditional Initialization**: Runtime menu configuration allows deployment-specific customization
- **Theme System**: Separates visual preset (Bootstrap + theme CSS) from color variant
- **Dark Mode**: CSS-based with cookie persistence, respects system preference
- **CSP Compliance**: All assets use nonces; external scripts use `crossorigin="anonymous"`

---

## Acceptance Criteria (SDD)

### Functional
- [x] `component-init.ntpl` injects CSS/JS on every page render
- [x] Theme preset CSS loads based on `current->theme->theme` value
- [x] Dark mode CSS loads with `media="not all"` for toggle support
- [x] BTDT JS initializes with dark mode configuration from data attributes
- [x] Translations provided for settings UI in 5 languages
- [x] Menu items for dark mode appear in navbar and drawer

### Technical
- [x] No routes exposed (empty base route)
- [x] `__init__.py` conditionally removes menus based on config
- [x] All inline resources use CSP nonce placeholder
- [x] External scripts use `crossorigin="anonymous"` and `referrerpolicy="no-referrer"`
- [x] Schema provides `theme_allowed` and `color_allowed` arrays

### Integration
- [x] CSS references use `current->site->static` for base path
- [x] Dark mode state reads from `USER->profile->properties->dark_mode`
- [x] Menu structure compatible with drawer system
- [x] Loads after `cmp_0300_site` (prefix 0400 > 0300) to ensure `site` data is available

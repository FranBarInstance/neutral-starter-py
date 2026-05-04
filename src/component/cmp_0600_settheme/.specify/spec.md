# Component: settheme_0yt2sa

## Executive Summary

Provides runtime theme and color selection menus for the application. Dynamically builds dropdown menus in drawer and navbar based on available themes and colors from `schema.json`. Users can switch themes and colors via query parameters.

## Identity

- **UUID**: `settheme_0yt2sa`
- **Base Route**: `` (no routes - provides runtime menus)
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
**Theme selector** component. Provides:
- Runtime theme menu generation via `__init__.py`
- Color selection menu generation
- Translations for theme/color names

### Directory Structure

```
src/component/cmp_NNNN_settheme/
├── manifest.json          # Identity, security, and menu config
├── __init__.py            # Runtime menu generation
└── schema.json            # Available themes/colors and translations
```

### Runtime Menu Generation (`__init__.py`)

The `init_component()` function runs at application startup and builds theme/color menus:

**`menu_drawer()` function:**
- Reads `allow_themes` and `allow_colors` arrays from schema
- Creates theme dropdown in drawer "setting" tab
- Creates color dropdown in drawer "setting" tab
- Links use query parameter format: `?theme={name}` or `?color={name}`
- Reads `Config.THEME_KEY` and `Config.THEME_COLOR_KEY` for parameter names
- Disabled if fewer than 2 options or config flag is false

**`menu_navbar()` function:**
- Creates theme and color dropdowns in navbar
- Same structure as drawer menus but positioned in top navigation
- Available for both anonymous and authenticated users

### Menu Builder Functions

**`build_drawer_menu(name, icon, values, config_key)`:**
- Creates dropdown menu with icon
- Each item has text, link with query parameter, and bullet icon
- Used for both theme and color menus in drawer

**`build_navbar_menu(name, icon, values, config_key)`:**
- Creates dropdown menu for navbar
- Each item has name, link with query parameter
- Uses `x-icon-none` for navbar items

### Dependencies

- **Depends on**: `cmp_0400_theme` (for theme configuration and CSS)
- **Used by**: All components (theme selector appears globally)

## Data and Models

### Available Themes (`data.current.theme.allow_themes`)

43 theme presets available:
- Base themes: `default`, `gray`, `paper`
- Color themes: `amber-roar`, `aurora`, `autumn-harvest`, `berry-smoothie`, `candy`, `rose-sonata`, `sky-forge`
- Studio variants: `studio`, `studio-asymmetric`, `studio-coupon`, `studio-fold`, `studio-notch`, `studio-pill`, `studio-skeuomorphism`, `studio-underline`, `studio-swiss`
- Blank variants: `blank`, `blank-asymmetric`, `blank-coupon`, `blank-fold`, `blank-swiss`, `blank-underline`
- Specialized: `boutique-chic`, `calm`, `cobalt-pro`, `mint-atelier`, `pwa`, `pwa-material`, `retro`, `royal-heritage`, `sketch`, `techno-splash`

### Available Colors (`data.current.theme.allow_colors`)

5 color variants:
- `primary`, `dark`, `secondary`, `light`, `white`

### Translations (`inherit.locale.trans`)

Provides translations for 6 languages:
- "Theme" / "Tema" / "Thème" / "Thema" / "الموضوع" / "主题"
- "Color" / "Color" / "Couleur" / "Farbe" / "اللون" / "颜色"
- "Colors" / "Colores" / "Couleurs" / "Farben" / "الألوان" / "颜色"
- Color names: primary, dark, secondary, light, body-tertiary, white, danger, warning, info, success, transparent

### Menu Structure

**Drawer (`data.current.menu`):**
- `setting.theme` - Theme dropdown (both session states)
- `setting.color` - Color dropdown (both session states)

**Navbar (`data.navbar.menu`):**
- `theme` - Theme dropdown (both session states)
- `color` - Color dropdown (both session states)

## Configuration (`manifest.json`)

| Config Key | Type | Default | Purpose |
|------------|------|---------|---------|
| `menu-theme-drawer-enable` | boolean | `true` | Enable theme menu in drawer |
| `menu-theme-navbar-enable` | boolean | `true` | Enable theme menu in navbar |
| `menu-color-drawer-enable` | boolean | `true` | Enable color menu in drawer |
| `menu-color-navbar-enable` | boolean | `false` | Enable color menu in navbar |

## Technical Rationale

- **Dynamic Generation**: Menus built at runtime from `allow_themes`/`allow_colors` arrays, allowing theme changes without code modification
- **Query Parameters**: Theme switching uses `?theme={name}` and `?color={name}` format (reads `Config.THEME_KEY` and `Config.THEME_COLOR_KEY`)
- **Conditional Display**: Automatically hides menus if fewer than 2 options available
- **Configurability**: Each menu can be enabled/disabled independently via manifest config

---

## Acceptance Criteria (SDD)

### Functional
- [x] `schema.json` defines 43 available themes and 5 color variants
- [x] Translations provided for theme/color names in 6 languages
- [x] `__init__.py` generates drawer theme menu dynamically
- [x] `__init__.py` generates drawer color menu dynamically
- [x] `__init__.py` generates navbar theme menu dynamically
- [x] `__init__.py` generates navbar color menu dynamically
- [x] Menu links use query parameter format with `Config.THEME_KEY` and `Config.THEME_COLOR_KEY`

### Technical
- [x] No routes exposed (empty base route)
- [x] `__init__.py` reads `allow_themes` and `allow_colors` from component_schema at runtime
- [x] Conditional menu generation based on option count and config flags
- [x] Separate builder functions for drawer and navbar menu structures

### Integration
- [x] Depends on `cmp_0400_theme` for theme configuration
- [x] Menu structure compatible with drawer and navbar systems
- [x] Loads after `cmp_0400_theme` (prefix 0600 > 0400)

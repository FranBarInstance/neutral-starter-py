# Component: materialicons_0yt2sa

Material Design Icons (MDI) provider.

## Overview

This component provides Material Design Icons for the application. It serves the CSS stylesheet and font files via dedicated routes, automatically injects the stylesheet into every page, and provides icon variables for framework-agnostic usage.

## Structure

- `manifest.json` - Component identity and security
- `route/routes.py` - Static file serving routes (CSS and fonts)
- `neutral/component-init.ntpl` - Global stylesheet injection
- `neutral/icons-snippets.ntpl` - Icon gallery snippet
- `schema.json` - Icon variable definitions (84 mappings)

## Routes

**`/materialicons/materialdesignicons.min.css`** (GET)
- Serves the MDI stylesheet
- Public access, no authentication required

**`/materialicons/fonts/<filename>`** (GET)
- Serves font files (woff2, etc.)
- Public access, no authentication required

## Global Stylesheet Injection

The `component-init.ntpl` automatically injects:

```html
<link nonce="{CSP_NONCE}" rel="stylesheet" href="/materialicons/materialdesignicons.min.css" />
```

Into the `<head>` of every page. CSP-compliant with nonce placeholder.

## Usage

### Method 1: Direct MDI Classes (Not Recommended)

```html
<span class="mdi mdi-home"></span>
<span class="mdi mdi-account"></span>
```

### Method 2: Icon Variables (Recommended)

Use icon variables from `data.x-icons` for framework-agnostic usage:

```ntpl
<span class="{:;local::x-icons->x-icon-home:}"></span>
<span class="{:;local::x-icons->x-icon-user:}"></span>
```

In menus:

```json
{
  "data": {
    "current": {
      "menu": {
        "session:": {
          "main": {
            "home": {
              "text": "Home",
              "link": "/",
              "icon": "x-icon-home"
            }
          }
        }
      }
    }
  }
}
```

**Benefits:**
- Framework-agnostic: Change icon font without updating templates
- Consistent naming across the application
- Semantic names (e.g., `x-icon-home` vs `mdi mdi-home-variant-outline`)

### Icon Gallery Snippet

Display all available icons:

```ntpl
{:snip; current:list-x-icons :}
```

This renders a responsive grid showing all 84 icon variables with their names.

## Icon Variables Available

84 semantic mappings including:
- Navigation: `x-icon-home`, `x-icon-menu`, `x-icon-back`, `x-icon-up/down/left/right`
- Actions: `x-icon-edit`, `x-icon-save`, `x-icon-send`, `x-icon-trash`, `x-icon-check`
- Users: `x-icon-user`, `x-icon-sign-in`, `x-icon-sign-out`, `x-icon-profile`
- System: `x-icon-setting`, `x-icon-help`, `x-icon-info`, `x-icon-error`

See `schema.json` for the complete list.

## Dependencies

- **None**: Self-contained icon font
- **Used by**: All components needing Material Design Icons

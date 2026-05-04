# Component: theme_0yt2sa

Global theming and asset injection component.

## Overview

This component provides the complete theming system for the application, including CSS/JS asset injection on every page, theme configuration, and dark mode support.

## Structure

- `manifest.json` - Component identity, security, and config
- `__init__.py` - Conditional menu initialization (removes darkmode menu if `menu-drawer-enable` is false)
- `schema.json` - Theme data, translations, and menu definitions
- `neutral/component-init.ntpl` - Global CSS/JS injection snippets

## Global Assets Injected

### Head (`theme_0yt2sa-head`)
- Bootstrap 5 CSS
- Theme preset CSS (`{theme}.min.css`)
- Dark mode CSS (`dark.min.css`)
- Custom CSS (`neutral-custom.min.css`)
- BTDT JS with dark mode configuration

### Body End (`theme_0yt2sa-body-end`)
- Bootstrap 5 JS bundle

## Configuration

Via `manifest.json` config:
- `menu-drawer-enable` (bool, default: true) - Enable/disable theme menu items

## Theme Data

Accessible via `current->theme->*`:
- `theme` - Active theme identifier
- `color` - Active color variant
- `class` - CSS class mappings
- `theme_allowed` - Available themes array
- `color_allowed` - Available colors array

## Usage

All templates automatically receive theme assets. Access theme values:

```ntpl
{:;current->theme->theme:}
{:;current->theme->class->container:}
```

## Dark Mode

- Toggle in navbar settings menu
- Persists via cookie (`dark-mode-on`)
- Respects system preference
- State stored in `USER->profile->properties->dark_mode`

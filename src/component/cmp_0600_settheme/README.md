# Component: settheme_0yt2sa

Theme and color selector menu component.

## Overview

This component provides runtime theme and color selection menus for the application. It dynamically builds dropdown menus in the drawer and navbar based on available themes and colors defined in `schema.json`.

## Structure

- `manifest.json` - Component identity, security, and menu configuration
- `__init__.py` - Runtime theme/color menu generation
- `schema.json` - Available themes/colors and translations

## Available Themes

43 theme presets including:
- Base: `default`, `gray`, `paper`
- Color themes: `amber-roar`, `aurora`, `autumn-harvest`, `berry-smoothie`, `candy`, `rose-sonata`, `sky-forge`
- Studio variants: `studio`, `studio-asymmetric`, `studio-coupon`, `studio-fold`, `studio-notch`, `studio-pill`, `studio-skeuomorphism`, `studio-underline`, `studio-swiss`
- Blank variants: `blank`, `blank-asymmetric`, `blank-coupon`, `blank-fold`, `blank-swiss`, `blank-underline`
- Specialized: `boutique-chic`, `calm`, `cobalt-pro`, `mint-atelier`, `pwa`, `pwa-material`, `retro`, `royal-heritage`, `sketch`, `techno-splash`

## Available Colors

5 color variants: `primary`, `dark`, `secondary`, `light`, `white`

## Menu Generation

The `__init__.py` generates menus dynamically at application startup:

### Drawer Menus
- Theme dropdown in "setting" tab
- Color dropdown in "setting" tab

### Navbar Menus
- Theme dropdown in top navigation
- Color dropdown in top navigation

## Configuration

Via `manifest.json` config:
- `menu-theme-drawer-enable` - Enable theme menu in drawer (default: `true`)
- `menu-theme-navbar-enable` - Enable theme menu in navbar (default: `true`)
- `menu-color-drawer-enable` - Enable color menu in drawer (default: `true`)
- `menu-color-navbar-enable` - Enable color menu in navbar (default: `false`)

## How It Works

1. Reads `allow_themes` and `allow_colors` arrays from schema
2. Builds dropdown menus with query parameter links (`?theme={name}` or `?color={name}`)
3. Automatically hides menus if fewer than 2 options available
4. Respects manifest config flags for enabling/disabling specific menus

## Usage

Theme and color selectors appear automatically in the UI when enabled and multiple options are available. Clicking an option switches the theme/color via query parameter.

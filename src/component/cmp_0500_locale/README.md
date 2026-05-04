# Component: locale_0yt2sa

Internationalization (i18n) and language selector component.

## Overview

This component provides the complete internationalization infrastructure including language configuration, text directionality (LTR/RTL), locale translations, and dynamic language selector menus. It builds the language menu at runtime based on configured languages.

## Structure

- `manifest.json` - Component identity, security, and menu configuration
- `__init__.py` - Runtime language menu generation
- `schema.json` - Languages config, translations, and menu definitions

## Language Configuration

Defines 6 supported languages:
- `en` (English, LTR)
- `es` (Spanish, LTR)
- `de` (German, LTR)
- `fr` (French, LTR)
- `ar` (Arabic, RTL)
- `zh` (Chinese, LTR)

## Menu Generation

The `__init__.py` generates language menus dynamically:

### Drawer Menu
- Located in "setting" tab by default
- Dropdown with all configured languages
- Links use `?lang={code}` format

### Navbar Menu
- Language dropdown in top navigation
- Available for both anonymous and authenticated users

## Configuration

Via `manifest.json` config:
- `menu-drawer-tab` - Tab ID for drawer menu (default: `setting`)
- `menu-drawer-enable` - Enable drawer language menu (default: `true`)
- `menu-navbar-enable` - Enable navbar language menu (default: `true`)

## Translations

Provides translations in 6 languages for:
- Language names (`ref:locale:*`)
- UI strings: "Language", "Open", "Close", "Menu", "Back"

## Usage

Language selector appears automatically when 2+ languages are configured. Clicking a language option switches via query parameter.

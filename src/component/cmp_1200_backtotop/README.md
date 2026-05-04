# Component: backtotop_0yt2sa

Back-to-top button and navbar hide-on-scroll component.

## Overview

This component provides a "back to top" button that appears when the user scrolls down the page, and hides the navbar on scroll for better content viewing.

## Structure

- `manifest.json` - Component identity and security
- `route/routes.py` - Static file serving routes (CSS and JS)
- `neutral/component-init.ntpl` - Global CSS/JS injection
- `schema.json` - Translations for accessibility labels
- `static/css/backtotop.min.css` - Component styles
- `static/js/backtotop.min.js` - Scroll detection and smooth scrolling

## Routes

**`/backtotop/css/backtotop.min.css`** (GET)
- Serves the back-to-top CSS
- Public access, no authentication required

**`/backtotop/js/backtotop.min.js`** (GET)
- Serves the back-to-top JavaScript
- Public access, no authentication required

## Global Asset Injection

The `component-init.ntpl` automatically injects:
- CSS into the `<head>`
- Back-to-top button and JavaScript at the end of `<body>`

## Features

- **Back-to-top button**: Appears after scrolling 250px down
- **Navbar auto-hide**: Hides on scroll down, shows on scroll up
- **Smooth scrolling**: Native smooth scroll behavior
- **Theme integration**: Uses `current->theme->color` for styling
- **Accessibility**: Proper ARIA labels with translations

## Configuration

Scroll behavior is configurable via `window.backToTopConfig`:

| Setting | Default | Description |
|---------|---------|-------------|
| `hideThreshold` | 50 | Pixels before hiding navbar |
| `scrollUpThreshold` | 50 | Pixels up before showing navbar |
| `backToTopThreshold` | 250 | Pixels before showing button |
| `peekHeight` | 8 | Navbar peek height when hidden |
| `scrollToBehavior` | 'smooth' | Scroll animation type |

## Dependencies

- **Depends on**: `theme_0yt2sa` (for theme color)
- **Used by**: All pages (global injection)

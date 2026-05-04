# Component: backtotop_0yt2sa

## Executive Summary

Provides a "back to top" button that appears when the user scrolls down the page, and hides the navbar on scroll for better content viewing. The component includes CSS for styling, JavaScript for scroll detection and smooth scrolling behavior, and translations for accessibility labels.

## Identity

- **UUID**: `backtotop_0yt2sa`
- **Base Route**: `/backtotop`
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
**UI enhancement** component. Provides:
- Static routes serving CSS and JavaScript files
- Global CSS/JS injection via `component-init.ntpl`
- Translations for accessibility labels

### Directory Structure

```
src/component/cmp_NNNN_backtotop/
├── manifest.json              # Identity and security
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving routes
├── neutral/
│   └── component-init.ntpl    # Global CSS/JS injection
├── schema.json                # Translations
└── static/
    ├── css/backtotop.min.css  # Back to top styles
    └── js/backtotop.min.js    # Back to top interactivity
```

### Routes (`route/routes.py`)

**`/css/backtotop.min.css`** (GET)
- Serves `backtotop.min.css` from component's `static/css/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

**`/js/backtotop.min.js`** (GET)
- Serves `backtotop.min.js` from component's `static/js/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

### Global Asset Injection (`neutral/component-init.ntpl`)

**`backtotop_0yt2sa-head` snippet (moved to `/head`):**
- Back to top CSS (`backtotop.min.css`)

**`backtotop_0yt2sa-body-end` snippet (moved to `/body`):**
- Back to top button with SVG icon and theme color support
- Configuration script with scroll thresholds
- Back to top JavaScript (`backtotop.min.js`)

**Key Features:**
- Button uses theme color (`current->theme->color`)
- Accessibility attributes: `title`, `aria-label` with translations
- SVG icon for the up arrow
- Configurable scroll behavior via `window.backToTopConfig`

**CSP Compliance:** All inline styles and scripts use `{:;CSP_NONCE:}` placeholder.

### Configuration

**Scroll Behavior Settings (`window.backToTopConfig`):**
| Setting | Value | Description |
|---------|-------|-------------|
| `hideThreshold` | 50 | Pixels to scroll before hiding navbar |
| `scrollUpThreshold` | 50 | Pixels to scroll up before showing navbar |
| `backToTopThreshold` | 250 | Pixels to scroll before showing back-to-top button |
| `peekHeight` | 8 | Height of navbar peek when hidden |
| `scrollToBehavior` | 'smooth' | Smooth scroll behavior |

### Dependencies

- **Depends on**: `cmp_0400_theme` (for `current->theme->color`)
- **Used by**: All pages (global injection affects every page)

## Data and Models

### Translations (`inherit.locale.trans`)

Provides translations for the back-to-top button title/aria-label in 6 languages:

| Language | Translation |
|----------|-------------|
| EN | "Go to top of page" |
| ES | "Volver arriba" |
| DE | "Zurück zur oberen Seite" |
| FR | "Retour en haut de page" |
| AR | "اذهب إلى أعلى الصفحة" |
| ZH | "转到页面顶部" |

**Reference key:** `ref:backtotop:go-top`

## Technical Rationale

- **Global Injection**: `component-init.ntpl` ensures back-to-top button appears on every page
- **Theme Integration**: Uses `current->theme->color` for consistent styling with the active theme
- **Accessibility**: Includes proper ARIA labels with translations
- **Configurable Behavior**: JavaScript configuration object allows customization without code changes
- **Smooth Scrolling**: Uses native smooth scroll behavior for better UX
- **Navbar Hiding**: Hides navbar on scroll down, shows on scroll up (with configurable thresholds)

---

## Acceptance Criteria (SDD)

### Functional
- [x] `component-init.ntpl` injects CSS into page head on every render
- [x] `component-init.ntpl` injects button and JavaScript at end of body
- [x] Back-to-top button uses theme color from `current->theme->color`
- [x] Button includes accessibility labels with translations
- [x] Scroll configuration exposed via `window.backToTopConfig`
- [x] Navbar hides on scroll down, shows on scroll up

### Technical
- [x] Route exposed at `/backtotop` (base route from manifest)
- [x] Static routes for CSS and JS assets
- [x] Static file serving with proper cache headers
- [x] No authentication required for asset access
- [x] CSP-compliant script and style injection

### Integration
- [x] Global injection affects all pages
- [x] Depends on theme component for color theming
- [x] Route paths derived from `manifest->route` BIF
- [x] SVG icon embedded in snippet (no external dependency)

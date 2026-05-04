# Component: moderndrawer_0yt2sa

## Executive Summary

Provides the main navigation sidebar (drawer) for the application layout. Designed to be highly responsive and persistent, allowing users to choose between three visual states (Full, Icons, or Hidden). **This component overrides the default drawer implementation from `template_0yt2sa`** by redefining the `current:template:main-drawer` and `current:template:main-drawer-button` snippets.

## Identity

- **UUID**: `moderndrawer_0yt2sa`
- **Base Route**: `` (no routes - provides global drawer snippets)
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
**Drawer override** component. Provides:
- Modern drawer implementation via `component-init.ntpl`
- Static assets (CSS/JS) via component routes
- State persistence via cookies and localStorage

### Override Mechanism

This component overrides the default drawer from `template_0yt2sa` by:
1. Redefining `current:template:main-drawer` - The main sidebar container
2. Redefining `current:template:main-drawer-button` - The toggle button (hamburger)
3. Redefining `current:template:main-drawer-items-icons-size` - Icon sizing

Since `cmp_0700_moderndrawer` loads after `cmp_0200_template` (prefix 0700 > 0200), its snippet definitions take precedence.

### Directory Structure

```
src/component/cmp_NNNN_moderndrawer/
├── manifest.json              # Identity and security
├── neutral/
│   └── component-init.ntpl    # Drawer snippets that override template_0yt2sa
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving routes
└── static/
    ├── css/moderndrawer.min.css   # Drawer styles
    └── js/moderndrawer.min.js     # Drawer interactivity
```

### Drawer States (Persistence Engine)

Uses cookies and `localStorage` to remember user preference:

| State | Description |
|-------|-------------|
| `Full` | Shows icons and descriptive text (default pinned state) |
| `Icons` | Minimized showing only icons (maximizes workspace) |
| `Hidden` | Completely hidden on desktop, off-canvas on mobile |

**Cookie:** `theme-drawer-state` stores the current state
**Cookie:** `theme-drawer-pin-full` stores the pinned state for Full mode

### Snippet Interface

**`current:template:main-drawer-button`** (line 17-21)
- Toggle button (hamburger) injected into the navbar
- Uses Bootstrap navbar-toggler-icon

**`current:template:main-drawer`** (line 31+)
- Main sidebar container including mobile overlay
- Includes tabs panel and content area
- Dynamic state class from `moderndrawer_0yt2sa:state`

**`moderndrawer_0yt2sa:state`** (line 13-15)
- Evaluates `theme-drawer-state` cookie at render time
- Returns appropriate CSS class for SSR (avoids FOUC)
- Falls back to `theme-drawer-state-hidden` if no cookie

**`current:template:main-drawer-items-icons-size`** (line 23-25)
- Returns `x-icon-20px` for drawer tab icons

### Static Assets and CSP Compliance

To avoid inline styles prohibited by CSP:
- **CSS**: Injected in `<head>` via `moderndrawer.min.css`
- **JS**: Injected at end of `<body>` via `moderndrawer.min.js`
- **CSS Variables**: `--theme-drawer-tabs-w` (74px) and `--theme-drawer-panel-w` (260px) for layout calculations

### Dependencies

- **Depends on**: `cmp_0200_template` (overrides its drawer snippets)
- **Used by**: All components (drawer appears on every page)
- **Weak coupling**: Communicates with PWA component via shared CSS classes (`pwa_0yt2sa-install-show`)

## Data and Models

### Drawer Configuration

Uses `current->drawer->name` for the drawer title displayed in the header.

### CSS Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `--theme-drawer-tabs-w` | 74px | Width of icon-only tabs column |
| `--theme-drawer-panel-w` | 260px | Width of full drawer panel |

## Disabling the Component

To revert to the default drawer from `template_0yt2sa`:
1. Rename directory to `_cmp_0700_moderndrawer` (add underscore prefix)
2. Restart the application
3. The default drawer implementation will be used

## Technical Rationale

- **State Detection**: Reading the cookie directly in NTPL (`moderndrawer_0yt2sa:state`) ensures the drawer appears in the correct state from the first HTML byte, improving perceived speed
- **SSR-Friendly**: No JavaScript required for initial state; state class applied server-side
- **Weak Coupling**: Uses CSS class sharing for component communication rather than direct dependencies
- **Override Pattern**: Demonstrates how to override core template snippets by loading later in component order

---

## Acceptance Criteria (SDD)

### Functional
- [x] `component-init.ntpl` defines `current:template:main-drawer` snippet
- [x] `component-init.ntpl` defines `current:template:main-drawer-button` snippet
- [x] Three states supported: Full, Icons, Hidden
- [x] State persistence via cookies (`theme-drawer-state`, `theme-drawer-pin-full`)
- [x] SSR state detection via `moderndrawer_0yt2sa:state` snippet
- [x] Tab-based navigation with icons and content areas

### Technical
- [x] No routes for UI (empty base route)
- [x] Static routes for CSS/JS assets via `route/routes.py`
- [x] CSP-compliant external CSS/JS (no inline styles)
- [x] CSS variables for layout dimensions
- [x] LocalStorage and cookie persistence

### Integration
- [x] Overrides `template_0yt2sa` drawer snippets (loads after with prefix 0700 > 0200)
- [x] Uses `current->drawer->name` for header title
- [x] Compatible with PWA component via CSS class sharing
- [x] Responsive design for mobile viewports (off-canvas behavior)

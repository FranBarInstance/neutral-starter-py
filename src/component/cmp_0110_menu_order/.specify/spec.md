# Component: menu_order_0yt2sa

## Executive Summary

Component that reserves menu key placeholders to control display order in navigation.
By defining empty menu keys in a specific sequence, later components can populate them
with actual menu items while maintaining the desired visual order.

## Identity

- **UUID**: `menu_order_0yt2sa`
- **Base Route**: `` (no routes)
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
**Pure configuration** component (no routes, no handlers, no templates).
Defines menu structure placeholders in `schema.json`.

### How It Works

The component defines empty menu keys (`{}`) in `schema.json`. These placeholders:
1. Reserve positions in the menu hierarchy
2. Are populated by later components with actual menu data
3. Control the display order through the merge mechanism

### Menu Structure Reserved

#### Navbar Menu (`data.navbar.menu`)

**Anonymous users (`session:`):**
- `signin` - Reserved for sign in link
- `signup` - Reserved for sign up link
- `theme` - Reserved for theme selector
- `color` - Reserved for color picker
- `language` - Reserved for language selector

**Authenticated users (`session:true`):**
- `signout` - Reserved for sign out link
- `theme` - Reserved for theme selector
- `color` - Reserved for color picker
- `language` - Reserved for language selector

#### Drawer Menu (`data.current.drawer.menu`)

**Both session states:**
- `main` - Reserved for main navigation tab
- `user` - Reserved for user-related tab
- `sign` - Reserved for sign in/out tab
- `rrss` - Reserved for social media tab
- `setting` - Reserved for settings tab
- `info` - Reserved for information tab

### Directory Structure

```
src/component/cmp_NNNN_menu_order/
├── manifest.json          # Identity and security
└── schema.json            # Menu structure placeholders
```

### Dependencies

- **Depends on**: `cmp_0100_default` (for base configuration)
- **Used by**: Components that provide actual menu items (e.g., `cmp_5000_user`, `cmp_5100_sign`, etc.)

## Data and Models

### Schema Structure

| Key | Purpose | Populated By |
|-----|---------|--------------|
| `data.navbar.menu.session:*` | Top bar for anonymous users | `cmp_5100_sign`, `cmp_0600_settheme`, etc. |
| `data.navbar.menu.session:true` | Top bar for authenticated users | `cmp_5100_sign`, `cmp_0600_settheme`, etc. |
| `data.current.drawer.menu.session:*` | Side drawer for anonymous users | Multiple components |
| `data.current.drawer.menu.session:true` | Side drawer for authenticated users | Multiple components |

## Acceptance Criteria (SDD)

### Functional
- [x] `schema.json` contains all required menu placeholders
- [x] Placeholder structure supports both session states (`session:` and `session:true`)
- [x] No component-specific data in placeholders (empty objects `{}`)
- [x] Menu order is defined by key declaration sequence in `schema.json`

### Technical
- [x] No routes, handlers, or templates
- [x] Loads after `cmp_0100_default` (prefix 0110 > 0100) to override base menu structure

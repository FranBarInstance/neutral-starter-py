# Component: menu_order_0yt2sa

Menu order reservation component.

## Overview

This component reserves empty menu placeholders to control the display order of navigation items. Later components populate these placeholders with actual menu content.

## Structure

- `manifest.json` - Component identity
- `schema.json` - Menu placeholder definitions

## Reserved Menu Keys

### Navbar (`data.navbar.menu`)
- `signin`, `signup`, `signout` - Authentication links
- `theme`, `color` - Theme selectors
- `language` - Language selector

### Drawer (`data.current.drawer.menu`)
- `main`, `user`, `sign`, `rrss`, `setting`, `info` - Navigation tabs

## How It Works

The component defines empty objects (`{}`) as placeholders. Components loaded later override these keys with actual menu data, maintaining the order defined here.

See [Overriding Components](../../../docs/override-components.md) for details.

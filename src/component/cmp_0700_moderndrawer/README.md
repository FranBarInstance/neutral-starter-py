# moderndrawer_0yt2sa (Modern Drawer)

This component provides the main navigation sidebar (drawer) for the application's layout. It is designed to be responsive, multi-state, and follows modern UI/UX patterns.

## Features

- **Multi-state**: Supports three states:
    - `Full`: Shows icons and text.
    - `Icons`: Minimized state showing only icons.
    - `Hidden`: Completely hidden on desktop, or off-canvas on mobile.
- **Tab-based Navigation**: Supports organizing navigation links into different categories/tabs.
- **Responsive Design**: Automatically adjusts its behavior for mobile viewports.
- **CSP Compliant**: Serves its CSS and JS from external files via component routes, avoiding inline styles and scripts.

## Static Assets

The component serves its own static files for performance and security:
- `CSS`: `/css/moderndrawer.min.css`
- `JS`: `/js/moderndrawer.min.js`

## Usage

This component registers snippets used by the base template to render the main drawer and its toggle button:
- `current:template:main-drawer-button`: Toggle button usually placed in the navbar.
- `current:template:main-drawer`: The main sidebar container.

## Implementation Notes

- Interactivity is handled via `moderndrawer.min.js` using `localStorage` and `cookie` to persist states.
- It uses a custom CSS variable `--theme-drawer-tabs-w` (=74px) and `--theme-drawer-panel-w` (=260px) for layout calculations.
- Layout persistence is maintained across page reloads and AJAX navigation.

## Overrides and Disabling

This component is designed to **override the default system drawer** implementation.

If you wish to revert to the previous drawer implementation, you can **deactivate** this component by renaming its directory and adding a leading underscore: 
`src/component/_cmp_0700_moderndrawer`

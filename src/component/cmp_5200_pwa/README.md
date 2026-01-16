# PWA Component

This component provides Progressive Web App (PWA) features to the **Neutral PWA** framework. It handles service worker registration, dynamic web app manifest generation, and provides a user-friendly installation prompt.

## Configuration

The component must be assigned to the root route (`""`) for the `service-worker.js` to function correctly. Other assets can be served from any path, which is defined in `manifest.json` via the `static-dir` property.

The component is highly configurable through its `manifest.json` (via overrides in `custom.json`):

*   **`enable`**: Globally toggle PWA features.
*   **`static-dir`**: Name of the directory for PWA assets (default: `pwa`).
*   **`theme_color`** & **`background_color`**: Colors used in the manifest and HTML meta tags.
*   **`navbar_times`**: Determines how many times the install prompt is suggested in the navigation bar.
*   **`public-has-*`**: Flags to indicate whether to use files from the project's root `public` directory instead of the component's internal `static` folder.

## Customization

To override settings in `manifest.json`, create a `custom.json` file in the component's root directory.

To add custom icons, simply place them in the `public/pwa` folder and change `public-has-icons` to `true` in the `custom.json` file. They will be processed and generated automatically.

Similarly, you can do the same for the service worker and the manifest by changing `public-has-service-worker` and `public-has-manifest` to `true` in the `custom.json` file:

```json
{
    "schema": {},
    "manifest": {
        "config": {
            "static-dir": "pwa",
            "enable": true,
            "navbar_times": 2,
            "theme_color": "#375A7F",
            "background_color": "#ffffff",
            "public-has-icons": false,
            "public-has-manifest": false,
            "public-has-service-worker": false,
            "public-has-offline": false
        }
    }
}
```

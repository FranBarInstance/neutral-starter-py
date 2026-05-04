# Home Component

Landing page for Neutral TS Starter Py.

## Overview

Provides the public home page at the root URL (`/`). Displays project branding, feature highlights, and call-to-action links.

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Home page with hero and features |

## Structure

```
├── manifest.json              # UUID: home_0yt2sa, route: ""
├── schema.json                # Menus and translations
├── route/
│   ├── __init__.py            # Blueprint init
│   └── routes.py              # Single route handler
└── neutral/
    └── route/
        ├── index-snippets.ntpl
        ├── data.json          # Page title, description, h1
        ├── locale-*.json      # 6 language translations
        └── root/
            └── content-snippets.ntpl  # Hero + feature cards
```

## Translations

6 languages: EN, ES, DE, FR, AR, ZH

Key strings: feature titles, descriptions, CTA buttons.

## Menu Integration

- **Main menu**: "Home" entry with `x-icon-home`
- **Drawer menu**: "Main" tab entry with `x-icon-home`

Available for both anonymous and authenticated users.

## Dependencies

- Core `RequestHandler`
- Base layout templates (provides theme variables)

## Notes

- No forms or AJAX — static content only
- External links to GitHub and documentation
- Theme-aware (uses `current->theme->color` for hero background)

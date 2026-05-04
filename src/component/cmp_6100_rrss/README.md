# RSS Reader Component

RSS feed aggregator displaying news from multiple external sources.

## Overview

Provides an RSS feed reader with AJAX-based feed switching, card-based entry layout, and configurable feed sources. Includes caching for performance and navigation integration.

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Main RSS reader page |
| `/ajax/<name>` | GET | No | AJAX feed load (requires header) |
| `/rss/<name>` | GET | No | Direct feed view |
| `/*` | GET | No | Catch-all |

## Structure

```
├── manifest.json              # UUID: rrss_0yt2sa, route: /rrss, feed URLs
├── schema.json                # Menu entries
├── route/
│   ├── __init__.py            # Blueprint init
│   ├── routes.py              # 5 route handlers
│   └── rrss_handler.py        # Custom request handler
├── neutral/
│   ├── component-init.ntpl    # Snippet inclusion
│   ├── obj/rss.json           # RSS object definition
│   └── route/
│       ├── index-snippets.ntpl
│       ├── snippets.ntpl      # Feed display snippets
│       ├── locale-*.json      # Translations (6 languages)
│       └── root/
│           ├── content-snippets.ntpl
│           ├── ajax/
│           │   └── content-snippets.ntpl
│           └── rss/
│               └── content-snippets.ntpl
├── src/
│   ├── feed.py                # RSS fetching/parsing
│   └── rss.py                 # RSS utilities
└── tests/
    └── test_routes.py
```

## Feed Sources

Configured in `manifest.json`:
- BBC, TechCrunch, Hackaday, CNET, NASA, TheRegister, ArsTechnica

**Default**: BBC
**Cache TTL**: 300 seconds (configurable)

## Key Snippets

- `rrss_0yt2sa-head` — CSS for feed images
- `rrss_0yt2sa-body-end` — External link & date formatting JS
- `rrss:urls-buttons` — Feed selector buttons
- `rrss:feed-entries` — Main feed display
- `rrss:play` — Cached feed renderer

## Translations

6 languages: EN, ES, DE, FR, AR, ZH

Key strings: "Source", "No publications", "RSS Error", "Alternate sources"

## Menu Integration

- **Navbar**: "RSS" entry with `x-icon-rss`
- **Drawer**: "RSS" tab with `x-icon-rss`

## Security

- AJAX endpoints require `Requested-With-Ajax` header
- External links use `target="_blank"` with `rel="noopener noreferrer"`
- CSP nonces on inline styles/scripts

## Notes

- Feed URLs configurable via `manifest.json` (no code changes needed)
- NTPL-level caching prevents repeated external fetches
- Client-side date localization from UTC to local timezone
- Graceful error handling for failed feed fetches

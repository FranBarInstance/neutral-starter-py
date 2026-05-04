# Info — `info_0yt2sa`

Skeleton informational pages: About, Contact, Help, and Legal. All pages share
a common placeholder layout and are publicly accessible.

## Overview

This component provides standard informational pages for the application. All four
pages render the same shared placeholder snippet (`info:sample-body-main-content`)
wrapped in a theme container. The content is intended to be replaced with real
information during project customization.

A single catch-all route delegates to `RequestHandler` for template resolution.

## Routes

| Route | Description |
|-------|-------------|
| `/info/about` | About page |
| `/info/contact` | Contact page |
| `/info/help` | Help page |
| `/info/legal` | Legal notice page |
| `/info/<path>` | Catch-all — returns 404 for unmatched subpaths |

## Structure

```
route/
├── __init__.py
└── routes.py              # Single catch-all: /info/<path:route>
neutral/route/
├── index-snippets.ntpl    # Locale loader + shared snippet include
├── snippets.ntpl          # Shared placeholder content
├── locale-{lang}.json     # Translations (en, es, fr, de, ar, zh)
└── root/
    ├── about/             # data.json + content-snippets.ntpl
    ├── contact/           # data.json + content-snippets.ntpl
    ├── help/              # data.json + content-snippets.ntpl
    └── legal/             # data.json + content-snippets.ntpl
```

## Menus

**Session menu** (anonymous + authenticated): About, Help, Contact, Legal entries
linking to `/info/<page>`.

**Drawer menu** (anonymous + authenticated): Single "Information" entry.

## Translations

6 languages: EN, ES, FR, DE, AR, ZH. Locale files include page titles and
descriptions for all subroutes.

## Dependencies

- `RequestHandler` core — route rendering
- `http_errors` (`http_errors_0yt2sa`) — 404 rendering for unmatched subroutes

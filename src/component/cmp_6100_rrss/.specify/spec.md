# Component: rrss_0yt2sa

## Executive Summary

RSS feed reader component providing news aggregation from multiple external RSS sources. Displays feed entries in a card-based layout with asynchronous feed switching via AJAX. Includes caching for performance, configurable feed sources via manifest, and navigation integration for easy access. Supports both static and AJAX-based feed loading patterns.

## Identity

- **UUID**: `rrss_0yt2sa`
- **Base Route**: `/rrss`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes are publicly accessible
- AJAX endpoints require `Requested-With-Ajax` header (anti-CSRF via `@require_header_set`)
- External links use `target="_blank"` with `rel="noopener noreferrer"`
- No user data exposure — only external RSS feed content

## Architecture

### Component Type
**Feature** component. Provides:
- RSS feed aggregation and display
- Configurable multiple feed sources
- Cached feed fetching with configurable TTL
- AJAX-based feed switching without page reload
- Card-based entry layout with images, summaries, and metadata
- Navigation menu integration (navbar and drawer)
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_NNNN_rrss/
├── manifest.json                          # Identity, security, feed URLs
├── schema.json                            # Menu integration
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions (5 handlers)
│   └── rrss_handler.py                    # Custom request handler
├── neutral/
│   ├── component-init.ntpl              # Snippet inclusion
│   ├── obj/
│   │   └── rss.json                       # RSS object definition
│   └── route/
│       ├── index-snippets.ntpl            # Auto-loaded snippets
│       ├── snippets.ntpl                  # RSS feed display snippets
│       ├── locale-*.json                  # Translations (6 languages)
│       └── root/
│           ├── content-snippets.ntpl      # Root page content
│           ├── ajax/
│           │   └── content-snippets.ntpl  # AJAX feed response
│           └── rss/
│               └── content-snippets.ntpl  # Direct feed view
├── src/
│   ├── feed.py                            # RSS feed fetching/parsing
│   └── rss.py                             # RSS utility functions
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Auth | Purpose |
|-------|--------|---------|------|---------|
| `/` | GET | `rrss()` | No | Main RSS reader page |
| `/ajax` | GET | `rrss_ajax()` | No | 404 placeholder |
| `/ajax/<rrss_name>` | GET | `rrss_ajax_name()` | No | AJAX feed load (requires header) |
| `/rss/<rrss_name>` | GET | `rrss_rss_name()` | No | Direct feed view |
| `/<path:route>` | GET | `rrss_catch_all()` | No | Catch-all |

### Route Handlers

**`rrss()`**
- Renders main RSS reader page
- Uses `RrssRequestHandler` with default feed selection

**`rrss_ajax_name(rrss_name)`**
- Requires `Requested-With-Ajax` header
- Validates feed name against allowed list
- Returns AJAX-rendered feed content
- Uses caching via NTPL `{:cache; ... :}` directive

**`rrss_rss_name(rrss_name)`**
- Direct feed view (non-AJAX)
- Full page render of specific feed

### Feed Sources (from `manifest.json`)

| Feed Name | Source |
|-----------|--------|
| BBC | BBC News |
| TechCrunch | TechCrunch |
| Hackaday | Hackaday |
| CNET | CNET News |
| NASA | NASA Breaking News |
| TheRegister | The Register |
| ArsTechnica | Ars Technica |

**Default feed**: BBC
**Cache TTL**: 300 seconds (configurable via `manifest.json`)

### NTPL Snippets (`neutral/route/snippets.ntpl`)

| Snippet | Purpose |
|---------|---------|
| `rrss_0yt2sa-head` | CSS styling for RSS feed images |
| `rrss_0yt2sa-body-end` | JavaScript for external links and date formatting |
| `rrss:urls-buttons` | Feed selector buttons (static links) |
| `rrss:urls-buttons-next` | Feed selector buttons (AJAX fetch) |
| `rrss:feed-entries` | Main feed display with error handling |
| `rrss:feed-entries-entries` | Individual entry cards grid |
| `rrss:play` | Main play snippet (caches feed entries) |
| `rrss:play-ajax` | AJAX loading with spinner |
| `rrss:play-static` | Static cached feed display |

**Features:**
- External link safety (auto-adds `target="_blank"` and `rel="noopener noreferrer"`)
- Date localization (UTC to local timezone conversion)
- Image width constraints (180px max)
- Entry cards with title, summary, tags, source link, and publish date
- Fallback for missing publications
- Error display on feed fetch failure

### Feed Parsing (`src/feed.py`, `src/rss.py`)

**`feed.py`:**
- Fetches RSS XML from external URLs
- Parses RSS feed into structured data
- Extracts: title, link, published date, summary/description, tags
- Error handling for failed fetches

**`rss.py`:**
- RSS utility functions and constants

### Cache Strategy

NTPL-level caching via `{:cache; <seconds>/rrss_0yt2sa-feed-entries-<name>/1/ :}`:
- Cache key includes feed name
- Configurable TTL via `manifest.json` (`cache_seconds`)
- Prevents repeated external fetches

### Dependencies

- **Depends on**: Core `RequestHandler`, `RrssRequestHandler` (custom), feed parsing modules
- **Used by**: End users accessing news feeds

## Data and Models

### Schema Data (`schema.json`)

Menu integration for authenticated users:

**Navbar menu:**
| Entry | Text | Link | Icon |
|-------|------|------|------|
| rrss | RSS | `<manifest.route>` | `x-icon-rss` |

**Drawer menu:**
| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| rrss | RSS | rrss | `x-icon-rss` |

### Translations (`neutral/route/locale-*.json`)

6 languages (EN, ES, DE, FR, AR, ZH):

| Key | EN |
|-----|----|
| Alternate sources | Alternate sources |
| Source | Source |
| No publications | No publications |
| RSS Error | RSS Error |
| RSS | RSS |
| news | news |
| RSS news in | RSS news in |

## Technical Rationale

- **AJAX-first design**: Feed switching without page reload via `{:fetch; ... :}`
- **Configurable sources**: Feed URLs defined in `manifest.json` — add/remove without code changes
- **Caching layer**: NTPL caching reduces external requests and improves performance
- **External link safety**: JavaScript automatically adds security attributes to external links
- **Date localization**: Client-side UTC to local timezone conversion for better UX
- **CSP compliance**: Inline scripts use `{:;CSP_NONCE:}` placeholder
- **Graceful degradation**: Error handling for failed feed fetches with user-friendly messages

## Known Limitations

- External RSS feeds may be unavailable or change format
- No server-side caching fallback if NTPL cache fails
- Image sizes may vary by feed source
- No feed filtering or search functionality

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/` displays main RSS reader page with default feed
- [x] `/ajax/<name>` returns AJAX feed content (requires header)
- [x] `/rss/<name>` displays specific feed as full page
- [x] Feed switching works without page reload via AJAX
- [x] Entry cards display title, summary, tags, source, date
- [x] External links open in new tab with security attributes
- [x] Error message displayed when feed fetch fails
- [x] All configured feeds accessible via buttons

### Technical
- [x] All routes public (no auth required)
- [x] AJAX endpoints require `Requested-With-Ajax` header
- [x] Feed content cached with configurable TTL
- [x] CSP nonces on inline styles and scripts
- [x] Client-side date localization
- [x] Image width constraints via CSS

### Integration
- [x] Navbar menu entry with RSS icon
- [x] Drawer menu entry with RSS icon
- [x] 6-language translation support
- [x] Translations include feed-specific strings

### Configuration
- [x] Feed URLs configured in `manifest.json`
- [x] Default feed specified in manifest
- [x] Cache TTL configurable via `cache_seconds`
- [x] Adding new feeds requires only manifest update

---

*Last updated: 2026-05-04*

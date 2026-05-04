# Component: cryptojs_0yt2sa

## Executive Summary

Provides the crypto-js library for client-side cryptographic operations. Serves the minified library via a dedicated route and automatically injects the script into every page through global snippet injection.

## Identity

- **UUID**: `cryptojs_0yt2sa`
- **Base Route**: `/crypto-js`
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
**Library provider** component. Provides:
- Static route serving crypto-js library
- Global script injection via `component-init.ntpl`

### Directory Structure

```
src/component/cmp_NNNN_crypto-js/
├── manifest.json              # Identity and security
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving route
└── neutral/
    └── component-init.ntpl    # Global script injection snippet
```

### Route (`route/routes.py`)

**`/crypto-js.min.js`** (GET)
- Serves `crypto-js.min.js` from component's `static/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

### Global Script Injection (`neutral/component-init.ntpl`)

Automatically injects crypto-js script into every page:

```ntpl
{:moveto; /head >>
    <script nonce="{:;CSP_NONCE:}" src="{:;cryptojs_0yt2sa->manifest->route:}/crypto-js.min.js"></script>
:}
```

**CSP Compliance:** Uses `{:;CSP_NONCE:}` placeholder for nonce attribute.

### Dependencies

- **No dependencies**: Self-contained library component
- **Used by**: Any component needing client-side cryptography (e.g., user authentication forms)

## Data and Models

No schema data. This component is a pure library provider.

## Technical Rationale

- **Global Availability**: By injecting via `component-init.ntpl`, crypto-js is available on every page without manual inclusion
- **CDN Alternative**: Self-hosted library avoids external CDN dependencies
- **CSP Compliant**: Uses nonce placeholder for inline script tag
- **Cache Control**: Proper HTTP cache headers for static asset

---

## Acceptance Criteria (SDD)

### Functional
- [x] `route/routes.py` serves `crypto-js.min.js` at `/crypto-js/crypto-js.min.js`
- [x] `component-init.ntpl` injects script into page head on every render
- [x] Script loads with CSP nonce placeholder

### Technical
- [x] Route exposed at `/crypto-js` (base route from manifest)
- [x] Static file serving with proper cache headers
- [x] No authentication required for library access
- [x] CSP-compliant script injection

### Integration
- [x] Global script injection affects all pages
- [x] Library accessible via `CryptoJS` global object in browser
- [x] Route path derived from `manifest->route` BIF

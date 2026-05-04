# Component: marked_0yt2sa

## Executive Summary

Provides the marked library for client-side Markdown parsing and rendering. Serves the ESM bundle via a dedicated route and automatically injects the module import into every page through global snippet injection.

## Identity

- **UUID**: `marked_0yt2sa`
- **Base Route**: `/marked`
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
- Static route serving marked ESM bundle
- Global module injection via `component-init.ntpl`

### Directory Structure

```
src/component/cmp_NNNN_marked/
├── manifest.json              # Identity and security
├── route/
│   ├── __init__.py            # Blueprint initialization
│   └── routes.py              # Static file serving route
└── neutral/
    └── component-init.ntpl    # Global module injection snippet
```

### Route (`route/routes.py`)

**`/marked.esm.js`** (GET)
- Serves `marked.esm.js` from component's `static/` directory
- Returns with `Config.STATIC_CACHE_CONTROL` headers
- Public access (no authentication required)

### Global Module Injection (`neutral/component-init.ntpl`)

Automatically injects marked import into every page:

```ntpl
{:moveto; /body >>
    <script nonce="{:;CSP_NONCE:}" type="module">
        import { marked } from '{:;marked_0yt2sa->manifest->route:}/marked.esm.js';
        window.marked = marked;
    </script>
:}
```

**Key differences from crypto-js:**
- Uses ES Module (`type="module"`) instead of global script
- Imports the `marked` named export
- Assigns to `window.marked` for global access
- Injected at end of body instead of head

**CSP Compliance:** Uses `{:;CSP_NONCE:}` placeholder for nonce attribute.

### Dependencies

- **No dependencies**: Self-contained library component
- **Used by**: Any component needing client-side Markdown rendering

## Data and Models

No schema data. This component is a pure library provider.

## Technical Rationale

- **ESM Approach**: Uses ES Modules for modern JavaScript import syntax
- **Global Assignment**: Assigns to `window.marked` for compatibility with non-module code
- **Body Injection**: Scripts that modify the DOM are better placed at end of body
- **Self-hosted**: Avoids external CDN dependencies
- **CSP Compliant**: Uses nonce placeholder for inline script

---

## Acceptance Criteria (SDD)

### Functional
- [x] `route/routes.py` serves `marked.esm.js` at `/marked/marked.esm.js`
- [x] `component-init.ntpl` injects ES module import on every render
- [x] Module import assigns `marked` to `window.marked` global
- [x] Script uses CSP nonce placeholder

### Technical
- [x] Route exposed at `/marked` (base route from manifest)
- [x] Static file serving with proper cache headers
- [x] No authentication required for library access
- [x] CSP-compliant module script injection
- [x] Uses `type="module"` for ES Module support

### Integration
- [x] Global module injection affects all pages
- [x] Library accessible via `window.marked` or `marked` global in browser
- [x] Route path derived from `manifest->route` BIF
- [x] ESM format compatible with modern bundlers

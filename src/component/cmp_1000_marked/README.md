# Component: marked_0yt2sa

Marked.js library provider for Markdown parsing.

## Overview

This component provides the marked library for client-side Markdown parsing and rendering. It serves the ESM bundle via a dedicated route and automatically injects the module import into every page.

## Structure

- `manifest.json` - Component identity and security
- `route/routes.py` - Static file serving route
- `neutral/component-init.ntpl` - Global module injection

## Route

**`/marked/marked.esm.js`** (GET)
- Serves the marked ESM bundle from static directory
- Public access, no authentication required
- Returns with proper cache headers

## Global Module Injection

The `component-init.ntpl` automatically injects:

```html
<script nonce="{CSP_NONCE}" type="module">
    import { marked } from '/marked/marked.esm.js';
    window.marked = marked;
</script>
```

At the end of the `<body>` of every page. CSP-compliant with nonce placeholder.

**Key differences from crypto-js:**
- Uses ES Module (`type="module"`) instead of global script
- Imports the `marked` named export
- Injected at end of body instead of head

## Usage

The library is automatically available on every page via the global `marked` object:

```javascript
// Example: Parse markdown to HTML
const html = marked.parse("# Hello World");
```

## Dependencies

- **None**: Self-contained library
- **Used by**: Components needing client-side Markdown rendering

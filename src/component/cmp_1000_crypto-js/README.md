# Component: cryptojs_0yt2sa

Crypto-js library provider.

## Overview

This component provides the crypto-js library for client-side cryptographic operations. It serves the minified library via a dedicated route and automatically injects the script into every page through global snippet injection.

## Structure

- `manifest.json` - Component identity and security
- `route/routes.py` - Static file serving route
- `neutral/component-init.ntpl` - Global script injection

## Route

**`/crypto-js/crypto-js.min.js`** (GET)
- Serves the crypto-js library from static directory
- Public access, no authentication required
- Returns with proper cache headers

## Global Script Injection

The `component-init.ntpl` automatically injects:

```html
<script nonce="{CSP_NONCE}" src="/crypto-js/crypto-js.min.js"></script>
```

Into the `<head>` of every page. CSP-compliant with nonce placeholder.

## Usage

The library is automatically available on every page via the global `CryptoJS` object:

```javascript
// Example: SHA256 hashing
const hash = CryptoJS.SHA256("message").toString();
```

## Dependencies

- **None**: Self-contained library
- **Used by**: Components needing client-side cryptography (e.g., authentication forms)

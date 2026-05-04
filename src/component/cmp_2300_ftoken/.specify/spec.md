# Component: ftoken_0yt2sa

## Executive Summary

CSRF protection for forms via time-limited signed tokens. Provides both backend token generation/validation and frontend snippet injection for automatic form field management.

## Identity

- **UUID**: `ftoken_0yt2sa`
- **Base Route**: `/ftoken`
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
**Security** component. Provides:
- Backend token generation and validation (Python library)
- Frontend snippet injection (NTPL)
- Static JS file serving
- AJAX endpoint for token fetching

### Directory Structure

```
src/component/cmp_NNNN_ftoken/
├── manifest.json              # Identity and security
├── __init__.py                # Library registration
├── lib/
│   └── ftoken_0yt2sa/
│       ├── __init__.py        # Module init
│       └── ftoken.py          # Token generation/validation
├── route/
│   ├── __init__.py            # Blueprint initialization
│   ├── ftoken_handler.py      # Request handler
│   └── routes.py              # Routes definition
├── neutral/
│   ├── component-init.ntpl    # Global JS injection
│   └── snippets.ntpl          # Token field snippets
├── schema.json                # Error translations
├── static/
│   └── ftoken.min.js          # Client-side token handling
└── tests/                     # Component tests
```

### Library (`lib/ftoken_0yt2sa/ftoken.py`)

**`ftoken_create(key, fetch_id, form_id, user_token) -> dict`**
- Generates a new signed token with HMAC-SHA256
- Token name format: `ftoken.{expire_timestamp}`
- Returns dict with `name`, `value`, `fetch_id`, `form_id`
- Uses `Config.FTOKEN_EXPIRES_SECONDS` and `Config.SECRET_KEY`

**`ftoken_check(field_key_name, data, user_token) -> bool`**
- Validates submitted token against expiration and signature
- Extracts token from fields starting with `ftoken.`
- Returns `True` if valid and not expired, `False` otherwise

### Routes (`route/routes.py`)

**`GET /ftoken/<key>/<fetch_id>/<form_id>`**
- Requires `Requested-With-Ajax` header
- Generates new token via `FtokenRequestHandler`
- Returns rendered token field HTML

**`GET /ftoken/ftoken.min.js`**
- Serves static JS file with cache headers
- Public access

### Request Handler (`route/ftoken_handler.py`)

`FtokenRequestHandler` extends `RequestHandler`:
- `ftoken(key, fetch_id, form_id)`: Calls `ftoken_create()` and stores result in `schema_data['ftoken']`

### Snippets (`neutral/snippets.ntpl`)

**`ftoken:form-field`**
- Main snippet that intelligently handles AJAX loading or error states
- If `ftoken->name` exists and request is AJAX: renders field snippet
- If `ftoken->name` exists but not AJAX: renders error snippet
- If no `ftoken->name`: renders field snippet (for initial load)

**`ftoken:form-field-field`**
- Renders hidden input with token name and value
- Uses `data-url="/ftoken"` for AJAX fetching

**`ftoken:form-field-error`**
- Renders error alert with translated message
- Uses `ref:ftoken:error` translation key

### Global Script Injection (`neutral/component-init.ntpl`)

Injects at end of body:
- Config constant: `FTOKEN_EXPIRES_SECONDS`
- Script tag loading `ftoken.min.js`

### Dependencies

- **Depends on**: None (self-contained security component)
- **Used by**: Any component with forms (user, contact, etc.)

## Data and Models

### Error Translations (`inherit.locale.trans`)

Provides error message in 6 languages:

| Language | Translation |
|----------|-------------|
| EN | "TOKEN ERROR: please reload the page." |
| ES | "ERROR DE TOKEN: por favor recargue la página." |
| DE | "TOKEN FEHLER: bitte laden Sie die Seite neu." |
| FR | "ERREUR DE TOKEN: veuillez recharger la page." |
| AR | "خطأ في الرمز: يرجى إعادة تحميل الصفحة." |
| ZH | "令牌错误：请重新加载页面。" |

**Reference key:** `ref:ftoken:error`

## Configuration

| Config Key | Purpose |
|------------|---------|
| `Config.FTOKEN_EXPIRES_SECONDS` | Token lifetime in seconds |
| `Config.SECRET_KEY` | Key for HMAC signing |

## Technical Rationale

- **Time-limited**: Tokens expire after `FTOKEN_EXPIRES_SECONDS`
- **Session-bound**: Tokens tied to user's UTOKEN
- **HMAC-signed**: SHA256 HMAC prevents tampering
- **AJAX fetchable**: Tokens can be refreshed without page reload
- **No robot integration**: Checkbox interaction can trigger token update
- **CSP compliant**: Script injection uses nonce placeholder

---

## Acceptance Criteria (SDD)

### Functional
- [x] `ftoken_create()` generates time-limited HMAC-signed tokens
- [x] `ftoken_check()` validates tokens against expiration and signature
- [x] `ftoken:form-field` snippet injects hidden token fields
- [x] Snippet handles AJAX vs non-AJAX rendering paths
- [x] Error message displayed when token generation fails
- [x] Translations provided for error message in 6 languages

### Technical
- [x] Route at `/ftoken/<key>/<fetch_id>/<form_id>` requires AJAX header
- [x] Route at `/ftoken/ftoken.min.js` serves static JS
- [x] Library importable via `from ftoken_0yt2sa import ftoken_create, ftoken_check`
- [x] Uses `Config.FTOKEN_EXPIRES_SECONDS` and `Config.SECRET_KEY`
- [x] `FtokenRequestHandler` properly extends `RequestHandler`

### Integration
- [x] Global script injection loads `ftoken.min.js` on all pages
- [x] Config constant `FTOKEN_EXPIRES_SECONDS` exposed to client
- [x] Compatible with form components via snippet usage
- [x] No authentication required for token generation (bound to UTOKEN)

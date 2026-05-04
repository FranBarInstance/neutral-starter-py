# Component: localdev_0yt2sa

## Executive Summary

Development-only local administration component providing isolated session management and component configuration overrides. Features IP-restricted access, custom role-based authentication ("localdev"), and a web interface for managing component custom overrides in `config.db`. Designed for local development environments to test component configurations without modifying source files.

## Identity

- **UUID**: `localdev_0yt2sa`
- **Base Route**: `/local-dev`
- **Version**: `1.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["localdev"],
  "/login": ["*"]
}

**Critical security properties:**
- **IP-based access control**: Only configured local IPs allowed (via `ALLOWED_DEV_IPS` in config)
- **Role-based authorization**: "localdev" role required for all routes except login
- **CSRF protection**: All POST actions require valid CSRF token
- **Rate limiting**: Login attempts are rate-limited per IP
- **No caching**: All responses include strict no-cache headers
- **Session isolation**: Uses separate `SessionDev` session management distinct from main app auth
- **Credentials via environment**: `DEV_ADMIN_USER` and `DEV_ADMIN_PASSWORD` from `.env`

## Architecture

### Component Type
**Development/Admin** component. Provides:
- Local development admin panel
- Component custom override management (save/delete)
- Isolated session/login system
- IP-restricted access
- Custom role assignment ("localdev")

### Directory Structure

```
src/component/cmp_NNNN_localdev/
├── manifest.json                          # Identity, security, config keys
├── schema.json                            # Empty menu (no public menu entries)
├── __init__.py                            # Component initialization (SessionDev setup)
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions
│   └── localdev_request_handler.py        # Custom request handler
├── neutral/
│   ├── component-init.ntpl              # Snippet inclusion
│   ├── snippets.ntpl                      # Admin panel snippets
│   └── route/
│       ├── login/
│       │   └── content-snippets.ntpl      # Login page
│       ├── login/ajax/
│       │   └── content-snippets.ntpl      # AJAX login form
│       ├── logout/ajax/
│       │   └── content-snippets.ntpl      # Logout handler
│       ├── custom/
│       │   └── content-snippets.ntpl      # Override management UI
│       └── root/
│           └── content-snippets.ntpl      # Admin dashboard
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Public | Purpose |
|-------|--------|---------|--------|---------|
| `/` | GET | `LocalDevRequestHandler` | No | Admin dashboard |
| `/login` | GET/POST | `LocalDevRequestHandler` | Yes | Login page |
| `/login/ajax` | GET/POST | `LocalDevRequestHandler` | Yes | AJAX login |
| `/logout/ajax` | GET/POST | `LocalDevRequestHandler` | Yes | AJAX logout |
| `/custom` | GET/POST | `LocalDevRequestHandler` | No | Override management |

### Request Handler (`localdev_request_handler.py`)

**`LocalDevRequestHandler`** extends `RequestHandler`:

**Public Routes:**
- `""` (root) — requires auth
- `"login"`, `"login/ajax"` — public
- `"logout/ajax"` — public

**Security Checks:**
1. IP whitelist validation (`SessionDev.check_ip_allowed()`)
2. Session validation for non-public routes
3. CSRF token validation for POST actions

**Login Flow:**
1. Accepts `username` and `password` from form
2. Validates length (username ≤128, password ≤256)
3. Checks rate limiting per IP
4. Validates against `DEV_ADMIN_USER`/`DEV_ADMIN_PASSWORD`
5. Creates session cookies on success
6. Assigns "localdev" role to session

**Logout Flow:**
1. Deletes session via `SessionDev.delete_session()`
2. Clears cookies

**Custom Override Management (`/custom`):**
- **GET**: Lists all component custom overrides
- **POST save**: Saves override JSON for component UUID
  - Validates UUID format
  - Validates component exists in loaded components
  - Saves to `config.db` via `upsert_component_custom_override()`
- **POST delete**: Removes override for component UUID
  - Validates UUID format
  - Deletes via `delete_component_custom_override()`

### Session Management (`SessionDev`)

Uses custom `SessionDev` class from `core.session_dev`:
- Separate from main application session
- Cookie-based session tracking
- IP-based access control
- Rate limiting for login attempts
- Environment-based credentials

### Configuration Used

| Config Key | Purpose |
|------------|---------|
| `Config.ALLOWED_DEV_IPS` | Comma-separated allowed IPs |
| `Config.DEV_ADMIN_USER` | Admin username (from `.env`) |
| `Config.DEV_ADMIN_PASSWORD` | Admin password (from `.env`) |
| `Config.CONFIG_DB_PATH` | Path to `config.db` for overrides |

### Dependencies

- **Depends on**: `SessionDev` (custom session), `config.db` functions (CRUD for overrides), Flask session, `RequestHandler`
- **Used by**: Developers for local component configuration testing

## Data and Models

### Schema Data Publication

No menu entries published (development-only component, not for end users).

### Override Data Structure

Component custom overrides stored in `config.db`:

```json
{
    "manifest": { /* manifest overrides */ },
    "schema": { /* schema overrides */ }
}
```

Managed via admin UI with:
- Component UUID selector
- JSON editor for override content
- Enabled/disabled toggle

## Technical Rationale

- **Isolated session**: Separate `SessionDev` prevents conflicts with main app authentication
- **IP restriction**: Limits access to development machines only
- **Environment credentials**: No hardcoded passwords — configured via `.env`
- **Component UUID validation**: Prevents typos in override targets
- **CSRF protection**: Even local development needs CSRF protection
- **No caching headers**: Ensures fresh data during development
- **Rate limiting**: Prevents brute-force on local dev login

## Known Limitations

- Only works with `config.db` SQLite backend
- Requires manual `.env` configuration
- No LDAP or external auth integration
- UI is basic (development-focused, not production-ready)
- No audit logging

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/` displays admin dashboard (requires "localdev" role)
- [x] `/login` allows authentication with `DEV_ADMIN_USER`/`DEV_ADMIN_PASSWORD`
- [x] `/login/ajax` supports AJAX login
- [x] `/logout/ajax` clears session
- [x] `/custom` lists component custom overrides
- [x] `/custom` allows saving override JSON for component UUID
- [x] `/custom` allows deleting overrides
- [x] UUID validation on save/delete operations

### Security
- [x] IP-based access control enforced
- [x] "localdev" role required for non-public routes
- [x] CSRF token validation on all POST actions
- [x] Rate limiting on login attempts
- [x] No caching headers on all responses
- [x] Credentials from environment variables only

### Technical
- [x] Uses `SessionDev` for isolated session management
- [x] Validates component UUID exists before override
- [x] Validates UUID format (length, allowed chars)
- [x] Override JSON must be valid object (not array/primitive)
- [x] Schema data includes `local_admin` and `localdev_role`

### Configuration
- [x] `ALLOWED_DEV_IPS` configures IP whitelist
- [x] `DEV_ADMIN_USER` sets admin username
- [x] `DEV_ADMIN_PASSWORD` sets admin password
- [x] `CONFIG_DB_PATH` points to config database

---

*Last updated: 2026-05-04*

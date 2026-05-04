# Local Admin Component

Development-only local administration panel for managing component custom overrides.

## Overview

Provides IP-restricted access to component configuration management via `config.db`. Uses isolated session management (`SessionDev`) with custom "localdev" role authentication. Designed for local development environments to test component configurations without modifying source files.

## Routes

| Route | Method | Public | Description |
|-------|--------|--------|-------------|
| `/` | GET | No | Admin dashboard (requires "localdev" role) |
| `/login` | GET/POST | Yes | Login page |
| `/login/ajax` | GET/POST | Yes | AJAX login |
| `/logout/ajax` | GET/POST | Yes | Logout handler |
| `/custom` | GET/POST | No | Component override management |

## Structure

```
├── manifest.json              # UUID: localdev_0yt2sa, route: /local-dev
├── schema.json                # Empty (no public menu)
├── __init__.py                # Component init (SessionDev)
├── route/
│   ├── __init__.py            # Blueprint init
│   ├── routes.py              # Route definitions
│   └── localdev_request_handler.py  # Custom handler
├── neutral/
│   ├── component-init.ntpl    # Snippet inclusion
│   ├── snippets.ntpl          # Admin panel snippets
│   └── route/
│       ├── login/             # Login page
│       ├── login/ajax/        # AJAX login
│       ├── logout/ajax/       # Logout
│       ├── custom/            # Override UI
│       └── root/              # Dashboard
└── tests/
    └── test_routes.py
```

## Configuration

Required in `config/.env`:

| Variable | Purpose |
|----------|---------|
| `DEV_ADMIN_USER` | Admin username |
| `DEV_ADMIN_PASSWORD` | Admin password |
| `ALLOWED_DEV_IPS` | Comma-separated allowed IPs (e.g., `127.0.0.1,192.168.1.100`) |

## Custom Override Management

Via `/custom` route:

- **List**: View all component custom overrides in `config.db`
- **Save**: Add/update override JSON for a component UUID
  - Validates UUID format and existence
  - JSON must be an object (not array/primitive)
  - Toggle enabled/disabled
- **Delete**: Remove override for a component UUID

Override structure:
```json
{
    "manifest": { /* manifest overrides */ },
    "schema": { /* schema overrides */ }
}
```

## Security

- **IP whitelist**: Only configured IPs can access
- **Role-based**: "localdev" role required for all routes except login
- **CSRF protection**: All POST actions require valid token
- **Rate limiting**: Login attempts limited per IP
- **Session isolation**: Separate `SessionDev` (not main app session)
- **No caching**: Strict no-cache headers on all responses
- **Credentials via env**: No hardcoded passwords

## Notes

- Development-only — not for production use
- Requires `config.db` SQLite backend
- UI is basic (functionality-focused)
- No LDAP/external auth integration

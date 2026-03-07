# Dev Admin Session Management

The `SessionDev` class (`src/core/session_dev.py`) provides a specialized, lightweight, stateless session manager intended exclusively for local administration tools.

Unlike the standard `Session` module, `SessionDev` **does not use a database**. It relies entirely on cryptographically signed tokens (similar to JWTs) and environmental configuration.

## Overview

The `SessionDev` module provides isolated authentication that operates parallel to standard user sessions. It features:
- **Stateless Tokens**: Auth state is maintained through a hashed, authenticated cookie (`DEV_ADMIN_SESSION`) signed with the application's `SECRET_KEY`.
- **Environment-Based Credentials**: Validates against hardcoded user and password pairs set in the `config/.env` file.
- **Special Runtime Role**: Grants the special `localdev` runtime role used by `cmp_8100_localdev`, without storing that role in the database.
- **IP Allowlisting**: Ensures that only requests originating from predefined IP addresses or subnets can authenticate.
- **Built-in Rate Limiting**: Tracks login attempts in-memory to prevent brute force attacks against the administration panel.

## Key Features

### 1. Stateless Security
Instead of querying a database, `SessionDev` creates a base64 encoded payload containing:
- Issue and Expiration timestamps
- Client IP hash
- A random nonce

This payload is signed using HMAC-SHA256 with the app's `SECRET_KEY` and a salt (`::dev-admin`). Any tampering with the cookie immediately invalidates it. When the cookie is read, `SessionDev` verifies the signature and validates that the current IP matches the IP hash stored in the cookie.

### 2. IP Address Validation (`_is_allowed_ip`)
Every request is checked against `DEV_ADMIN_ALLOWED_IPS` from the configuration. This list natively supports both specific IP strings and CIDR network blocks (e.g., `192.168.0.0/16`). By default, it is configured to allow loopback addresses and common local network blocks.

### 3. Rate Limiting (`_login_rate_limited`)
A lightweight, in-memory dictionary tracks failed login timestamps per IP address. If an IP exceeds `_LOGIN_MAX_ATTEMPTS` (7 attempts) within `_LOGIN_WINDOW_SECONDS` (5 minutes), the module temporarily blocks further attempts.

## Configuration

Configuration is managed via `config/.env` utilizing the following keys:

- `DEV_ADMIN_USER`: The username for the local administration.
- `DEV_ADMIN_PASSWORD`: The password for the local administration.
- `DEV_ADMIN_ALLOWED_IPS`: Comma-separated list of allowed IPs/CIDRs.
- `DEV_ADMIN_AUTH_COOKIE_KEY`: Name of the authentication cookie (default: `"DEV_ADMIN_SESSION"`).
- `DEV_ADMIN_ROLE_COOKIE_KEY`: Name of the role flag cookie (default: `"dev_admin_role"`).
- `DEV_ADMIN_CSRF_SESSION_KEY`: The Flask session key where the CSRF token is stored (default: `"DEV_ADMIN_CSRF"`).

> **Important**: If `DEV_ADMIN_USER` or `DEV_ADMIN_PASSWORD` are not configured in `.env`, `SessionDev.are_credentials_ready()` returns `False`, and related dev tools should block login attempts.

## Code Example

```python
from core.session_dev import SessionDev

session_dev = SessionDev()

# 1. Check if the current environment allows access
if not session_dev.check_ip_allowed() or not session_dev.are_credentials_ready():
    abort(403)

# 2. Check if the user is already authenticated
is_auth = session_dev.check_session()

if not is_auth:
    # 3. Validate credentials and login
    if session_dev.validate_credentials("admin", "secret"):
        # Returns a dict of configured cookies to attach to the Flask Response
        cookie_updates = session_dev.create_session()
```

## Integration with Components
`SessionDev` is designed to be agnostic to the components that consume it. Components such as `cmp_8100_localdev` instantiate `SessionDev`, check `check_session()`, and use `create_session()` / `delete_session()` to retrieve the necessary cookie updates which they then apply to the `flask.Response`. At request bootstrap time, a valid `SessionDev` session grants the special runtime role `localdev`.

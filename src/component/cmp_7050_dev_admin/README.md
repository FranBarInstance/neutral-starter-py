# Dev Admin Component (`devadmin_0yt2sa`)

> WARNING: For production environments, it is strongly recommended to disable this component.
> Keep it enabled only in controlled development/operations contexts.

This component provides a restricted administration panel at `/dev-admin` to manage `config.db` custom overrides for components.

It is designed for development/operations usage, not for public users.

## What It Does

- Provides a login-protected page to edit component overrides stored in SQLite (`config.db`).
- Reads and writes records in table `custom`.
- Accepts JSON payloads with the same structure as `custom.json`:
  - `manifest` object (optional)
  - `schema` object (optional)
- Lists existing overrides and lets you load one into the editor.
- Saves overrides via upsert by component UUID (`comp_uuid`).

## Route

- Base route: `/dev-admin`

Important:
- There is intentionally no navigation menu entry for `/dev-admin`.
- This is by design (not an omission) to reduce discoverability and avoid exposing this sensitive endpoint through normal site navigation or accidental indexing paths.

## Security Model

Access is protected by **all** these checks:

1. IP restrictions:
- `DEV_ADMIN_LOCAL_ONLY=true` blocks non-loopback IPs.
- `DEV_ADMIN_ALLOWED_IPS` must include the requester IP/CIDR (defaults to `127.0.0.1,::1`).

2. Credentials from `.env`:
- `DEV_ADMIN_USER`
- `DEV_ADMIN_PASSWORD`

These variable names are currently tied to this component prefix, but they are documented as a reusable security baseline for future admin components.

3. Session login:
- After successful login, session key `DEV_ADMIN_AUTH` is set.
4. CSRF protection:
- Login, save, and logout forms require a valid CSRF token stored in session.
5. Login anti-bruteforce:
- Failed login attempts are rate-limited per client IP (component-local in-memory window).

If credentials are not configured, the panel shows an error and does not allow editing.

## Environment Configuration (`config/.env`)

Set these values:

```env
# Path to config DB
CONFIG_DB_PATH=../config/config.db

# Dev Admin credentials
DEV_ADMIN_USER=admin
DEV_ADMIN_PASSWORD=replace-with-strong-password

# Extra network guard
DEV_ADMIN_LOCAL_ONLY=true
DEV_ADMIN_ALLOWED_IPS=127.0.0.1,::1
```

Notes:
- `CONFIG_DB_PATH` default resolves to `config/config.db` in project root.
- Keep `DEV_ADMIN_LOCAL_ONLY=true` unless you really need remote access.
- If remote access is needed, use a strict allow-list in `DEV_ADMIN_ALLOWED_IPS`.

## `config.db` Integration

This component uses table:

```sql
CREATE TABLE custom (
    comp_uuid TEXT NOT NULL PRIMARY KEY,
    value_json TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    updated_at INTEGER NOT NULL
);
```

### Field Meaning

- `comp_uuid`: component UUID (example: `hellocomp_0yt2sa`)
- `value_json`: JSON text (copy/paste `custom.json`-style content)
- `enabled`: active flag (`1` enabled, `0` disabled)
- `updated_at`: Unix timestamp (seconds)

## JSON Format (same as `custom.json`)

Valid example:

```json
{
    "manifest": {
        "route": "/HelloComponent"
    },
    "schema": {
        "data": {
            "my_flag": true
        }
    }
}
```

The panel validates:
- `comp_uuid` format
- `comp_uuid` must exist in loaded components
- JSON must be a valid object

## Runtime Merge Order

When the app loads components, precedence is:

1. `manifest.json` / `schema.json` (base component files)
2. `custom.json` (if present)
3. DB override from `custom.value_json` for the same `comp_uuid`

So DB values take final precedence over `custom.json`.

## UI Workflow

1. Open `/dev-admin`.
2. Login with `DEV_ADMIN_USER` + `DEV_ADMIN_PASSWORD`.
3. Select or type a component UUID.
4. Paste/edit JSON override.
5. Save.
6. Use the table below to load existing entries for editing.

After saving, restart the application so all changes are applied consistently across component loading and routing.
Also consider Neutral TS cache behavior: in some environments, template/schema updates may not appear immediately if cache is active.
If changes are not visible, restart the app and/or disable Neutral cache in development (`NEUTRAL_CACHE_DISABLE=true`) while validating updates.

## Operational Notes

- This panel edits critical runtime behavior; keep access tightly restricted.
- Do not expose `/dev-admin` directly to the public internet.
- Prefer loopback + SSH tunnel/VPN for remote admin scenarios.

## Tests

Component tests:

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7050_dev_admin/tests/test_dev_admin_component.py
```

Related DB tests:

```bash
source .venv/bin/activate && pytest -q tests/test_config_db.py
```

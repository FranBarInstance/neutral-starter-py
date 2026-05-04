# Component: sign_0yt2sa

Manages all user authentication: sign-in, sign-up, password reminder, PIN verification, and sign-out.

## Overview

- **UUID**: `sign_0yt2sa`
- **Route Prefix**: `/sign`
- **Required dependency**: `ftoken_0yt2sa` `0.0.x`

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/sign/in` | GET | Sign-in page |
| `/sign/in/form/<ltoken>` | GET/POST | Sign-in form (AJAX) |
| `/sign/up` | GET | Sign-up page |
| `/sign/up/form/<ltoken>` | GET/POST | Sign-up form (AJAX) |
| `/sign/reminder` | GET | Password reminder page |
| `/sign/reminder/form/<ltoken>` | GET/POST | Reminder form (AJAX) |
| `/sign/out` | GET | Sign-out page |
| `/sign/out/form/<ltoken>` | GET | Execute logout (AJAX) |
| `/sign/pin/<pin_token>` | GET | PIN verification page |
| `/sign/pin/form/<pin_token>/<ltoken>` | GET/POST | PIN form (AJAX) |
| `/sign/help/<item>` | GET | Help content (cached) |

## Security

- All routes public (auth not required) — users need access when not logged in
- All POST forms protected by `ftoken` (CSRF) + `notrobot` honeypot
- Rate limiting on sign-in (per-IP + per-email hashed), sign-up, reminder, PIN
- Anti-enumeration: sign-up silently sends reminder if email exists; reminder always returns success
- Sessions tied to User Agent

## Key Flows

- **Sign-in**: email + password → check credentials → check disabled states → create session
- **Sign-up**: alias + email + password + birthdate → create user → send confirmation email → if exists, silently send reminder
- **PIN verification**: token from email link → classify target (signup/reminder) → verify PIN → remove disabled state (if signup) → create session
- **Reminder**: email → always return success → send PIN email if user exists

## Form Validation

| Form | Key Fields |
|------|------------|
| `sign_in_form` | email, password, notrobot, ftoken |
| `sign_up_form` | alias (3-50), email + MX, password + match, birthdate (13-100), agree, notrobot, ftoken |
| `sign_reminder_form` | email + MX, notrobot, ftoken |
| `sign_pin_form` | pin (4-10 alphanumeric), notrobot, ftoken |

## Integration

Sign links available via `data.current.site.sign_links`:

```html
<a href="{:;data->sign_0yt2sa->manifest->route:}/in">Sign In</a>
<a href="{:;data->sign_0yt2sa->manifest->route:}/up">Sign Up</a>
```

## Dependencies

- `ftoken_0yt2sa` — CSRF tokens (required)
- Core `User`, `Mail`, `Session` helpers

## Known Limitations

- **UNVALIDATED lifecycle**: When `VALIDATE_SIGNUP=true`, users can remain blocked after confirmation. Manual admin intervention required. Default is `VALIDATE_SIGNUP=false`.

## Testing

```bash
source .venv/bin/activate && pytest -q src/component/cmp_5100_sign/tests
```

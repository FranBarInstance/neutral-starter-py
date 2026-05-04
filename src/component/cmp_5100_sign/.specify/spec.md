# Component: sign_0yt2sa

## Executive Summary

Manages all user authentication processes: sign-in, sign-up, password reminder, PIN verification, and sign-out. A critical component that interacts directly with the core security system, providing secure authentication flows with anti-enumeration protection, rate limiting, CSRF tokens, and honeypot bot detection.

## Identity

- **UUID**: `sign_0yt2sa`
- **Base Route**: `/sign`
- **Version**: `0.0.0`
- **Required dependency**: `ftoken_0yt2sa` `0.0.x`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

**Critical security properties:**
- All routes are publicly accessible (authentication not required) — users must be able to reach auth forms when not logged in
- Sign-out requires active session (enforced in handler logic, not route config)
- All POST forms protected by `ftoken` (CSRF) and `notrobot` honeypot
- Rate limiting on sign-in, sign-up, reminder, and PIN routes
- Sign-in rate limited per email (SHA256 hashed) in addition to per-IP
- Account enumeration protection: sign-up silently sends reminder if email exists
- Reminder always returns success regardless of email existence
- Sessions tied to User Agent

## Architecture

### Component Type
**Authentication** component. Provides:
- Sign-in with credential validation
- Sign-up with email confirmation via PIN
- Password reminder with email PIN
- PIN verification for signup confirmation and reminder access
- Sign-out with session cleanup
- Help content for auth items
- Session-dependent menus (navbar, drawer, session menu)
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_NNNN_sign/
├── manifest.json                          # Identity, security, dependencies
├── schema.json                            # Menus, translations, sign links
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions with rate limiting
│   ├── sign_handler.py                    # Business logic (6 handler classes)
│   └── schema.json                        # Form validation rules (5 forms)
├── neutral/
│   ├── component-init.ntpl                # Global snippet loading
│   ├── snippets-session-false.ntpl        # Modals for unauthenticated users
│   ├── snippets-session-true.ntpl         # Logout modal for authenticated users
│   └── route/
│       ├── index-snippets.ntpl            # Auto-loaded snippets
│       ├── snippets.ntpl                  # Shared snippets
│       ├── locale-{lang}.json             # Translations (6 languages)
│       └── root/
│           ├── in/                        # Sign-in page + AJAX form
│           ├── up/                        # Sign-up page + AJAX form
│           ├── out/                       # Sign-out page + AJAX form
│           ├── reminder/                  # Reminder page + AJAX form
│           ├── pin/                       # PIN verification page + AJAX form
│           ├── unconfirmed/               # Unconfirmed account info
│           └── help/                      # Help content items
└── tests/
    └── test_sign_component.py             # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Rate Limit | Purpose |
|-------|--------|---------|------------|---------|
| `/sign/in` | GET | `SignInRequestHandler` | — | Sign-in page |
| `/sign/in/form/<ltoken>` | GET | `SignInRequestHandler` | — | Load sign-in form (AJAX) |
| `/sign/in/form/<ltoken>` | POST | `SignInRequestHandler` | `SIGNIN_LIMITS` + `SIGNIN_EMAIL_LIMITS` | Authenticate user |
| `/sign/up` | GET | `SignUpRequestHandler` | — | Sign-up page |
| `/sign/up/form/<ltoken>` | GET | `SignUpRequestHandler` | — | Load sign-up form (AJAX) |
| `/sign/up/form/<ltoken>` | POST | `SignUpRequestHandler` | `SIGNUP_LIMITS` | Register user |
| `/sign/reminder` | GET | `SignReminderRequestHandler` | — | Reminder page |
| `/sign/reminder/form/<ltoken>` | GET | `SignReminderRequestHandler` | — | Load reminder form (AJAX) |
| `/sign/reminder/form/<ltoken>` | POST | `SignReminderRequestHandler` | `SIGNREMINDER_LIMITS` + Ajax required | Send reminder |
| `/sign/out` | GET | `SignOutRequestHandler` | — | Sign-out page |
| `/sign/out/form/<ltoken>` | GET | `SignOutRequestHandler` | Ajax required | Execute logout |
| `/sign/pin/<pin_token>` | GET | `SignPinRequestHandler` | — | PIN verification page |
| `/sign/pin/form/<pin_token>/<ltoken>` | GET | `SignPinRequestHandler` | — | Load PIN form (AJAX) |
| `/sign/pin/form/<pin_token>/<ltoken>` | POST | `SignPinRequestHandler` | `SIGNT_LIMITS` + Ajax required | Verify PIN |
| `/sign/help/<item>` | GET | `SignRequestHandler` | — + cached 3600s | Help content |

### Request Handlers (`route/sign_handler.py`)

6 handler classes extending `SignRequestHandler` → `FormRequestHandler`:

**Base class: `SignRequestHandler`**
- `validate_get()`: Rejects if session already active
- `validate_post()`: Rejects if session active + validates ftoken + form tokens + fields
- `send_reminder(email)`: Sends password reminder email via `Mail` core helper
- `create_session(user_data)`: Creates session cookie with UA binding

**`SignInRequestHandler`** — Sign-in processing
- Validates credentials via `user.check_login(email, password, pin)`
- Checks `UNCONFIRMED` and `UNVALIDATED` disabled states
- Creates session on success

**`SignUpRequestHandler`** — Registration processing
- Creates user via `user.create()` with alias, email, password, birthdate, locale
- If email exists (`USER_EXISTS`): silently sends reminder (anti-enumeration)
- On success: sends confirmation email with PIN via `Mail`

**`SignOutRequestHandler`** — Session termination
- Closes session via `session.close()`
- Sets session cleanup cookie

**`SignReminderRequestHandler`** — Password reminder
- Always returns success (anti-enumeration)
- Sends reminder email if user exists (silently fails if not)

**`SignPinRequestHandler`** — PIN verification
- Resolves `pin_token` to database row via `get-pin-by-token`
- Classifies target: `signup` (UNCONFIRMED) or `reminder`
- On PIN match + signup target: removes UNCONFIRMED disabled state
- Deletes used PIN (one-time use)
- Creates session after successful verification

### Key Business Logic

#### Sign-In Flow
1. User submits email + password + notrobot
2. `ftoken_check()` validates CSRF token
3. `user.check_login()` verifies credentials
4. Check disabled states (UNCONFIRMED, UNVALIDATED)
5. Create session with UA binding

#### Sign-Up Flow
1. User submits alias + email + password + birthdate + agree + notrobot
2. `ftoken_check()` validates CSRF token
3. `user.create()` creates account (with UNCONFIRMED disabled state if `VALIDATE_SIGNUP=true`)
4. If email exists: silently send reminder (no error disclosed)
5. On success: send confirmation email with PIN token

#### PIN Verification Flow
1. User arrives via email link: `/sign/pin/<pin_token>`
2. System resolves token to DB row, classifies target (signup/reminder)
3. User submits PIN
4. On match: remove UNCONFIRMED (if signup), delete PIN, create session

#### Anti-Enumeration Protection
- **Sign-up**: If email exists, silently sends reminder instead of error
- **Reminder**: Always returns success regardless of email existence
- Neither flow reveals whether an email is registered

### Dependencies

- **Required**: `ftoken_0yt2sa` `0.0.x` (CSRF form tokens)
- **Depends on**: Core `User` helper, Core `Mail` helper, Core `Session` helper
- **Used by**: Session menu system, drawer menu, navbar menu, `user_0yt2sa` (logout link)

## Data and Models

### Sign Links (`data.current.site.sign_links`)

Global sign route references for use by other components:

| Key | Value |
|-----|-------|
| `in` | `<manifest.route>/in` |
| `up` | `<manifest.route>/up` |
| `reminder` | `<manifest.route>/reminder` |
| `out` | `<manifest.route>/out` |
| `pin` | `<manifest.route>/pin` |

### Form Validation (`route/schema.json`)

| Form | Fields | Key Validation |
|------|--------|----------------|
| `sign_in_form` | email, password, remember, notrobot, pin | Email + password + notrobot="human" + ftoken |
| `sign_up_form` | alias, email, password, rptpassword, birthdate, agree, notrobot | Alias (3-50), email + MX, password match, age 13-100, agree=true, notrobot="human" + ftoken |
| `sign_reminder_form` | email, notrobot | Email + MX DNS + notrobot="human" + ftoken |
| `sign_pin_form` | pin, notrobot | PIN (4-10 alphanumeric) + notrobot="human" + ftoken |
| `sign_out_form` | (none) | Token validation only |

### Honeypot Protection (`notrobot` / `notrobot-hidden`)

All forms include:
- `notrobot`: Checkbox with required value `"human"` (bots won't check it)
- `notrobot-hidden`: Hidden field that must NOT be submitted (`"set": false`) — if present, indicates bot

### Translations (`inherit.locale.trans`)

6 languages with UI strings:

| Key | EN | ES |
|-----|----|----|
| Sign in | Sign in | Iniciar sesión |
| Sign up | Sign up | Registrarse |
| Sign out | Sign out | Cerrar sesión |
| Reminder | Reminder | Recordar |
| Confirm logout | Confirm logout | Confirmar cierre de sesión |

Full translations also in FR, DE, AR, ZH. Extended translations in `neutral/route/locale-{lang}.json`.

### Session Menu (`data.current.menu["session:"]`)

Menu entries for unauthenticated users:

| Entry | Text | Link | Icon |
|-------|------|------|------|
| login | Sign in | `<manifest.route>/in` | `x-icon-sign-in` |
| register | Sign up | `<manifest.route>/up` | `x-icon-sign-up` |
| reminder | Reminder | `<manifest.route>/reminder` | `x-icon-sign-reminder` |

### Navbar Menu (`data.navbar.menu`)

| Session State | Entry | Name | Link | Icon | Properties |
|---------------|-------|------|------|------|------------|
| No session | signin | Sign in | `#loginModal` | `x-icon-sign-in` | `data-bs-toggle=modal, data-bs-target=#loginModal` |
| No session | signup | Sign up | `#registerModal` | `x-icon-sign-up` | `data-bs-toggle=modal, data-bs-target=#registerModal` |
| Authenticated | signout | Sign out | `#logoutModal` | `x-icon-sign-out` | `data-bs-toggle=modal, data-bs-target=#logoutModal` |

### Drawer Menu (`data.current.drawer.menu["session:"]`)

| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| sign | User | sign | `x-icon-user` |

## Configuration

| Config Key | Purpose |
|------------|---------|
| `Config.VALIDATE_SIGNUP` | If true, new users require PIN confirmation before login (default: false) |
| `Config.PIN_EXPIRES_SECONDS` | PIN lifetime for signup/reminder (displayed as hours in email) |
| `Config.SIGNIN_LIMITS` | Rate limit string for sign-in (per-IP) |
| `Config.SIGNIN_EMAIL_LIMITS` | Rate limit string for sign-in (per-email, SHA256 hashed) |
| `Config.SIGNUP_LIMITS` | Rate limit string for sign-up |
| `Config.SIGNREMINDER_LIMITS` | Rate limit string for reminder |
| `Config.SIGNT_LIMITS` | Rate limit string for PIN verification |
| `Config.DISABLED[UNCONFIRMED]` | Disabled reason value for unconfirmed accounts |
| `Config.DISABLED[UNVALIDATED]` | Disabled reason value for unvalidated accounts |
| `Config.SESSION_KEY` | Session cookie key name |

## Technical Rationale

- **Anti-enumeration**: Neither sign-up nor reminder reveal whether an email is registered
- **Dual rate limiting on sign-in**: Per-IP + per-email (hashed) prevents brute force from distributed sources
- **ftoken integration**: All forms validated against CSRF via `ftoken_check()`
- **Honeypot bot detection**: `notrobot` checkbox + `notrobot-hidden` hidden field
- **PIN token flow**: Email links contain token, user enters PIN separately — prevents token theft via email link inspection
- **One-time PIN**: PIN deleted after successful verification
- **UA-bound sessions**: Sessions tied to User Agent for additional security
- **Session-dependent menus**: Navbar, drawer, and session menus change based on auth state
- **Bootstrap modals**: Navbar entries trigger modal dialogs instead of page navigation
- **Cached help content**: Help items cached for 1 hour

## Known Limitations

- **UNVALIDATED lifecycle**: When `VALIDATE_SIGNUP=true`, users can remain blocked even after confirmation. Manual admin intervention required to remove `UNVALIDATED` from `user_disabled`. Default is `VALIDATE_SIGNUP=false` to avoid blocking signups.

---

## Acceptance Criteria (SDD)

### Functional — Sign In
- [x] `/sign/in` renders sign-in page
- [x] Sign-in validates email + password via `user.check_login()`
- [x] Sign-in checks UNCONFIRMED and UNVALIDATED disabled states
- [x] Sign-in creates session with UA binding on success
- [x] Sign-in rejects if user already has active session

### Functional — Sign Up
- [x] `/sign/up` renders sign-up page
- [x] Sign-up creates user with alias, email, password, birthdate, locale
- [x] Sign-up sends confirmation email with PIN token on success
- [x] Sign-up silently sends reminder if email already exists (anti-enumeration)
- [x] Sign-up requires `agree=true` and `notrobot=human`

### Functional — Reminder
- [x] `/sign/reminder` renders reminder page
- [x] Reminder always returns success (anti-enumeration)
- [x] Reminder sends email with PIN token if user exists

### Functional — PIN Verification
- [x] `/sign/pin/<token>` renders PIN verification page
- [x] PIN token resolved to DB row with target classification
- [x] Signup PIN: removes UNCONFIRMED disabled state + creates session
- [x] Reminder PIN: creates session directly
- [x] PIN deleted after successful verification (one-time use)
- [x] Invalid/expired token detected and reported

### Functional — Sign Out
- [x] `/sign/out` renders sign-out confirmation page
- [x] Sign-out closes session and sets cleanup cookie
- [x] Sign-out requires active session

### Technical
- [x] All POST forms protected by `ftoken_check()` (CSRF)
- [x] All forms include `notrobot` honeypot protection
- [x] Rate limiting applied to sign-in, sign-up, reminder, PIN routes
- [x] Sign-in rate limited per-IP and per-email (SHA256 hashed)
- [x] Reminder and PIN POST routes require `Requested-With-Ajax` header
- [x] Help content cached for 1 hour
- [x] Form validation rules defined in `route/schema.json` (5 forms)
- [x] Required dependency on `ftoken_0yt2sa` declared in manifest

### Integration
- [x] Session menu entries for unauthenticated users
- [x] Navbar modal triggers (loginModal, registerModal, logoutModal)
- [x] Drawer menu entry for unauthenticated users
- [x] Sign links exposed via `data.current.site.sign_links`
- [x] Menu links use `[:;data->sign_0yt2sa->manifest->route:]` BIF
- [x] Used by `user_0yt2sa` for logout link

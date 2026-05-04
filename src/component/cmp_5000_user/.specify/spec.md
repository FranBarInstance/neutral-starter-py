# Component: user_0yt2sa

## Executive Summary

User profile management component providing authenticated users with the ability to view and edit their profile data, manage their email addresses (add/delete with PIN verification), and manage their account settings (password change, birthdate change, login email change). All operations require authentication and use the user ID from the session context — never from URL parameters — ensuring no cross-user access.

## Identity

- **UUID**: `user_0yt2sa`
- **Base Route**: `/user`
- **Version**: `1.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": true
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

**Critical security properties:**
- All routes require authentication (`"/": true` applies to all sub-routes)
- User ID is always obtained from `USER.userId` in request context, never from URL parameters
- Cross-user access is impossible by design
- Sensitive operations (password, birthdate, login change) require PIN verification via email
- Login email change requires current password verification

## Architecture

### Component Type
**User management** component. Provides:
- Profile viewing and editing
- Email management (add, delete, PIN verification)
- Account management (password, birthdate, login email)
- Session menu entries for authenticated users
- Drawer menu entries for authenticated users
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_NNNN_user/
├── manifest.json                          # Identity and security
├── schema.json                            # Menus, translations, inheritance
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions
│   ├── user_handler.py                    # Business logic (11 handler classes)
│   └── schema.json                        # Form validation rules (8 forms)
├── neutral/
│   └── route/
│       ├── index-snippets.ntpl            # Auto-loaded snippets
│       ├── locale-{lang}.json             # Translations (6 languages)
│       └── root/
│           ├── data.json                  # /u route metadata
│           ├── content-snippets.ntpl      # /u content
│           ├── profile/
│           │   ├── data.json              # /u/profile metadata
│           │   ├── content-snippets.ntpl  # /u/profile content
│           │   ├── snippets.ntpl          # Profile form snippets
│           │   └── ajax/
│           │       └── content-snippets.ntpl  # AJAX response
│           ├── email/
│           │   ├── data.json              # /u/email metadata
│           │   ├── content-snippets.ntpl  # /u/email content
│           │   ├── snippets.ntpl          # Email form snippets
│           │   ├── pin/                   # PIN request form
│           │   ├── add/                   # Add email form
│           │   └── delete/                # Delete email form
│           └── account/
│               ├── data.json              # /u/account metadata
│               ├── content-snippets.ntpl  # /u/account content
│               ├── snippets.ntpl          # Account form snippets
│               ├── password/              # Password change (pin + change)
│               ├── birthdate/             # Birthdate change (pin + change)
│               └── login/                 # Login email change
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

#### Profile Routes

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/u` | GET | `UserRequestHandler` | Profile view (read-only) |
| `/u/profile` | GET | `UserProfileFormHandler` | Profile edit page |
| `/u/profile/ajax/<ltoken>` | GET | `UserProfileFormHandler` | Load profile form (AJAX) |
| `/u/profile/ajax/<ltoken>` | POST | `UserProfileFormHandler` | Submit profile changes (AJAX) |

#### Email Routes

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/u/email` | GET | `UserEmailRequestHandler` | Email management page |
| `/u/email/pin/ajax/<ltoken>` | GET | `UserEmailPinFormHandler` | Load PIN request form (AJAX) |
| `/u/email/pin/ajax/<ltoken>` | POST | `UserEmailPinFormHandler` | Send PIN to email (AJAX) |
| `/u/email/add/ajax/<ltoken>` | GET | `UserEmailAddFormHandler` | Load add email form (AJAX) |
| `/u/email/add/ajax/<ltoken>` | POST | `UserEmailAddFormHandler` | Add email with PIN (AJAX) |
| `/u/email/delete/ajax/<ltoken>` | GET | `UserEmailDeleteFormHandler` | Load delete form (AJAX) |
| `/u/email/delete/ajax/<ltoken>` | POST | `UserEmailDeleteFormHandler` | Delete email (AJAX) |

#### Account Routes

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/u/account` | GET | `UserAccountRequestHandler` | Account management page |
| `/u/account/password/pin/ajax/<ltoken>` | GET/POST | `UserAccountPasswordPinFormHandler` | Request password PIN |
| `/u/account/password/ajax/<ltoken>` | GET/POST | `UserAccountPasswordChangeFormHandler` | Change password |
| `/u/account/birthdate/pin/ajax/<ltoken>` | GET/POST | `UserAccountBirthdatePinFormHandler` | Request birthdate PIN |
| `/u/account/birthdate/ajax/<ltoken>` | GET/POST | `UserAccountBirthdateChangeFormHandler` | Change birthdate |
| `/u/account/login/ajax/<ltoken>` | GET/POST | `UserAccountLoginChangeFormHandler` | Change login email |

### Request Handlers (`route/user_handler.py`)

11 handler classes organized by functional area:

**Profile:**
- `UserRequestHandler` — Base handler, loads user data from context
- `UserProfileFormHandler` — Profile edit form with username validation, image ownership check, and cache invalidation

**Email:**
- `UserEmailRequestHandler` — Email list page, loads user emails with delete protection
- `UserEmailPinFormHandler` — Sends PIN to new email for verification
- `UserEmailAddFormHandler` — Adds email after PIN verification
- `UserEmailDeleteFormHandler` — Deletes email with minimum email protection

**Account:**
- `UserAccountRequestHandler` — Account management page
- `UserAccountPasswordPinFormHandler` — Sends PIN to login email for password change
- `UserAccountPasswordChangeFormHandler` — Changes password after PIN verification
- `UserAccountBirthdatePinFormHandler` — Sends PIN for birthdate change
- `UserAccountBirthdateChangeFormHandler` — Changes birthdate after PIN verification
- `UserAccountLoginChangeFormHandler` — Changes login email after password verification

### Key Business Logic

#### Profile Edit (`UserProfileFormHandler.post()`)
1. Normalize username
2. Validate form tokens and fields
3. Check image ownership (image must belong to user's profile)
4. Validate username change (cooldown, taken, blacklisted)
5. Save profile data (username, alias, locale, region, imageId, properties with theme/color/dark_mode)
6. Invalidate public profile image cache for old/new username
7. Update session data in `schema_data["USER"]["profile"]`

#### Email Add Flow (Two-Step PIN)
1. **Step 1** (`email/pin`): User enters email → system checks ownership → sends PIN via email
2. **Step 2** (`email/add`): User enters email + PIN → system verifies PIN → adds email → deletes used PIN

#### Email Delete Protection
- If `Config.REQUIRES_USER_EMAIL` is true and user has only one email, deletion is blocked
- `user_email_delete_disabled` flag controls UI state

#### Password Change Flow (Two-Step PIN)
1. **Step 1** (`password/pin`): User enters login email → system verifies it belongs to user → sends PIN
2. **Step 2** (`password/change`): User enters PIN + new password → system verifies PIN → updates password → deletes used PIN

#### Birthdate Change Flow (Two-Step PIN)
1. **Step 1** (`birthdate/pin`): Same as password PIN flow
2. **Step 2** (`birthdate/change`): User enters PIN + birthdate → system verifies PIN → updates birthdate

#### Login Email Change (Password Verification)
- User selects existing email + enters current password
- System verifies password, checks email ownership, updates login
- No PIN required — password verification is sufficient

#### Public Image Cache Invalidation
When username changes, the handler invalidates cached public profile-image responses for both old and new usernames via `Image().invalidate_public_username_cache()`. This targets the route `<image manifest.route>/p/<username>`.

### Dependencies

- **Depends on**: `forms_0yt2sa` (form utilities and snippets), `ftoken_0yt2sa` (CSRF tokens), core `User` helper, core `Mail` helper, core `Image` helper
- **Used by**: Session menu system, drawer menu system

## Data and Models

### Profile Fields

| Field | Required | Validation | Description |
|-------|----------|------------|-------------|
| `username` | No | 0-30 chars, `^[a-z0-9]([a-z0-9-]*[a-z0-9])?$` | Public identifier for profile image route |
| `alias` | Yes | 2-50 chars | Display name |
| `locale` | No | 2-10 chars, `^[a-zA-Z]{2,10}$` | Preferred language code |
| `region` | No | Max 20 chars | Geographic region |
| `imageId` | No | UUID format | Profile avatar image ID |
| `properties` | No | Max 2000 chars (JSON) | Additional properties |
| `theme` | No | Max 50 chars | Theme preference (stored in properties) |
| `color` | No | Max 20 chars | Color preference (stored in properties) |
| `dark_mode` | No | — | Dark mode preference (stored in properties) |

### Email Forms

| Form | Fields | Key Validation |
|------|--------|----------------|
| `user_email_pin` | email | Email format + MX DNS check |
| `user_email_add` | email, pin | Email format + 6-digit PIN |
| `user_email_delete` | email, confirm_email | Email format + confirmation checkbox |

### Account Forms

| Form | Fields | Key Validation |
|------|--------|----------------|
| `user_account_password_pin` | email | Login email + MX DNS check |
| `user_account_password_change` | pin, password, rptpassword | 6-digit PIN + password match |
| `user_account_birthdate_pin` | email | Login email + MX DNS check |
| `user_account_birthdate_change` | pin, birthdate | 6-digit PIN + age 13-100 |
| `user_account_login_change` | email, current_password | MX DNS check + password verify |

### Translations (`inherit.locale.trans`)

6 languages with UI strings:

| Key | EN | ES |
|-----|----|----|
| User | User | Usuario |
| Profile | Profile | Perfil |
| Edit Profile | Edit Profile | Editar Perfil |
| Edit Email | Edit Email | Editar correo |
| Edit Account | Edit Account | Editar cuenta |
| Sign out | Sign out | Cerrar sesión |

Full translations also in FR, DE, AR, ZH. Extended translations in `neutral/route/locale-{lang}.json` for form labels, error messages, and success messages.

### Session Menu (`data.current.menu["session:true"]`)

Menu entries for authenticated users:

| Entry | Text | Link | Icon |
|-------|------|------|------|
| profile | Profile | `<manifest.route>` | `x-icon-user` |
| edit-profile | Edit Profile | `<manifest.route>/profile` | `x-icon-profile` |
| edit-email | Edit Email | `<manifest.route>/email` | `x-icon-email` |
| edit-account | Edit Account | `<manifest.route>/account` | `x-icon-lock` |
| logout | Sign out | `<sign.route>/out` | `x-icon-sign-out` |

### Drawer Menu (`data.current.drawer.menu["session:true"]`)

| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| user | User | user | `x-icon-user` |

## Configuration

| Config Key | Purpose |
|------------|---------|
| `Config.REQUIRES_USER_EMAIL` | If true, users must have at least one email (blocks deletion of last email) |
| `Config.PIN_ACCOUNT_EXPIRES_SECONDS` | PIN lifetime for account operations (displayed as hours in email) |
| `Config.SECRET_KEY` | Key for HMAC signing (used by ftoken) |

## Technical Rationale

- **Context-based user ID**: User ID from session prevents cross-user access by design
- **Two-step PIN flows**: Sensitive operations require email verification before changes
- **Password verification for login change**: Login email change is the most sensitive operation — requires current password instead of PIN
- **Username cooldown**: Prevents rapid username changes that could abuse public profile routes
- **Image ownership check**: Profile image must belong to user's profile (prevents referencing other users' images)
- **Cache invalidation on username change**: Public profile image route is cached per username; must invalidate when username changes
- **Session data sync**: After profile save, `schema_data["USER"]["profile"]` is updated so the session reflects changes immediately
- **Theme in properties**: Theme, color, and dark_mode are stored inside `properties` JSON, keeping the profile schema clean
- **Minimum email protection**: When `REQUIRES_USER_EMAIL` is true, the last email cannot be deleted
- **AJAX forms**: All forms use `{:fetch; ... :}` pattern with LTOKEN for seamless UX

---

## Acceptance Criteria (SDD)

### Functional — Profile
- [x] `/u` displays authenticated user's profile (read-only)
- [x] `/u/profile` provides edit form for profile data
- [x] Profile form saves username, alias, locale, region, imageId, theme/color/dark_mode
- [x] Username normalized and validated (cooldown, taken, blacklisted)
- [x] Image ownership verified before saving
- [x] Public profile image cache invalidated on username change
- [x] Session data updated after successful profile save

### Functional — Email
- [x] `/u/email` displays user's email list
- [x] PIN sent to new email via `Mail` core helper
- [x] Email added after PIN verification
- [x] Email deleted with minimum email protection when `REQUIRES_USER_EMAIL` is true
- [x] Duplicate email detection (own and other users)

### Functional — Account
- [x] Password change requires PIN verification sent to login email
- [x] Birthdate change requires PIN verification sent to login email
- [x] Login email change requires current password verification
- [x] PIN deleted after successful verification (one-time use)
- [x] Birthdate validated with min age 13, max age 100

### Technical
- [x] All routes require authentication (`"/": true`)
- [x] User ID always from `USER.userId` context, never from URL
- [x] All forms use `FormRequestHandler` with LTOKEN validation
- [x] Form validation rules defined in `route/schema.json`
- [x] 8 form schemas defined with field rules and validation
- [x] Translations provided in 6 languages

### Integration
- [x] Session menu entries for authenticated users
- [x] Drawer menu entry for authenticated users
- [x] Menu links use `[:;data->user_0yt2sa->manifest->route:]` BIF
- [x] Logout link references `sign_0yt2sa` component route
- [x] Depends on `forms_0yt2sa` for form utilities
- [x] Uses core `User`, `Mail`, and `Image` helpers

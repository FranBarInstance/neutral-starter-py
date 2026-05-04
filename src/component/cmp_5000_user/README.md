# Component: user_0yt2sa

User profile management component.

## Overview

Provides authenticated users with profile viewing/editing, email management (add/delete with PIN verification), and account management (password, birthdate, login email changes). All routes require authentication. User ID is always from session context — never from URL parameters.

## Routes

### Profile

| Route | Method | Description |
|-------|--------|-------------|
| `/u` | GET | Profile view (read-only) |
| `/u/profile` | GET | Profile edit page |
| `/u/profile/ajax/<ltoken>` | GET/POST | Profile form (AJAX) |

### Email

| Route | Method | Description |
|-------|--------|-------------|
| `/u/email` | GET | Email management page |
| `/u/email/pin/ajax/<ltoken>` | GET/POST | Request PIN for new email |
| `/u/email/add/ajax/<ltoken>` | GET/POST | Add email with PIN |
| `/u/email/delete/ajax/<ltoken>` | GET/POST | Delete email |

### Account

| Route | Method | Description |
|-------|--------|-------------|
| `/u/account` | GET | Account management page |
| `/u/account/password/pin/ajax/<ltoken>` | GET/POST | Request password change PIN |
| `/u/account/password/ajax/<ltoken>` | GET/POST | Change password |
| `/u/account/birthdate/pin/ajax/<ltoken>` | GET/POST | Request birthdate change PIN |
| `/u/account/birthdate/ajax/<ltoken>` | GET/POST | Change birthdate |
| `/u/account/login/ajax/<ltoken>` | GET/POST | Change login email |

## Security

- All routes require authentication (`"/": true`)
- User ID from `USER.userId` context, never from URL
- Sensitive operations require PIN verification via email
- Login email change requires current password
- Cross-user access impossible by design

## Profile Fields

| Field | Required | Validation |
|-------|----------|------------|
| `username` | No | 0-30 chars, lowercase alphanumeric + hyphens |
| `alias` | Yes | 2-50 chars |
| `locale` | No | 2-10 chars, language code |
| `region` | No | Max 20 chars |
| `imageId` | No | UUID format |
| `theme`/`color`/`dark_mode` | No | Stored in properties JSON |

## Key Flows

- **Email add**: Two-step PIN (send PIN → verify + add)
- **Password change**: Two-step PIN (send PIN → verify + change)
- **Birthdate change**: Two-step PIN (send PIN → verify + change)
- **Login change**: Password verification (no PIN needed)
- **Username change**: Cooldown + taken + blacklist validation + cache invalidation

## Dependencies

- `forms_0yt2sa` — Form utilities and snippets
- `ftoken_0yt2sa` — CSRF tokens
- Core `User`, `Mail`, `Image` helpers

## Testing

```bash
source .venv/bin/activate && python -m pytest src/component/cmp_5000_user/tests/ -v
```

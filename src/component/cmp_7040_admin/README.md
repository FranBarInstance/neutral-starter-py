# Admin — `admin_0yt2sa`

Role-based admin panel for managing users, profiles, images, and posts. Access
restricted to users with `admin` or `moderator` roles.

## Overview

The admin component provides a comprehensive administration interface with
granular role-based permissions. Admins have full access to all actions; moderators
have restricted capabilities (e.g., cannot delete users, limited disabled reasons).

All POST actions require LTOKEN validation and include strict input sanitization.

## Routes

| Route | Methods | Description |
|-------|---------|-------------|
| `/admin/` | GET | Admin dashboard (shows current user roles) |
| `/admin/help` | GET | Help with technical docs and policy placeholder |
| `/admin/user` | GET, POST | User management (list, disable, delete, close sessions) |
| `/admin/profile` | GET, POST | Profile management (list, disable, assign roles) |
| `/admin/image` | GET, POST | Image management (list, search, disable, paginate) |
| `/admin/image/ajax` | GET | AJAX image list pagination |
| `/admin/post` | GET | Post management placeholder |

## Role Permissions

| Action | Admin | Moderator |
|--------|-------|-----------|
| Set user disabled | All reasons | `unvalidated`, `moderated` only |
| Remove user disabled | All reasons | `unvalidated`, `moderated` only |
| Delete user | Yes (no self-delete) | No |
| Close user sessions | Yes | No |
| Set profile disabled | `moderated`, `spam` | `moderated`, `spam` |
| Remove profile disabled | `moderated`, `spam` | `moderated`, `spam` |
| Assign/remove role | Yes | No |
| Set image disabled | All reasons | `moderated`, `spam` only |
| Remove image disabled | All reasons | `moderated`, `spam` only |

## Security

- **Auth**: All routes require authentication + `admin` or `moderator` role
- **CSRF**: All POST actions require LTOKEN validation
- **Input validation**: IDs validated against `^[a-zA-Z0-9_-]+$`, max 64 chars
- **Destructive actions**: Require confirmation strings (`DELETE`, `CLOSE SESSIONS`)
- **Self-deletion prevention**: Admins cannot delete their own account
- **AJAX protection**: `/admin/image/ajax` requires `Requested-With-Ajax` header

## Access Control

`component-init.ntpl` evaluates `USER.profile_roles` at request time. If the user
lacks `admin`/`moderator` roles, `access-false.json` is loaded which removes all
admin menu entries from both session and drawer menus.

## Menus

**Session menu** (`session:true`): Admin, Users, Profiles, Images, Posts, Help
entries with BIF route references.

**Drawer menu** (`session:true`): Single "Admin" entry.

## Translations

6 languages: EN, ES, FR, DE, AR, ZH.

## Dependencies

- `RequestHandler` core — base rendering
- `core.image.Image` — image operations and cache invalidation
- `utils.tokens.ltoken_check` — form token validation
- `constants` — disabled reason constants, RBAC roles
- `app.config.Config` — DISABLED reasons configuration
- `app.extensions.require_header_set` — AJAX header enforcement
- `http_errors` (`http_errors_0yt2sa`) — 404 rendering

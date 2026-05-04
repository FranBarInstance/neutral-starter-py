# Component: admin_0yt2sa

## Executive Summary

Role-based admin panel providing authenticated users with `admin` or `moderator` roles the ability to manage users, profiles, images, and posts. The component enforces granular role-based permissions: admins have full access while moderators have restricted capabilities (e.g., cannot delete users, cannot set certain disabled reasons). All POST actions require LTOKEN validation and include comprehensive input sanitization.

## Identity

- **UUID**: `admin_0yt2sa`
- **Base Route**: `/admin`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": true
}
- **Allowed roles**: {
  "/": [
    "admin",
    "moderator"
  ]
}

**Critical security properties:**
- All routes require authentication
- Only `admin` and `moderator` roles can access any `/admin/*` route
- Role-based action control: admins have full access, moderators have restricted access
- All POST actions require LTOKEN validation (`ltoken_check` against UTOKEN)
- Input validation on all IDs (alphanumeric, hyphens, underscores; max 64 chars)
- Self-deletion prevention (admin cannot delete their own user)
- Confirmation strings required for destructive actions (`DELETE`, `CLOSE SESSIONS`)
- Access denied state (`access-false.json`) removes menu entries when user lacks roles

## Architecture

### Component Type

**Administration** component. Provides:
- Admin home dashboard with role information
- User management (list, search, disable/enable, delete, close sessions)
- Profile management (list, search, disable/enable, assign/remove roles)
- Image management (list, search, pagination, disable/enable with AJAX load-more)
- Post management (placeholder page)
- Help section with technical documentation and policy placeholder
- Session menu entries for admin/moderator users
- Drawer menu entry for admin/moderator users
- Translations in 6 languages

### Directory Structure

```
src/component/cmp_7040_admin/
├── manifest.json                          # Identity and security
├── schema.json                            # Menus, translations, inheritance
├── access-false.json                      # Menu removal when access denied
├── __init__.py                            # Component init hook (no-op)
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions
│   └── admin_handler.py                   # 6 handler classes
├── neutral/
│   ├── component-init.ntpl                # Role-based access control + snippet loading
│   └── route/
│       ├── index-snippets.ntpl            # Layout overrides, locale, image snippets
│       ├── image-snippets.ntpl            # Shared image admin snippets
│       └── root/
│           ├── data.json                  # Admin home metadata
│           ├── content-snippets.ntpl      # Admin home content
│           ├── help/
│           │   ├── data.json
│           │   ├── content-snippets.ntpl
│           │   ├── policy.ntpl            # Policy placeholder
│           │   └── technical.ntpl         # Technical documentation
│           ├── user/
│           │   ├── data.json
│           │   └── content-snippets.ntpl  # User management UI
│           ├── profile/
│           │   ├── data.json
│           │   └── content-snippets.ntpl  # Profile management UI
│           ├── image/
│           │   ├── data.json
│           │   ├── content-snippets.ntpl  # Image management UI
│           │   ├── README.md              # Image route documentation
│           │   └── ajax/
│           │       └── content-snippets.ntpl  # AJAX load-more
│           └── post/
│               ├── data.json
│               └── content-snippets.ntpl  # Post management placeholder
└── tests/
    └── test_routes.py                     # Component tests
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Purpose |
|-------|--------|---------|---------|
| `/admin/` | GET | `AdminHomeRequestHandler` | Admin home dashboard |
| `/admin/help` | GET | `AdminHomeRequestHandler` | Admin help page |
| `/admin/user` | GET, POST | `AdminUserRequestHandler` | User management |
| `/admin/profile` | GET, POST | `AdminProfileRequestHandler` | Profile management |
| `/admin/image` | GET, POST | `AdminImageRequestHandler` | Image management |
| `/admin/image/ajax` | GET | `AdminImageRequestHandler` | AJAX image list pagination |
| `/admin/post` | GET | `AdminPostRequestHandler` | Post management (placeholder) |

### Request Handlers (`route/admin_handler.py`)

6 handler classes organized by responsibility:

**Base:**
- `AdminRequestHandler` — Base class with role resolution, input validation, image cache invalidation helpers

**Section handlers:**
- `AdminHomeRequestHandler` — Renders admin home and help pages with role info
- `AdminUserRequestHandler` — User listing, search, filtering, disable/enable, delete, close sessions
- `AdminProfileRequestHandler` — Profile listing, search, filtering, disable/enable, role assignment
- `AdminImageRequestHandler` — Image listing, search, pagination, disable/enable, AJAX load-more
- `AdminPostRequestHandler` — Post management placeholder

### Key Business Logic

#### Role-Based Permissions

| Action | Admin | Moderator |
|--------|-------|-----------|
| Set user disabled (any reason) | Yes | Only `unvalidated`, `moderated` |
| Remove user disabled | Yes | Only `unvalidated`, `moderated` |
| Delete user | Yes | No |
| Close user sessions | Yes | No |
| Set profile disabled | Yes | Only `moderated`, `spam` |
| Remove profile disabled | Yes | Only `moderated`, `spam` |
| Assign/remove profile role | Yes | No |
| Set image disabled | Yes | Only `moderated`, `spam` |
| Remove image disabled | Yes | Only `moderated`, `spam` |

#### User Actions (`AdminUserRequestHandler._apply_user_action`)
1. **set-disabled**: Set user disabled status with reason + optional description
2. **remove-disabled**: Remove a disabled reason from user
3. **delete-user**: Delete user (admin only, requires `DELETE` confirmation, cannot self-delete)
4. **close-sessions**: Close all active user sessions (admin only, requires `CLOSE SESSIONS` confirmation)

All actions invalidate public profile image cache for the affected user.

#### Profile Actions (`AdminProfileRequestHandler._apply_profile_action`)
1. **set-profile-disabled**: Set profile disabled (moderated/spam only)
2. **remove-profile-disabled**: Remove profile disabled status
3. **assign-role**: Assign role to profile (admin only)
4. **remove-role**: Remove role from profile (admin only)

#### Image Actions (`AdminImageRequestHandler._apply_image_action`)
1. **set-image-disabled**: Set image disabled (deleted/moderated/spam)
2. **remove-image-disabled**: Remove image disabled status

Image list supports: search by ID, filter by disabled reason, order by created/disabled dates, pagination via AJAX.

#### Input Validation
- IDs validated against `^[a-zA-Z0-9_-]+$` pattern, max 64 chars
- Disabled reasons validated against `Config.DISABLED` values
- LTOKEN checked against UTOKEN for all POST actions

#### Image Cache Invalidation
When user/profile status changes, the handler invalidates all cached public profile images via `Image().invalidate_all_public_profile_images_cache()`.

#### Access Control (`component-init.ntpl`)
On startup, evaluates `USER.profile_roles` for `admin`/`moderator`. If neither role is present, loads `access-false.json` which nullifies the admin menu entries in both session and drawer menus.

### Dependencies

- **Depends on**: `RequestHandler` core for base rendering
- **Depends on**: `constants` module for `DELETED`, `MODERATED`, `SPAM`, `UNCONFIRMED`, `UNVALIDATED`, `RBAC_DEFAULT_ROLES`
- **Depends on**: `core.image.Image` for image operations and cache invalidation
- **Depends on**: `utils.tokens.ltoken_check` for form token validation
- **Depends on**: `app.config.Config` for `DISABLED` reasons, `SECRET_KEY`
- **Depends on**: `app.extensions.require_header_set` for AJAX route protection
- **Depends on**: `http_errors` component for 404 rendering

## Data and Models

### Route Data (`data.json`)

| Route | title | description | h1 |
|-------|-------|-------------|-----|
| `/admin/` | Admin | Administration area | Admin |
| `/admin/help` | Help | Admin help and documentation | Help |
| `/admin/user` | Admin Users | User administration | Users |
| `/admin/profile` | Profiles Admin | Administer user profiles, roles, and status | Profiles |
| `/admin/image` | Admin Images | Administer uploaded images and image moderation status | Images |
| `/admin/post` | Admin Posts | Posts administration placeholder | Posts |

### Translations (`inherit.locale.trans`)

6 languages with admin section labels:

| Key | EN | ES | FR | DE | AR | ZH |
|-----|----|----|----|----|----|-----|
| Admin | — | Administrador | Administrateur | Administrator | مدير | 管理员 |
| Help | — | Ayuda | Aide | Hilfe | مساعدة | 帮助 |
| Users | — | Usuarios | Utilisateurs | Benutzer | المستخدمون | 用户 |
| Profiles | — | Perfiles | Profils | Profile | الملفات الشخصية | 个人资料 |
| Images | — | Imágenes | Images | Bilder | الصور | 图片 |
| Posts | — | Publicaciones | Publications | Beiträge | المنشورات | 帖子 |

### Session Menu (`data.current.menu["session:true"]`)

Menu entries for authenticated users with admin/moderator roles:

| Entry | Text | Link | Icon |
|-------|------|------|------|
| admin-home | Admin | `[:;data->admin_0yt2sa->manifest->route:]` | `x-icon-admin` |
| admin-users | Users | `[:;data->admin_0yt2sa->manifest->route:]/user` | `x-icon-user` |
| admin-profiles | Profiles | `[:;data->admin_0yt2sa->manifest->route:]/profile` | `x-icon-profile` |
| admin-images | Images | `[:;data->admin_0yt2sa->manifest->route:]/image` | `x-icon-images` |
| admin-posts | Posts | `[:;data->admin_0yt2sa->manifest->route:]/post` | `x-icon-edit` |
| admin-help | Help | `[:;data->admin_0yt2sa->manifest->route:]/help` | `x-icon-help` |

### Drawer Menu (`data.current.drawer.menu["session:true"]`)

| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| admin | Admin | admin | `x-icon-admin` |

### Access Denied State (`access-false.json`)

When the current user lacks admin/moderator roles, `component-init.ntpl` loads
`access-false.json` which sets both `session:true` menu entries and drawer menu
entries for `admin` to `null`, effectively removing them from navigation.

## Configuration

| Config Key | Purpose |
|------------|---------|
| `Config.DISABLED` | Dictionary mapping disabled reason names to integer codes (deleted, moderated, spam, unconfirmed, unvalidated) |
| `Config.SECRET_KEY` | Key for HMAC signing (used by ltoken) |

## Technical Rationale

- **Role-based action control**: Business logic enforces permissions in handler code, not just UI hiding. Moderators cannot bypass restrictions via direct POST.
- **LTOKEN validation**: All state-changing POST actions require a valid LTOKEN bound to the user's UTOKEN, preventing CSRF.
- **Input sanitization**: All IDs are validated against a strict pattern before database use, preventing injection.
- **Self-deletion prevention**: Admins cannot delete their own account, preventing accidental lockout.
- **Confirmation strings**: Destructive actions (delete user, close sessions) require typing a confirmation string, preventing accidental clicks.
- **Image cache invalidation**: When user/profile status changes, all cached public profile images are invalidated to ensure stale content is not served.
- **Access-false pattern**: Menu entries are conditionally removed via JSON data rather than template logic, keeping the UI declarative.
- **component-init.ntpl**: Uses `{:!eval; :}` to check roles at request time and conditionally load access-false data, enabling dynamic menu visibility.
- **AJAX image pagination**: The `/admin/image/ajax` route supports load-more pagination with `Requested-With-Ajax` header enforcement.
- **Post management placeholder**: The post section is a skeleton (`enabled: "true"` with no actions), intended for future implementation.

---

## Acceptance Criteria (SDD)

### Functional — User Management
- [x] `/admin/user` lists users with search, role filtering, and disabled status filtering
- [x] Admin can set/remove user disabled status with any valid reason
- [x] Moderator can only set/remove `unvalidated` and `moderated` reasons
- [x] Admin can delete users (requires `DELETE` confirmation, cannot self-delete)
- [x] Admin can close all user sessions (requires `CLOSE SESSIONS` confirmation)
- [x] Public profile image cache invalidated on user status changes

### Functional — Profile Management
- [x] `/admin/profile` lists profiles with search, role filtering, and disabled status filtering
- [x] Admin can set/remove profile disabled status (moderated/spam only)
- [x] Moderator can only set/remove `moderated` and `spam` reasons
- [x] Admin can assign/remove roles on profiles
- [x] Public profile image cache invalidated on profile status changes

### Functional — Image Management
- [x] `/admin/image` lists images with search, disabled filter, and ordering
- [x] Image list supports pagination via AJAX (`/admin/image/ajax`)
- [x] Admin can set/remove image disabled status (deleted/moderated/spam)
- [x] Moderator can only set/remove `moderated` and `spam` reasons
- [x] Exact image search by ID supported

### Functional — General
- [x] `/admin/` shows admin dashboard with current user roles
- [x] `/admin/help` shows technical documentation and policy placeholder
- [x] `/admin/post` renders post management placeholder
- [x] Session menu entries appear for admin/moderator users
- [x] Drawer menu entry appears for admin/moderator users
- [x] Menu entries removed when user lacks admin/moderator roles

### Technical
- [x] All routes require authentication and admin/moderator role
- [x] All POST actions require LTOKEN validation
- [x] Input IDs validated against `^[a-zA-Z0-9_-]+$` pattern, max 64 chars
- [x] Disabled reasons validated against `Config.DISABLED` values
- [x] Translations provided in 6 languages (EN, ES, FR, DE, AR, ZH)
- [x] Menu links use BIF `[:;data->admin_0yt2sa->manifest->route:]` for route resolution
- [x] Tests cover all routes and key actions

### Security
- [x] Role-based access enforced in handler code (not just UI)
- [x] Self-deletion prevention
- [x] Confirmation strings for destructive actions
- [x] CSRF protection via LTOKEN on all POST routes
- [x] AJAX route protected by `Requested-With-Ajax` header check
- [x] Input sanitization on all user-provided IDs and reasons

# Admin Component (`admin_0yt2sa`)

Role-based administration panel for user management.

## Routes

- Admin home.
- User administration.
- Post administration (Placeholder for future post administration.

## Access Model

- `dev` / `admin` (`can_full = true`)
  - Full visibility and full user operations.
- `moderator` (`can_moderate = true`, `can_full = false`)
  - Limited moderation view and limited status operations.
- Any other role / no role
  - Access denied (`403`).

## User Listing (`/admin/user`)

### Filters

- `search`
  - Exact match against `userId` or `login` hash.
- `role_filter`
  - Filter users by role code (`dev`, `admin`, `moderator`, `editor`).
- `disabled_filter`
  - Filter users by disabled reason code.
- `order`
  - `created`
  - `modified`
  - `role_date` (last role assignment timestamp)
  - `disabled_created_date` (last disabled record creation timestamp)
  - `disabled_modified_date` (last disabled record modification timestamp)

### Date Semantics

For `user_disabled` records:

- `created`: when the disabled record was first created.
- `modified`: updated when description/status is updated.

`upsert-disabled` preserves `created` and updates `modified` on update.

## Permissions by Action

### `dev` / `admin`

- View: full user card data (`User ID`, `Roles`, `Disabled`, `Alias`, `Locale`, `Email`, timestamps).
- Roles:
  - Assign role
  - Remove role
- Disabled:
  - Set any disabled reason
  - Remove any disabled reason
- Delete user:
  - Physical delete enabled
  - Requires explicit confirmation text: `DELETE`
  - UI warns this is an extreme action; preferred path is setting disabled status (`deleted`).

### `moderator`

- View:
  - `User ID`
  - `Roles` (read-only)
  - `Disabled` (read-only list)
  - `Alias`
  - `Locale`
  - timestamps
- Disabled operations allowed only for:
  - `unvalidated`
  - `moderated`
- `moderated` requires non-empty description.
- Not allowed:
  - Role assign/remove
  - User delete
  - Other disabled reasons (`deleted`, `unconfirmed`, `spam`, etc.)

## UX Behavior

- After successful role/disabled change, listing is focused to the target user by setting `search=<userId>`.
- Filters (`search`, `role_filter`, `disabled_filter`, `order`) are preserved across action forms.
- Responsive card layout is used in both mobile and desktop.

## Key Files

- Backend route/controller:
  - `src/component/cmp_7060_admin/route/routes.py`
- UI template:
  - `src/component/cmp_7060_admin/neutral/route/root/user/content-snippets.ntpl`
- SQL model queries:
  - `src/model/user.json`
- User service helpers:
  - `src/core/user.py`
- Component tests:
  - `src/component/cmp_7060_admin/tests/test_admin_component.py`

## Tests

Run:

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7060_admin
```

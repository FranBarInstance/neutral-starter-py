# Admin Component (`admin_0yt2sa`)

Role-based administration panel for managing users and their multiple profiles.

## Architecture: User vs Profile

The system follows a profile-centric model where a single **User** (global account, email, login) can manage multiple **Profiles** (identities, aliases, roles).

- **Users (`/admin/user`)**: Global account management. Focuses on identity, main email, and global account-level disabling.
- **Profiles (`/admin/profile`)**: specific identity management. Focuses on aliases, localized settings (locale/region), and profile-specific roles and statuses.

## Access Model

- **`dev` / `admin`** (`can_full = true`)
  - Full visibility and operations across users and profiles.
- **`moderator`** (`can_moderate = true`, `can_full = false`)
  - Can manage user statuses: `unvalidated` and `moderated`.
  - Can manage profile statuses: `moderated` and `spam`.
  - `moderated` status **requires** a description.
- **Any other role / no role**
  - Access denied (`403`).

## Sections

### Users (`/admin/user`)

Main list of global accounts.
- Shows associated **Profile IDs** with direct "Edit" links to the profile section.
- Allows global account searching by `userId`, `login` hash, or any associated profile `Alias`.
- Management of global **Roles** (consolidated from all profiles) and **User Disabled Status**.

### Profiles (`/admin/profile`)

Individual identity management.
- Shows specific data: `Alias`, `Locale`, `Region`.
- Management of **Profile Roles** and **Profile Status** (Disabled reasons).
- Direct link to the owner's **User ID** for global management.

## Filters and Ordering

Both sections support:
- `search`: IDs or Aliases.
- `role_filter`: Filter by specific role codes.
- `disabled_filter`: Filter by reason code.
- `order`:
  - `created`: Record creation date.
  - `modified`: Last modification date.
  - `role_date` (User only): Last role assignment.
  - `disabled_modified_date` (User only): Last status change.

## Permissions by Role

### `dev` / `admin`
- **Full View**: All IDs, roles, statuses, and metadata.
- **Roles**: Assign/Remove roles to users (resolved by exact `userId` to first profile) or specific profiles.
- **Statuses**: Set/Remove any disabled reason.
- **Safety Guards**:
  - Cannot remove own `dev`/`admin` role.
  - Cannot delete own user account.
- **Delete**: Physical user deletion for other users (requires `DELETE` confirmation).

### `moderator`
- **Limited View**: Access to IDs, roles, and statuses.
- **User Statuses**: Can only Set/Remove `unvalidated` or `moderated`.
- **Profile Statuses**: Can only Set/Remove `moderated` or `spam`.
- **Constraint**: `moderated` always requires a description.

## Technical Implementation Notes

- **Query Consolidation**: User-level searches automatically join and group profile data to avoid duplicates while allowing searches by alias.
- **Nested Data**: The `User._rows_to_dicts` helper automatically expands dot-separated SQL column names (e.g., `user_profile.alias`) into nested dictionaries, allowing templates to use `user->user_profile->alias` syntax.
- **Profile Roles**: Roles are physically stored in `profile_role`, linking them to specific identities rather than the global account.

## Key Files

- **Backend Dispatcher**: `src/component/cmp_7040_admin/route/dispatcher_admin.py`
- **User Service**: `src/core/user.py` (Methods: `admin_list_users`, `admin_list_profiles`).
- **SQL Queries**: `src/model/user.json`.
- **Templates**:
  - `src/component/cmp_7040_admin/neutral/route/root/user/content-snippets.ntpl`
  - `src/component/cmp_7040_admin/neutral/route/root/profile/content-snippets.ntpl`

## Tests

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7040_admin
```

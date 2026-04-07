# Admin Component (`admin_0yt2sa`)

Role-based administration panel for managing users, profiles, and images.

## Architecture: User vs Profile

The system follows a profile-centric model where a single **User** (global account, email, login) can manage multiple **Profiles** (identities, aliases, roles).

- **Users (`/admin/user`)**: Global account management. Focuses on identity, main email, and global account-level disabling.
- **Profiles (`/admin/profile`)**: specific identity management. Focuses on aliases, localized settings (locale/region), and profile-specific roles and statuses.

## Access Model

- **`admin`** (`can_full = true`)
  - Full visibility and operations across users, profiles, and images.
- **`moderator`** (`can_moderate = true`, `can_full = false`)
  - Can manage user statuses: `unvalidated` and `moderated`.
  - Can manage profile statuses: `moderated` and `spam`.
  - Can manage image statuses: `moderated` and `spam`.
  - `moderated` status **requires** a description.
- **Any other role / no role**
  - Access denied (`403`).

## Sections

### Users (`/admin/user`)

Main list of global accounts.
- Shows associated **Profile IDs** with direct "Edit" links to the profile section.
- Allows global account searching by `userId`, `login` hash, or any associated profile `Alias`.
- Shows user information and management of **User Disabled Status**.

### Profiles (`/admin/profile`)

Individual identity management.
- Shows specific data: `Alias`, `Locale`, `Region`.
- Management of **Profile Roles** and **Profile Status** (Disabled reasons).
- Direct link to the owner's **User ID** for global management.

### Images (`/admin/image`)

Uploaded image moderation and review.
- Lists uploaded images ordered by upload date, newest first by default.
- Can filter the list by one concrete creator profile through `profileId`.
- Shows the creator profile for each image.
- Allows management of **Image Status** using `deleted`, `moderated`, and `spam`.
- Direct links to the creator profile and creator user.

## Filters and Ordering

Administrative sections support filters according to the resource type. For example:
- `search`: IDs or Aliases.
- `filter_role`: Filter by specific role codes.
- `disabled_filter`: Filter by reason code.
- `order`:
  - `created`: Record creation date.
  - `modified`: Last modification date.
  - `role_date` (User only): Last role assignment.
  - `disabled_modified_date` (User only): Last status change.

Images additionally support:
- `search` by `imageId` or `profileId`
- ordering by upload date or status change date

## Permissions by Role

### `admin`
- **Full View**: All IDs, roles, statuses, and metadata.
- **Roles**: Assign/Remove roles only on specific profiles.
- **Statuses**: Set/Remove any disabled reason.
- **Image Statuses**: Set/Remove `deleted`, `moderated`, or `spam`.
- **Safety Guards**:
  - Cannot delete own user account.
  - Session closure and user deletion require explicit confirmation.
- **Sessions**: Can close all active sessions for a user in exceptional security cases.
- **Delete**: Physical user deletion for other users (requires `DELETE` confirmation).

### `moderator`
- **Limited View**: Access to IDs, roles, and statuses.
- **User Statuses**: Can only Set/Remove `unvalidated` or `moderated`.
- **Profile Statuses**: Can only Set/Remove `moderated` or `spam`.
- **Image Statuses**: Can only Set/Remove `moderated` or `spam`.
- **Constraint**: `moderated` always requires a description.

## Technical Implementation Notes

- **Query Consolidation**: User-level searches automatically join and group profile data to avoid duplicates while allowing searches by alias.
- **Nested Data**: The `User._rows_to_dicts` helper automatically expands dot-separated SQL column names (e.g., `user_profile.alias`) into nested dictionaries, allowing templates to use `user->user_profile->alias` syntax.
- **Profile Roles**: Roles are physically stored in `profile_role`, linking them to specific identities rather than the global account.
- **Image Moderation**: Image status is stored in `image_disabled`, using the same disabled-reason code family as other moderation areas.
- **Creator Resolution**: Image records are stored separately from user-profile data, so creator profile details are resolved in a second step from the user model.

## Key Files

- **Backend Dispatcher**: `src/component/cmp_7040_admin/route/dispatcher_admin.py`
- **User Service**: `src/core/user.py` (Methods: `admin_list_users`, `admin_list_profiles`).
- **Image Service**: `src/core/image.py` (Methods: `admin_list_images`, `set_image_disabled`, `delete_image_disabled`).
- **SQL Queries**: `src/model/user.json`.
- **Image SQL Queries**: `src/model/image.json`.
- **Templates**:
  - `src/component/cmp_7040_admin/neutral/route/root/user/content-snippets.ntpl`
  - `src/component/cmp_7040_admin/neutral/route/root/profile/content-snippets.ntpl`
  - `src/component/cmp_7040_admin/neutral/route/root/image/content-snippets.ntpl`

## Tests

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7040_admin
```

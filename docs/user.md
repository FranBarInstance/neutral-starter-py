# User Core Module (`src/core/user.py`)

The `User` class serves as the primary interface for all user-related operations in the application, including authentication, profile management, role assignment (RBAC), and administrative functions.

It uses `src/model/user.json` as its SQL query store and interfaces with the database via the `Model` class.

## Initialization

```python
from core.user import User
user_manager = User()
```

## Core Features

### 1. User Creation & Retrieval
- **`create(data: dict) -> dict`**: Creates a new user with the provided data (`email`, `password`, `birthdate`, `locale`, `alias`). Handles checking for existing users, creating IDs, storing hashed data, and generating a confirmation PIN.
- **`get_user(login: str) -> dict`**: Retrieves user profile data based on their login (email).
- **`get_runtime_user(user_id: str) -> dict`**: Loads the current authenticated user from the database to build the request context (runtime user data).
- **`get_main_email(user_id: str) -> str`**: Loads the current main active email for a user, abstracting local component queries into the core module.

### 2. Authentication & Security
- **`hash_login(email: str) -> str`**: Converts an email to a base64url SHA-256 hash.
- **`hash_password(password: str) -> bytes`**: Hashes a raw password using `bcrypt`.
- **`hash_birthdate(birthdate: str) -> str`**: Hashes a normalized birthdate timestamp using `bcrypt` to protect PII.
- **`check_login(login, password, pin) -> dict | None`**: Validates user credentials. If an unconfirmed user provides the correct PIN, it confirms the account and cleans up the strict disability reason. Returns the user's runtime data if successful.
- **`user_reminder(user_data) -> dict`**: Generates a new reminder token and PIN for an existing user.
- **`build_session_user_data(user_id) -> dict`**: Constructs a minimal payload (just the `userId`) intended for persistent sessions.

### 3. Modifying User Data & Profiles
- **`set_login(user_id: str, new_email: str) -> bool`**: Updates a user's login (hashes the new email and updates the `user` table).
- **`set_password(user_id: str, raw_password: str) -> bool`**: Hashes and updates a user's password.
- **`set_birthdate(user_id: str, raw_birthdate: str) -> bool`**: Hashes and updates a user's birthdate.
- **`update_profile(profile_id: str, data: dict) -> bool`**: Updates a user profile. It merges the new `properties` dictionary with the existing JSON `properties` in the database, while optionally updating the `alias`, `region`, and `locale`.

### 4. Role-Based Access Control (RBAC)
Roles are assigned on a **per-profile** basis, but the `User` class provides helpers to easily check and assign roles using the user's primary profile.
- **`get_roles(user_id) -> list[str]`**: Gets all role codes assigned to a user (across all profiles).
- **`get_roles_by_profile(profile_id) -> list[str]`**: Gets all role codes for a specific profile.
- **`has_role(user_id, role_code: str) -> bool`**: Checks if a user has a specific role.
- **`assign_role(user_id, role_code: str) -> bool`**: Assigns a role to a user's first profile.
- **`assign_role_to_profile(profile_id, role_code: str) -> bool`**: Idempotent assignment of a role directly to a profile ID.
- **`remove_role(user_id, role_code: str) -> bool`**: Removes a role from a user.
- **`remove_role_from_profile(profile_id, role_code: str) -> bool`**: Removes a role from a specific profile ID.

### 5. Administrative Methods & Moderation
The system uses "Disabled Reasons" (integer codes) to restrict or disable user accounts or specific profiles.
- **`set_user_disabled(user_id, reason: int, description: str = "") -> bool`**: Adds or updates a disable reason for a user account.
- **`delete_user_disabled(user_id, reason: int) -> bool`**: Lifts a particular restriction/disable reason from a user.
- **`set_profile_disabled(profile_id, reason: int, description: str = "") -> bool`**: Flags a specific profile as disabled.
- **`delete_profile_disabled(profile_id, reason: int) -> bool`**: Removes a disability reason from a profile.
- **`delete_user(user_id) -> bool`**: Completely deletes a user and cascades the deletion to their profiles, emails, roles, and PINs.
- **`admin_list_users(...) -> list[dict]`**: Retrieves a heavily paginated and optionally filtered list of users with details on their roles, profiles, and disabled statuses.
- **`admin_list_profiles(...) -> list[dict]`**: Retrieves a paginated and filtered list of user profiles.

## Database & Model Integration

Every method invokes self-contained SQL statements stored in `src/model/user.json` through the `self.model.exec(namespace, query_name, params)` API. This design keeps the Python codebase strictly focused on business logic and orchestration, while all SQL logic (portable across SQLite, MySQL, PostgreSQL) remains neatly organized and decoupled.

**Note on Component Integration:**
Local app components do not maintain their own private database SQL models for modifying core user information (such as profiles, login, or retrieving the main email). Instead, they are completely decoupled and consume the public methods of this centralized `User` core module.

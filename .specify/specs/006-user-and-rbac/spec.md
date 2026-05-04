# 006 - Users, Authentication, and RBAC System

## Executive Summary

This specification defines the identity, authentication, profile, and role
based access control (RBAC) system of Neutral Starter Py. It covers the full
user lifecycle: registration, authentication with bcrypt-hashed passwords,
user/profile separation, and dynamic role assignment.

The architecture separates **user** (credentials and authentication) from
**profile** (public identity), allowing flexible future support for multiple
profiles per account.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/000-core-system/spec.md` - session and request architecture.
- `specs/003-forms-standard/spec.md` - authentication and registration forms.
- `specs/005-image-system/spec.md` - profile image management.
- `src/core/user.py` - user system implementation.
- `src/model/user.json` - user model SQL definitions.
- `docs/user.md` - users and sessions documentation.

---

## 1. Goals

### 1.1 What this system must achieve

- identity creation, authentication, and account maintenance;
- secure password and temporary PIN storage;
- strict separation between credentials and public identity;
- flexible RBAC based on data-driven assignments, not hardcoded checks;
- account disabled states for `unconfirmed`, `unvalidated`, `deleted`,
  `moderated`, and `spam`.

### 1.2 Non-goals

- no OAuth or SAML integration;
- no built-in 2FA;
- no billing or subscription management.

---

## 2. Technical Contracts

### 2.1 Data model

#### Main tables

| Table | Purpose |
|-------|---------|
| `user` | Credentials and account timestamps |
| `user_profile` | Public identity and profile settings |
| `user_email` | One or more associated email addresses |
| `user_disabled` | Account disabled states |
| `pin` | Temporary verification and recovery codes |
| `role` | Available roles |
| `user_role` | User-to-role assignments |
| `profile_role` | Profile-to-role assignments |

#### `user` structure

| Field | Type | Description |
|-------|------|-------------|
| `userId` | VARCHAR(64) | User UUID (PK) |
| `login` | VARCHAR(256) | SHA256 hash of the login |
| `password` | VARCHAR(256) | bcrypt password hash |
| `birthdate` | VARCHAR(256) | Birthdate hash for recovery |
| `lasttime` | BIGINT | Last known activity |
| `created` | BIGINT | Account creation |
| `modified` | BIGINT | Last modification |

#### `user_profile` structure

| Field | Type | Description |
|-------|------|-------------|
| `profileId` | VARCHAR(64) | Profile UUID (PK) |
| `userId` | VARCHAR(64) | Reference to `user.userId` |
| `username` | VARCHAR(64) | Public unique username |
| `username_changed_at` | BIGINT | Last username change timestamp |
| `alias` | VARCHAR(128) | Display name or label |
| `locale` | VARCHAR(8) | Preferred language |
| `region` | VARCHAR(16) | Region or country code |
| `imageId` | VARCHAR(64) | Profile image reference |
| `properties` | TEXT | Extra JSON properties |
| `lasttime` | BIGINT | Last profile activity |
| `created` | BIGINT | Profile creation |
| `modified` | BIGINT | Last modification |

#### Disabled reasons

| Code | Constant | Description |
|------|----------|-------------|
| 1 | `DELETED` | Account moved to trash |
| 2 | `UNCONFIRMED` | Email not yet confirmed |
| 3 | `UNVALIDATED` | Pending admin validation |
| 4 | `MODERATED` | Moderated or suspended |
| 5 | `SPAM` | Marked as spam or abuse |

### 2.2 Normalization and validation

#### Username

- regex: `^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$`
- reserved words include `admin`, `root`, `user`, `api`, `app`, `support`,
  and similar system names;
- changes are rate-controlled using `username_changed_at`.

#### Email

- standard format validation;
- support for multiple emails per user;
- `main` flag for the primary address.

#### Passwords

- bcrypt with automatic salt;
- minimum length and complexity rules belong to form schema validation.

### 2.3 RBAC

#### Default roles

```python
RBAC_DEFAULT_ROLES = ["admin", "moderator", "editor", "user"]
```

#### Permission model

- roles assigned to a user are global to the user account;
- roles assigned to a profile apply to operations on that profile;
- authorization checks use `has_role(user_id, role_code)` or runtime
  `profile_roles`.

#### Authorization checks

| Function or source | Usage |
|--------------------|-------|
| `has_role(user_id, role_code)` | Check global user role |
| `_extract_roles(rows)` | Extract roles from joined query results |
| `routes_auth` in `manifest.json` | Mark routes that require authentication |
| `routes_role` in `manifest.json` | Mark routes that require a specific role |

### 2.4 `User` helper API

#### Authentication

| Method | Purpose |
|--------|---------|
| `check_password(password, hashed)` | Verify bcrypt hash |
| `hash_password(password)` | Create bcrypt hash |
| `hash_birthdate(birthdate)` | Create SHA256 recovery hash |
| `check_birthdate(birthdate, hashed)` | Verify birthdate hash |

#### User management

| Method | Purpose |
|--------|---------|
| `create(data)` | Create user, profile, email, and roles |
| `get_by_login(login)` | Fetch by hashed login |
| `get_by_id(user_id)` | Fetch by UUID |
| `exists(login)` | Check login uniqueness |
| `update(user_id, data)` | Update account data |
| `admin_delete_user(user_id)` | Full physical admin deletion |

#### Role management

| Method | Purpose |
|--------|---------|
| `assign_role_by_code(user_id, role_code)` | Assign role |
| `remove_role_by_code(user_id, role_code)` | Remove role |
| `has_role(user_id, role_code)` | Check role |
| `get_roles_by_userid(user_id)` | List user roles |

#### Account state management

| Method | Purpose |
|--------|---------|
| `set_disabled(user_id, reason, description)` | Add disabled state |
| `delete_disabled(user_id, reason)` | Remove disabled state |
| `is_active(user_data)` | Check whether the account is active |

#### PINs and verification

| Method | Purpose |
|--------|---------|
| `create_pin(target, user_id, expires)` | Create temporary PIN |
| `get_pin(pin)` | Validate PIN |
| `delete_pin(pin)` | Delete used PIN |

---

## 3. Behavior

### 3.1 Registration flow

1. validate form data, login availability, password, and optional birthdate;
2. generate UUIDs for user and profile;
3. hash login with SHA256, password with bcrypt, and birthdate with SHA256;
4. insert transactionally into `user`, `user_profile`, `user_email`, `pin`
   when applicable, and `user_role`;
5. return created user data without exposing hashes.

### 3.2 Authentication flow

1. fetch the user by hashed login;
2. compare bcrypt password hash;
3. ensure the account is not disabled;
4. build runtime user data including user, profile, roles, and disabled states;
5. create the session according to `000-core-system`.

### 3.3 Runtime user data

The runtime structure built by `_build_runtime_user_data()` has this shape:

```python
{
    "auth": True,
    "id": "user_uuid",
    "userId": "user_uuid",
    "created": "...",
    "lasttime": "...",
    "modified": "...",
    "profile_roles": {"admin": "admin", "user": "user"},
    "user_disabled": {},
    "profile_disabled": {},
    "profile": {
        "id": "profile_uuid",
        "userId": "user_uuid",
        "username": "username",
        "username_changed_at": "...",
        "imageId": "...",
        "alias": "...",
        "locale": "es",
        "region": "ES",
        "properties": {},
        "lasttime": "...",
        "created": "...",
        "modified": "..."
    }
}
```

---

## 4. Security

### 4.1 Security controls

- [x] passwords are always stored as bcrypt hashes;
- [x] logins are stored as SHA256 hashes to avoid exposing raw logins in the
  database;
- [x] rate limiting is required on login, registration, and recovery routes;
- [x] reserved usernames prevent system impersonation;
- [x] PINs are temporary and single-use;
- [x] disabled states support multiple reasons.

### 4.2 Risks and mitigations

| Risk | Mitigation | Level |
|------|------------|-------|
| Password brute force | Rate limiting and slow bcrypt hashing | High |
| User enumeration | Hashed logins and generic error messages | Medium |
| System-name impersonation | Reserved username list | High |
| Timing attacks | bcrypt constant-time verification | Medium |

---

## 5. Implementation and Deployment

### 5.1 Dependencies

- `bcrypt`
- `regex`
- `sqlalchemy`
- `json`

### 5.2 Configuration constants

```python
USER_EXISTS = 1
DELETED = 1
RBAC_DEFAULT_ROLES = ["admin", "moderator", "editor", "user"]

DISABLED_KEY = {
    "1": "deleted",
    "2": "unconfirmed",
    "3": "unvalidated",
    "4": "moderated",
    "5": "spam",
}
```

---

## 6. Testing

### 6.1 Required test cases

- [ ] user creation hashes password and login correctly;
- [ ] successful authentication returns full runtime user data;
- [ ] failed authentication does not reveal whether the user exists;
- [ ] disabled users cannot authenticate;
- [ ] username changes update `username_changed_at`;
- [ ] role assignment is reflected immediately in authorization checks;
- [ ] physical admin deletion cleans all related tables.

---

## 7. Acceptance Criteria

- [x] registration creates all required entities transactionally;
- [x] passwords are never stored in plaintext;
- [x] logins remain searchable without exposing the original value;
- [x] RBAC supports role assignment and verification;
- [x] disabled states support multiple reasons and recovery;
- [x] temporary PINs work for verification and recovery flows.

---

## 8. Impact and Dependencies

### 8.1 Dependent components

| Component | Usage |
|-----------|-------|
| `cmp_5100_sign` | Registration, login, logout, recovery |
| `cmp_5000_user` | Profile, email, and role management |
| `cmp_0250_forms` | User-form snippets |
| `cmp_5300_image` | Profile avatar |

---

## 9. Decisions and Risks

### 9.1 Architectural decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| User/profile separation | Future support for multiple profiles per user | More complexity, more flexibility |
| Login stored as SHA256 | Protect the raw login value | The original login cannot be recovered from the DB |
| bcrypt for passwords | Industry standard | Intentionally slow against brute-force attacks |

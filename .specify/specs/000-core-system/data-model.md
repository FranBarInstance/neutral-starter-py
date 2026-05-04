# Core Data Model: Neutral Starter Py

## Summary

Neutral Starter Py uses declarative persistence: SQL operations are defined in
JSON files and executed through `core.model.Model` on top of SQLAlchemy. Python
code must select operations by stable name and pass named parameters. Business
SQL must not be embedded directly in handlers, routes, or services.

This document describes the core databases, persisted entities, JSON model
contracts, centralized configuration data, and the rules that component models
must follow when they extend persistence.

## Databases

The core distinguishes three main connections:

| Connection | Config | Responsibility |
|---|---|---|
| PWA | `DB_PWA_*` | Users, profiles, emails, roles, PINs, disabled states, and distributed UID registry. |
| Safe | `DB_SAFE_*` | Normal user sessions. |
| Image | `DB_IMAGE_*` | Images and image lifecycle state. |

Rules:

- every connection must declare engine type plus either a local SQLite path or
  the credentials required by the chosen SQLAlchemy URL;
- `AUTO_BOOTSTRAP_DB=true` triggers `setup-*` operations for shared structures;
- components may use their own model directories via `model_dir` and should not
  pollute shared model namespaces.

## Declarative `Model` Engine

### Initialization

`Model(db_url, db_type)` creates a SQLAlchemy engine bound to the configured
database type.

Per-instance error state:

- `last_error`
- `user_error`
- `has_error`
- `error_code`

`get_last_error()` must return a safe structured payload. In debug mode it may
include more technical detail.

### JSON model files

Every model file uses this structure:

```json
{
    "operation-name": {
        "@portable": "SELECT 1",
        "@sqlite": "@portable",
        "@mysql": "SELECT 1"
    }
}
```

Rules:

- outer keys are stable operation names;
- inner keys are dialect selectors beginning with `@`;
- `@portable` is the default fallback;
- a dialect may alias another dialect by string reference;
- the final resolved value may be a single SQL string or an array of SQL
  strings;
- arrays execute atomically within a transaction;
- placeholders use named binds such as `:userId`;
- missing operations must return `OPERATION_NOT_FOUND`;
- missing or invalid JSON must raise a configuration-level error.

### Result contract

For `SELECT`:

- `success`
- `operation`
- `columns`
- `rows`
- `rowcount`

For `INSERT`, `UPDATE`, and `DELETE`:

- `success`
- `operation`
- `rowcount`
- `lastrowid` when applicable

For multi-step transactions, the result may include per-statement information
including `statement_index`.

## `app.json`

### Responsibility

`app.json` defines shared PWA-database infrastructure, currently focused on
distributed UID reservation and minimal health-check operations.

### `uid` table

| Field | Logical type | Rules |
|---|---|---|
| `uid` | string or numeric identifier | Primary key, globally unique. |
| `target` | string | Logical entity target. |
| `created` | int timestamp | Creation time. |

### Operations

| Operation | Usage |
|---|---|
| `setup-base` | Create the `uid` table. |
| `sentence-example` | Minimal dialect health-check statement. |
| `uid-create` | Reserve a UID for a target. |

### UID generation

`Model.create_uid(target, attempts=10)` must:

1. generate a random value between `UUID_MIN` and `UUID_MAX`;
2. try to insert it into `uid`;
3. retry until success or until attempts are exhausted;
4. return the reserved UID or `None`.

## `session.json`

### Responsibility

`session.json` lives in the Safe database and controls normal user sessions.

### `session` table

| Field | Logical type | Rules |
|---|---|---|
| `sessionId` | string | Primary key. Generated with `secrets.token_urlsafe`. |
| `open` | bool | `1` active, `0` closed. |
| `userId` | string | Session owner. |
| `ua` | string | User-Agent or client identifier. |
| `properties` | JSON text | Auxiliary session data, default `{}`. |
| `modified` | int timestamp | Last renewal. |
| `created` | int timestamp | Creation time. |
| `expire` | int timestamp | Inactivity expiration. |

Indexes:

- `idx_session_userId`
- `idx_session_expire`

### Operations

| Operation | Usage |
|---|---|
| `setup-base` | Create table and indexes. |
| `get` | Fetch an open, non-expired session. |
| `create` | Insert a new session. |
| `close` | Close one session. |
| `close-by-userid` | Close all active sessions for a user. |
| `update` | Renew `modified` and `expire`. |
| `delete` | Remove one session. |

### Runtime contract

`Session.get()` must:

- read the `SESSION` cookie;
- find an open and non-expired session;
- return `(None, {})` when the session is missing or expired;
- renew expiry and cookie state when the session is stale enough to require
  refresh;
- return a secure cookie definition for valid sessions.

Session cookies must use:

- `HttpOnly: true`
- `Secure: true`
- `SameSite: Lax`

`Session.get_session_properties()` must parse `properties` as JSON and return
`{}` on invalid JSON.

## `user.json`

### Responsibility

`user.json` lives in the PWA database. It defines users, profiles, emails,
PINs, restrictive states, reserved usernames, and RBAC data.

### Main tables

| Table | Purpose |
|---|---|
| `user` | Credentials and account timestamps |
| `user_profile` | Public identity and user-facing settings |
| `user_email` | One or more associated email addresses |
| `pin` | Temporary verification and recovery codes |
| `user_disabled` | Account disabled states |
| `profile_role` / `user_role` / `role` | RBAC structures |
| `username_blacklist` | Reserved or forbidden usernames |

### Core field expectations

- `user.password` stores a hash, never plaintext;
- `user.login` is stable and queryable according to the user subsystem
  contract;
- `user_profile.username` is unique when present;
- `user_profile.locale` stores the preferred language;
- `user_profile.imageId` is a logical image reference;
- `pin` entries must support expiration and one-time invalidation;
- disabled-state tables must allow multiple reasons.

### Setup, read, and write operations

The model must provide:

- `setup-*` operations for the shared user system;
- lookup operations by login, user ID, username, and PIN;
- insert/update flows for users, profiles, emails, roles, and disabled states;
- administrative delete and moderation support.

## Centralized Configuration: `config/config.db`

### Responsibility

The configuration database provides mutable runtime overrides that do not
require editing the versioned component package.

### `custom` table

| Field | Purpose |
|---|---|
| component UUID | Target component |
| payload | Override blob |
| enabled flag | Whether the override is active |
| timestamps | Auditability |

### Payload

The payload may override:

- manifest-level mutable configuration;
- schema-level inheritable values;
- operator-managed runtime settings.

It must never be treated as a secret store for values that should live in the
environment.

## Global Runtime Schema

### Main sections

The runtime schema is composed from:

- static `data`;
- mutable `inherit.data`;
- locale data;
- component metadata;
- request-local context injected during request preparation.

### Context data

Per-request schema state typically includes:

- `CONTEXT` for GET, POST, headers, cookies, and environment;
- session and runtime user information;
- current route paths and template provider paths;
- CSP nonce and security-related values.

### Current component data

The core also keeps enough metadata to identify the active component by UUID,
derive route-relative paths, and resolve provider contracts such as the active
layout or mail-template provider.

## Tokens and Cookies

### Core cookies

Important cookie categories include:

- standard session cookies;
- development admin cookies for `SessionDev`;
- locale or preference cookies where configured.

### Token rules

The core must support the token families required by request handling and forms,
including LTOKEN, CSRF-related state, and form anti-bot tokens when a form flow
requires them.

## Image Models

Image persistence is isolated in the Image database and described in
specification 005. The core only defines the shared persistence mechanism and
connection strategy.

## Component Models

### Location

Components may ship additional model files under their own `model/`
directories.

### Execution

Components must execute their own JSON model files explicitly via
`model.exec(..., model_dir=component_path)`.

## Migrations and Evolution

The system favors explicit setup operations over automatic versioned migrations.
Schema evolution must be documented in the relevant spec and implemented
through deterministic setup or operator-controlled migration steps.

## Data Security

- secrets do not belong in versioned JSON config;
- SQL parameters must always be bound, never concatenated;
- user-facing errors must remain sanitized;
- runtime schema dumps must not expose unnecessary secret material.

## Acceptance Criteria

- [x] core persistence is declarative;
- [x] shared databases are separated by responsibility;
- [x] session and user contracts are supported through JSON model files;
- [x] centralized overrides are possible through `config/config.db`;
- [x] components can isolate their own models without breaking the core.

# 007 - Data Modeling and Persistence System

## Executive Summary

This specification defines the declarative data modeling system used by Neutral
Starter Py. Database schemas, SQL queries, and persistence operations are
defined in JSON files, keeping raw SQL out of Python business logic.

The JSON-over-SQL pattern provides portability across SQLite, PostgreSQL, and
MySQL/MariaDB while keeping queries centralized for auditing, optimization, and
migration work.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/000-core-system/spec.md` - core architecture and `PreparedRequest`.
- `specs/006-user-and-rbac/spec.md` - user data model.
- `src/core/model.py` - `Model` implementation.
- `docs/model.md` - modeling system documentation.
- `src/model/*.json` - system SQL definitions.

---

## 1. Goals

### 1.1 What this system must achieve

- declarative SQL definitions in JSON instead of Python code;
- multi-engine portability using explicit dialect variants;
- atomic multi-step operations through transaction arrays;
- component isolation, allowing each component to ship its own `model/`;
- distributed UID generation without centralized coordination.

### 1.2 Non-goals

- no traditional ORM mapping;
- no automatic versioned migrations;
- no database replication or sharding management.

---

## 2. Technical Contracts

### 2.1 System architecture

```text
Python code (handlers)
    ↓
Model.exec(target, operation, params, model_dir)
    ↓
Load JSON: {model_dir}/{target}.json
    ↓
Resolve dialect: @portable → engine-specific variant
    ↓
SQLAlchemy + text() execution
    ↓
Result dict: {success, rows, columns, operation}
```

### 2.2 JSON definition format

#### Base structure

```json
{
    "operation-name": {
        "@portable": "STANDARD SQL STATEMENT",
        "@mysql": "MYSQL SPECIFIC STATEMENT",
        "@postgresql": "@portable",
        "@sqlite": "@portable",
        "@mariadb": "@mysql"
    }
}
```

#### Positional parameters

Parameters use `:name` placeholders and are bound through SQLAlchemy `text()`:

```json
{
    "get-by-id": {
        "@portable": "SELECT * FROM user WHERE userId = :userId"
    }
}
```

#### Multi-step transactions

Atomic operations are defined as arrays:

```json
{
    "create-complex": {
        "@portable": [
            "INSERT INTO user (userId, login) VALUES (:userId, :login)",
            "INSERT INTO user_profile (profileId, userId) VALUES (:profileId, :userId)",
            "INSERT INTO user_email (email, userId) VALUES (:email, :userId)"
        ]
    }
}
```

If any statement fails, the entire transaction must roll back.

### 2.3 Supported dialects

| Dialect | Identifier | Notes |
|---------|------------|-------|
| Standard SQL | `@portable` | Default, SQLite-compatible baseline |
| MySQL | `@mysql` | `LONGBLOB`, `ON DUPLICATE KEY`, and similar features |
| MariaDB | `@mariadb` | Usually inherits from `@mysql` |
| PostgreSQL | `@postgresql` | `BYTEA`, `ON CONFLICT`, and similar features |
| SQLite | `@sqlite` | Dynamic types and SQLite-specific behavior |

### 2.4 `Model` API

#### Constructor

```python
Model(db_url: str, db_type: str)
```

#### Main method

```python
def exec(
    self,
    target: str,
    operation: str,
    params: dict,
    model_dir: str = None
) -> dict
```

#### Standard response

```python
{
    "success": True,
    "operation": "SELECT",
    "columns": ["col1", "col2"],
    "rows": [[val1, val2]],
    "rowcount": 1,
    "lastrowid": 123
}
```

#### Error management

```python
model.has_error
model.error_code
model.user_error
model.last_error
model.get_last_error()
model.clear_error()
```

### 2.5 Distributed UID generation

```python
def create_uid(self, target: str, attempts: int = 10) -> Optional[int]
```

- generates random IDs inside the configured range;
- verifies global uniqueness through the `uid` table;
- retries on collisions.

---

## 3. Behavior

### 3.1 Execution flow

1. resolve the JSON file as `{model_dir}/{target}.json`;
2. load and parse JSON into the operation map;
3. resolve the effective dialect from `db_type`;
4. bind `:params` through SQLAlchemy `text()`;
5. execute statements;
6. commit or roll back atomic multi-step operations;
7. return a standardized response dict.

### 3.2 Naming conventions

#### Operations

| Prefix | Usage | Example |
|--------|-------|---------|
| `get-` | Fetch one or more records | `get-by-id`, `get-by-email` |
| `list-` | Filtered listings | `list-by-profile`, `list-all` |
| `create` / `insert` | Insert data | `create`, `insert` |
| `update` | Update data | `update-profile` |
| `delete` | Physical delete | `delete-by-id` |
| `setup-` | Table and index creation | `setup-base`, `setup-rbac` |
| `admin-` | Administrative operations | `admin-list`, `admin-delete` |
| `count-` | Count queries | `count-by-profile` |
| `upsert-` | Insert-or-update operations | `upsert-disabled` |

#### System tables

| Table | Purpose |
|-------|---------|
| `uid` | Distributed unique ID generation |
| `session` | User session management |
| `user` + `user_*` | User system |
| `image` + `image_disabled` | Image system |

---

## 4. Security

### 4.1 Security controls

- [x] SQL injection protection through SQLAlchemy bind parameters;
- [x] atomic transactions for multi-step operations;
- [x] separated user-facing and technical error messages.

### 4.2 Risks and mitigations

| Risk | Mitigation | Level |
|------|------------|-------|
| Injection caused by incorrect JSON SQL | Code review and tests | High |
| Sensitive data exposed in logs | Separate `user_error` and `last_error` | Medium |
| UID race conditions | Retry strategy | Low |

---

## 5. Implementation and Deployment

### 5.1 Models in components

Components may ship their own models under `src/component/.../model/`.

#### Option 1: custom directory (recommended)

```python
component_path = self.schema["data"][UUID]["path"]
custom_model_dir = os.path.join(component_path, "model")
result = model.exec("my_queries", "operation", {}, model_dir=custom_model_dir)
```

#### Option 2: copy into the global model directory (legacy)

```python
shutil.copy2(src_json, os.path.join(Config.MODEL_DIR, filename))
```

### 5.2 Naming conventions in components

- files: `{component}_queries.json`, `{component}_data.json`;
- operations: `{comp}-get-items`, `{comp}-insert-log`.

---

## 6. Testing

### 6.1 Required test cases

- [ ] simple `SELECT` operations return the expected structure;
- [ ] multi-step transactions roll back atomically on partial failure;
- [ ] the correct dialect is selected for each `db_type`;
- [ ] parameters are safely escaped and bound;
- [ ] UID generation remains unique under simulated concurrency;
- [ ] errors populate `has_error`, `error_code`, and `user_error`.

---

## 7. Acceptance Criteria

- [x] SQL lives in JSON, not Python business logic;
- [x] SQLite, PostgreSQL, and MySQL/MariaDB are supported;
- [x] multi-step operations are atomic;
- [x] components may isolate their own models;
- [x] distributed UID generation works without collisions;
- [x] error handling distinguishes technical and user-facing failures.

---

## 8. Impact and Dependencies

### 8.1 Dependent systems

| System | Usage |
|--------|-------|
| `006-user-and-rbac` | All user operations |
| `005-image-system` | Image storage and retrieval |
| `000-core-system` | Sessions and configuration |
| All components | Data persistence |

---

## 9. Decisions and Risks

### 9.1 Architectural decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| JSON-over-SQL instead of ORM | More SQL control and portability | Less abstraction, more verbosity |
| No automatic migrations | Simplicity and manual control | Setup requires more care |
| Distributed UIDs instead of sequential IDs | Cross-engine portability | Collisions remain possible but managed |

### 9.2 Technical debt

- versioned migrations are not implemented yet;
- current setup flows still depend on explicit table creation.

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **Target** | JSON file name that contains operations |
| **Operation** | Query key inside the JSON file |
| **Dialect** | Engine-specific SQL variant |
| **Portable** | Standard SQL shared across engines |

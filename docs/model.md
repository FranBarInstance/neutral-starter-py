# Data Model Documentation

This application uses a custom database abstraction layer that separates SQL logic from Python code. The system is based on JSON definition files located in `src/model/` and a central executor in `src/core/model.py`.

## Architecture

Data access is managed through the `Model` class (`src/core/model.py`). This class does not contain "hardcoded" SQL queries; instead, it loads queries dynamically from JSON files.

### File Locations

- **Logic (Python):** `src/core/model.py`
- **Definitions (JSON):** `src/model/*.json`

## Query Definition (JSON)

Each JSON file in `src/model` represents a logical set of operations (e.g., `user.json` for user operations).

### JSON Structure

```json
{
    "operation-name": {
        "@portable": "STANDARD SQL STATEMENT",
        "@mysql": "MYSQL SPECIFIC STATEMENT",
        "@postgresql": "@portable",
        "@sqlite": "@portable"
    }
}
```

- **Operation Keys:** Identify the query (e.g., `create`, `get-by-id`).
- **Dialects:**
  - `@portable`: Standard SQL compatible with most engines (or the default).
  - `@mysql`, `@postgresql`, `@sqlite`: Specific versions if syntax varies.
  - References can be used (e.g., `"@mariadb": "@mysql"`).

### Transactions

If an operation requires multiple atomic steps, it can be defined as a list of strings. The system will execute them within a single database transaction.

```json
{
    "create-complex": {
        "@portable": [
            "INSERT INTO table1 ...",
            "INSERT INTO table2 ...",
            "UPDATE table3 ..."
        ]
    }
}
```

## Usage in Code

To execute a query from Python:

```python
# Example: Execute the 'get-by-login' query from the 'user.json' file
result = self.exec("user", "get-by-login", {"login": "user1"})
```

- **First argument:** Name of the JSON file (without extension).
- **Second argument:** Key of the operation within the JSON.
- **Third argument:** Dictionary of parameters (mapped to `:parameter` in the SQL).
- **Fourth argument (optional):** Custom directory path where the JSON file is located (overrides `Config.MODEL_DIR`).

## Defined Models

Below are the models and tables identified in the current system.

### 1. System (`app.json`)
General utility operations for the application.

- **Tables:**
  - `uid`: Table for distributed unique identifier generation.
- **Operations:**
  - `uid-create`: Inserts and generates a new unique ID.

### 2. Session (`session.json`)
User session management.

- **Tables:**
  - `session`: Stores information on active and expired sessions.
- **Operations:**
  - `get`: Retrieve session by ID.
  - `create`: Create new session.
  - `close`: Close session (mark as closed).
  - `update`: Update modification/expiration timestamp.
  - `delete`: Physically delete session.

### 3. User (`user.json`)
Complete management of users, profiles, and authentication.

- **Tables:**
  - `user`: Main credential data (login, password, dates).
  - `user_profile`: Extended profile data (alias, locale, region).
  - `user_disabled`: Record of user blocks or disables.
  - `user_email`: Associated email addresses.
  - `pin`: Temporary codes (PINs) and validation tokens.
  - `role`: Catalog of available roles.
  - `user_role`: User-role assignments (many-to-many).
- **Operations:**
  - `setup-rbac`: Creates role tables if missing for standard RBAC roles (for example `admin`, `moderator`, `editor`).
  - `assign-role-by-code`, `remove-role-by-code`: Assign/remove role by role code.
  - `has-role`, `get-roles-by-userid`: Role checks and role listing.
  - `admin-list-by-created`, `admin-list-by-modified`: User listings with filter by `userId` or login hash.
  - `admin-get-disabled-by-userid`: List disabled states and descriptions for a user.
  - `upsert-disabled`: Add/update a disabled reason for a user.
  - `admin-delete-user`: Full user deletion (cascading DB cleanup).
  - `get-by-login`: Retrieves user data joining `user`, `user_profile`, and `user_disabled` tables.
  - `check-exists`: Checks if a login already exists.
  - `create`: Complex transaction that inserts into `user`, `user_profile`, `user_email`, `user_disabled`, and `pin` simultaneously.
  - `insert-pin`: Inserts or updates a PIN (Uses `ON CONFLICT`/`ON DUPLICATE KEY`).
  - `get-pin`, `get-pin-by-token`, `delete-pin`: Security PIN management.

### Disabled Status Codes

Disabled user states are currently code-driven from application constants/config:

- `deleted`
- `unconfirmed`
- `unvalidated`
- `moderated`
- `spam`

## Component SQL Files

Components can include their own SQL definition files within their directory structure. This keeps database operations self-contained and isolated within the component.

### Location for Component SQL Files

Create a `model/` directory inside your component:

```
src/component/cmp_NNNN_name/
├── model/                                # Component SQL definitions
│   └── component_queries.json            # JSON file with SQL operations
├── route/
├── neutral/
└── ...
```

### File Format

Component SQL files use the same JSON format as the global model files in `src/model/`:

```json
{
    "operation-name": {
        "@portable": "SELECT * FROM table WHERE id = :id",
        "@mysql": "MYSQL SPECIFIC STATEMENT",
        "@postgresql": "@portable",
        "@sqlite": "@portable"
    }
}
```

### Registration and Execution

The component's SQL files are **not automatically loaded**. You have three options:

#### Option 1: Copy to Global Model Directory

In your component's `__init__.py`, copy the JSON file to the global model directory:

```python
import os
import shutil
from app.config import Config

def init_component(component, component_schema, _schema):
    """Initialize component and register SQL files."""
    component_path = component["path"]
    model_dir = os.path.join(component_path, "model")

    # Copy SQL definition files to global model directory
    if os.path.exists(model_dir):
        for filename in os.listdir(model_dir):
            if filename.endswith('.json'):
                src = os.path.join(model_dir, filename)
                dst = os.path.join(Config.MODEL_DIR, filename)
                shutil.copy2(src, dst)
```

#### Option 2: Execute using Custom Directory Path (Best Choice)

Since the `exec()` method supports an optional `model_dir` parameter, you can execute component-specific queries directly by providing the path to your component's model folder:

```python
import os
from core.model import Model
from app.config import Config

# Inside your route or handler:
# 1. Get the component path (usually available in blueprint or schema)
component_path = self.schema['data'][UUID]['path']
custom_model_dir = os.path.join(component_path, "model")

# 2. Execute passing the custom directory
result = model.exec("component_queries", "get-items", {}, model_dir=custom_model_dir)
```

#### Option 3: Execute SQL Directly from Component (Legacy/Specific Use)

> [!CAUTION]
> **Not Recommended for Redistribution.** Using embedded SQL strings in Python code makes your component harder to maintain and less portable across different database engines.

For very specific internal operations where a JSON file is not practical, you can execute SQL directly:

```python
from core.model import Model
from app.config import Config

def init_component(component, component_schema, _schema):
    """Initialize component and setup database tables."""
    # Get database configuration
    db_config = Config.DB_PWA

    # Create model instance
    model = Model(db_config["url"], db_config["type"])

    # Example: Execute SQL directly (Avoid this for business logic!)
    sql = """
        CREATE TABLE IF NOT EXISTS my_component_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """
    result = model._execute_single(sql)
```

### Naming Conventions

- Use descriptive filenames that reflect the component's purpose (e.g., `mycomponent_user.json`, `mycomponent_logs.json`)
- Prefix operation names with the component name to avoid conflicts (e.g., `mycomp-get-users` instead of just `get-users`)
- Consider using the component's UUID in operation names for guaranteed uniqueness

### Example Component Structure

```
src/component/cmp_7000_mycomponent/
├── manifest.json
├── schema.json
├── __init__.py                           # Contains init_component for SQL registration
├── model/
│   └── mycomponent_data.json             # SQL operations
├── route/
│   ├── __init__.py
│   ├── routes.py                         # Uses: model.exec("mycomponent_data", "get-items", {})
│   └── handler.py
└── neutral/
    └── route/
        └── root/
            └── content-snippets.ntpl
```

### Best Practices

1. **Isolation**: Keep all SQL operations related to your component within the component's `model/` directory.
2. **Avoid Embedded SQL**: **Never** embed SQL strings directly in your Python code for business logic or queries. Always use JSON model files. Even for `CREATE TABLE` and setup operations, using JSON files is preferred as it allows you to provide different dialects (e.g., `@mysql` vs `@sqlite`).
3. **Redistribution**: If you plan to share your component, using JSON model files with `@portable` or multiple dialect support is **mandatory** to ensure it works on any system.
4. **Setup Operations**: Use `setup-*` operations for creating tables and initial data, and call them using `model.exec(..., model_dir=...)` during initialization.
5. **Transactions**: Use transaction arrays in JSON for multi-step operations that must be atomic.
6. **Error Handling**: Always check `model.has_error` after executing operations.
7. **Cleanup**: If your component is removed, ensure there is a way to clean up its database tables.

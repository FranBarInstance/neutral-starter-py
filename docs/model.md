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
- **Operations:**
  - `get-by-login`: Retrieves user data joining `user`, `user_profile`, and `user_disabled` tables.
  - `check-exists`: Checks if a login already exists.
  - `create`: Complex transaction that inserts into `user`, `user_profile`, `user_email`, `user_disabled`, and `pin` simultaneously.
  - `insert-pin`: Inserts or updates a PIN (Uses `ON CONFLICT`/`ON DUPLICATE KEY`).
  - `get-pin`, `get-pin-by-token`, `delete-pin`: Security PIN management.

# Neutral PWA Starter - Developer Guide

This document is a comprehensive guide for developers looking to understand, extend, and maintain the Neutral PWA Starter application. It covers high-level architecture, core concepts, and detailed implementation workflows.

---

## 1. Architectural Overview

The application is designed around **modularity, security, and separation of concerns**.

### Core Philosophy
1.  **Everything is a Component**: The feature set is built entirely from components (`src/component/`). Even core features like the template engine or themes are components.
2.  **Neutral Template Library (NTPL)**: A language-agnostic, secure-by-default logic-less templating engine handles the frontend.
3.  **Declarative SQL**: Database interactions are defined in JSON files, keeping Python code free of hardcoded SQL strings and allowing for database portability.
4.  **Dispatcher Pattern**: A central `Dispatcher` class mediates between Flask (HTTP handling) and NTPL (View rendering), ensuring consistent security and context setup.

### The Stack
*   **Backend**: Python, Flask (Routing/WSGI).
*   **Database**: SQL (SQLite/PostgreSQL/MySQL) via the `Model` abstraction.
*   **Frontend**: HTML5/CSS3 (Vanilla), Neutral Templates (`.ntpl`).
*   **Security**: Custom Token System (`UTOKEN`, `LTOKEN`), robust Session management, CSP.

---

## 2. Project Structure

```
root/
├── docs/                   # Documentation
├── src/
│   ├── app/                # Application Factory & Configuration
│   │   ├── components.py   # Component Loader Logic
│   │   ├── config.py       # Global Config (Paths, Secrets)
│   │   └── ...
│   ├── component/          # MODULES LIVE HERE
│   │   ├── cmp_0200_template/ # The base layout/theme engine
│   │   ├── cmp_5100_sign/     # Example: Auth system (Login/Register)
│   │   └── cmp_7000_hellocomp/# Example: Minimal component
│   ├── core/               # Framework Core Logic
│   │   ├── dispatcher.py   # Request Controller Base
│   │   ├── model.py        # Database Executor
│   │   ├── template.py     # NTPL Integration
│   │   └── session.py      # Session Handler
│   ├── model/              # SQL Definitions (JSON)
│   └── neutral/            # Global Templates (if any)
└── ...
```

---

## 3. Core Concepts

### 3.1 Component System
Components are loaded alphabetically based on their folder name (`cmp_NNNN_name`).
*   **Precedence**: A component loaded later can override parts of an earlier component (schemas, translations, templates).
*   **Anatomy of a Component**:
    *   `manifest.json`: Registration info (UUID, Name, Route).
    *   `schema.json`: Configuration data (menus, constants, translations).
    *   `custom.json`: *Local-only* overrides (never committed to git).
    *   `route/`: Python backend logic (Blueprints, Dispatchers).
    *   `neutral/`: Frontend templates (`.ntpl`).

### 3.2 The Request Pipeline
1.  **Flask Route**: Receives HTTP request.
    ```python
    @bp.route("/")
    def index():
        dispatch = DispatcherHello(request, "", bp.neutral_route)
        return dispatch.view.render()
    ```
2.  **Dispatcher**:
    *   Initializes `Session` and `User`.
    *   Validates/Generates Security Tokens (`UTOKEN`).
    *   Prepares `CONTEXT` for the template (POST/GET data, Headers).
3.  **Business Logic**:
    *   Dispatcher calls `Model` to fetch data.
    *   Data is injected into `Generic View` or `Schema`.
4.  **Template Rendering**:
    *   `Template` class renders the `index.ntpl` (usually from `cmp_0200_template`).
    *   `index.ntpl` dynamically includes the component's `content-snippets.ntpl`.

### 3.3 Data Layer (Model)
SQL is defined in JSON files in `src/model/`.
*   **File**: `src/model/user.json`
*   **Execution**: `self.model.exec("user", "get-by-login", {"login": "..."})`
*   **Transactions**: Supports atomic transactions by defining an array of SQL statements in the JSON value.

---

## 4. Developer Workflow

### 4.1 Creating a New Component

**Goal**: Create a "Dashboard" component mapped to `/dashboard`.

1.  **Copy Template**: Start from `cmp_7000_hellocomp` or `cmp_5100_sign`.
    ```bash
    cp -r src/component/cmp_7000_hellocomp src/component/cmp_8000_dashboard
    ```

2.  **Configuration**:
    *   Edit `manifest.json`:
        ```json
        {
            "uuid": "dashboard_8x90s",
            "name": "Dashboard",
            "route": "/dashboard",
            ...
        }
        ```
    *   Clean up `schema.json` to remove old component data.

3.  **Backend Implementation**:
    *   Rename/Edit `route/dispatcher_dashboard.py`:
        ```python
        from core.dispatcher import Dispatcher
        class DispatcherDashboard(Dispatcher):
            def _pre_process(self):
                # Add custom logic here
                self.view.set_data("dashboard_stats", {"users": 100})
        ```
    *   Update `route/routes.py`:
        ```python
        @bp.route("/")
        def index():
            # "root" folder in neutral/route/
            dispatch = DispatcherDashboard(request, "", bp.neutral_route)
            return dispatch.view.render()
        ```

4.  **Frontend Implementation**:
    *   Edit `neutral/route/root/content-snippets.ntpl`.
    *   **Crucial**: You must define `current:template:body-main-content`.
        ```ntpl
        {:snip; current:template:body-main-content >>
            <h1>Dashboard</h1>
            <p>Users: {:;dashboard_stats->users:}</p>
        :}
        {:^;:}
        ```

### 4.2 Handling Forms
Inherit from `DispatcherForm` (see `src/core/dispatcher_form.py` and `cmp_5100_sign`).

1.  **Dispatcher**:
    ```python
    class DispatcherMyForm(DispatcherForm):
        def form_post(self) -> bool:
            if not self.validate_post("ref:my_form_error"): return False
            # Process data...
            return True
    ```
2.  **Template**:
    Use `{:snip; form-start :}`, `{:snip; form-end :}` and input snippets provided by the theme or form component.

### 4.3 Database Interactions
To add a new query:

1.  Create `src/model/dashboard.json`.
    ```json
    {
        "get-stats": {
            "@portable": "SELECT COUNT(*) as count FROM user"
        }
    }
    ```
2.  Call it in Python:
    ```python
    stats = self.model.exec("dashboard", "get-stats", {})
    ```

### 4.4 Using Neutral Templates (NTPL)
*   **Snippets**: Reusable blocks. `{:snip; name >> content :}` to define, `{:snip; name :}` to call.
*   **Conditionals**: `{:filled; var >> show :}`.
*   **Variables**:
    *   `{:;varname:}`: Output variable.
    *   `{:;local::varname:}`: Output from local (inheritable) scope.
    *   `{:trans; key :}`: Translate string.
*   **Includes**: `{:include; file.ntpl :}`.

Refer to `docs/templates-neutrats.md` for full syntax.

---

## 5. Security & Best Practices

1.  **Do NOT write SQL in Python**. Always use `src/model/*.json`.
2.  **Use Context**: All user input (POST, GET) is available in `self.schema_data['CONTEXT']`. Do not access Flask's `request` object directly for data processing in templates if possible.
3.  **Naming**:
    *   Components: `cmp_NNNN_name`.
    *   UUIDs: specific format (alphanumeric + underscore).
4.  **Tokens**: The system automatically handles `UTOKEN` (User identity token) and `LTOKEN` (Link/Form token) to prevent CSRF. Ensure your forms include the necessary token fields (usually handled by `form-start` snippet).

---

## 6. Testing

Run tests with `pytest`. Each component should carry its own tests.

```bash
# Test specific component
pytest src/component/cmp_8000_dashboard/tests
```

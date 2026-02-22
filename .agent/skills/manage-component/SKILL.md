---
name: manage-component
description: Create or modify components following the standard architecture, security standards, and best practices of the Neutral TS Starter Py framework.
---

# Create or Modify Neutral TS Component Skill

This comprehensive skill provides complete guidance for creating new components or modifying existing ones in the Neutral TS Starter Py framework. It covers directory structure, configuration files, backend routes, dispatchers, frontend templates, security standards, testing, and deployment considerations.

## Prerequisites

Before using this skill, ensure you understand:
- Basic Python and Flask knowledge
- Neutral Template Language (NTPL) syntax
- Component-based architecture principles
- Security best practices for web applications

Use `view_file` on `docs/component.md` for component architecture details.
Use `view_file` on `docs/dispatcher.md` for dispatcher patterns and business logic.
Use `view_file` on `docs/templates-neutrats.md` for NTPL syntax reference.
Use `view_file` on `docs/development-style-guide.md` for routing and template organization.
Use `view_file` on `docs/translation-component.md` for translation strategies.
Use `view_file` on `docs/model.md` for database interaction patterns.

---

## 1. Component Architecture Overview

### 1.1 What is a Component?

A component in Neutral TS Starter Py is a self-contained, modular unit that encapsulates:
- **Backend Logic**: Python/Flask routes and business logic
- **Frontend Templates**: NTPL templates for rendering
- **Configuration**: Manifest, schema, and localization files
- **Static Assets**: CSS, JavaScript, images
- **Tests**: Component-specific test suite

Components are isolated functional units that can be enabled, disabled, or overridden without affecting other parts of the application.

### 1.2 Component Loading System

Components are loaded in **alphabetical order** based on their folder name. This enables:
- **Priority Control**: Later components can override earlier ones
- **Modularity**: Components can be added/removed independently
- **Fallback Patterns**: Components starting with `cmp_9` serve as catch-alls

**Loading Order:**
1. Components `cmp_0000` to `cmp_8999` (alphabetically)
2. Components `cmp_9000` to `cmp_9999` (fallback/catch-all components)

**Naming Convention:**
```
cmp_NNNN_name/
│   ├── NNNN: Load order number (5000-7000 for normal components)
│   └── name: Descriptive component name (lowercase, underscores)
```

### 1.3 Component Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPONENT LIFECYCLE                       │
├─────────────────────────────────────────────────────────────┤
│  1. DISCOVERY: Scan src/component/ for cmp_* folders        │
│  2. REGISTRATION: Read manifest.json, apply overrides       │
│  3. SCHEMA MERGE: Load schema.json, merge with global       │
│  4. PYTHON INIT: Execute __init__.py init_component()       │
│  5. BLUEPRINT: Execute route/__init__.py init_blueprint()   │
│  6. TEMPLATES: Load neutral/component-init.ntpl snippets    │
│  7. READY: Component available for requests                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Directory Structure

### 2.1 Standard Component Structure

```
src/component/cmp_NNNN_name/
├── manifest.json                    # Component identity (REQUIRED)
├── schema.json                      # Configuration, menus, translations
├── custom.json                      # Local overrides (NEVER commit)
├── __init__.py                      # Component initialization
├── README.md                        # Component documentation
├── route/                           # Backend (Python/Flask)
│   ├── __init__.py                  # Blueprint initialization
│   ├── routes.py                    # Flask route definitions
│   └── dispatcher_name.py           # Custom business logic (optional)
├── neutral/                         # Frontend (NTPL)
│   ├── component-init.ntpl          # Global snippets (app-wide)
│   ├── obj/                         # Template-to-Python mappings
│   │   └── object.json              # Python object definitions
│   └── route/                       # Component templates
│       ├── index-snippets.ntpl      # Component-level snippets
│       ├── locale-xx.json           # Translations (es, fr, de, en)
│       ├── data.json                # Shared route metadata
│       └── root/                    # Template root for routes
│           ├── data.json            # Route metadata
│           ├── content-snippets.ntpl # Main template
│           └── subroute/            # Subroute templates
│               ├── data.json
│               └── content-snippets.ntpl
├── static/                          # CSS, JS, images
├── src/                             # Backend logic snippets
│   └── module.py                    # Python functions for templates
├── lib/                             # Private Python libraries
│   └── uuid_name/                   # Namespaced package
└── tests/                           # Pytest test suite
    ├── conftest.py                  # Test configuration
    └── test_component.py            # Component tests
```

### 2.2 Minimum Viable Structure

For a simple component with no custom logic:

```
src/component/cmp_NNNN_name/
├── manifest.json
├── schema.json
├── route/
│   ├── __init__.py
│   └── routes.py
└── neutral/
    └── route/
        └── root/
            ├── data.json
            └── content-snippets.ntpl
```

---

## 3. Configuration Files

### 3.1 manifest.json (REQUIRED)

Defines component identity and registration metadata.

```json
{
  "uuid": "component_name_random",
  "name": "Component Display Name",
  "description": "Detailed component description",
  "version": "1.0.0",
  "route": "/url-prefix",
  "required": {
    "component": {
      "dependency_uuid": "version_constraint"
    }
  },
  "config": {
    "cache_seconds": 300,
    "custom_setting": "value"
  }
}
```

**Field Requirements:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `uuid` | string | **Yes** | Unique identifier, format: `name_random` (alphanumeric + underscore) |
| `name` | string | **Yes** | Human-readable component name |
| `description` | string | **Yes** | Component description |
| `version` | string | **Yes** | Semantic version (major.minor.patch) |
| `route` | string | **Yes** | Base URL prefix for component routes |
| `required` | object | No | Component dependencies |
| `config` | object | No | Component-specific configuration |

**UUID Rules:**
- Must be unique across all components
- Format: `name_random` (lowercase alphanumeric + underscore)
- Minimum length: 5 characters
- Maximum length: 50 characters
- Must contain at least one underscore
- Use UUID for cross-component references (not folder name)

**Example:**
```json
{
  "uuid": "dashboard_8x90s",
  "name": "Dashboard",
  "description": "User dashboard with statistics and quick actions",
  "version": "1.0.0",
  "route": "/dashboard"
}
```

### 3.2 schema.json

Defines configuration, menu entries, translations, and global data.

```json
{
  "inherit": {
    "locale": {
      "trans": {
        "en": { "Menu Item": "Menu Item" },
        "es": { "Menu Item": "Elemento del Menú" },
        "fr": { "Menu Item": "Élément du Menu" },
        "de": { "Menu Item": "Menüelement" }
      }
    },
    "data": {
      "drawer": {
        "menu": {
          "session:": {
            "tab-id": {
              "name": "Tab Name",
              "tabs": "tab-id",
              "icon": "x-icon-info"
            }
          },
          "session:true": {
            "tab-id": {
              "name": "Tab Name",
              "tabs": "tab-id",
              "icon": "x-icon-info"
            }
          }
        }
      },
      "menu": {
        "session:": {
          "tab-id": {
            "item-id": {
              "text": "Menu Item",
              "link": "[:;data->uuid->manifest->route:]",
              "icon": "x-icon-info"
            }
          }
        },
        "session:true": {
          "tab-id": {
            "item-id": {
              "text": "Menu Item",
              "link": "[:;data->uuid->manifest->route:]",
              "icon": "x-icon-info"
            }
          }
        }
      },
      "navbar": {
        "menu": {
          "session:": {
            "item-id": {
              "name": "Item Name",
              "link": "#modal-id",
              "icon": "x-icon-info",
              "prop": {
                "data-bs-toggle": "modal",
                "data-bs-target": "#modal-id"
              }
            }
          },
          "session:true": {
            "item-id": {
              "name": "Item Name",
              "link": "#modal-id",
              "icon": "x-icon-info"
            }
          }
        }
      }
    }
  },
  "data": {
    "core": {
      "forms": {
        "form_name": {
          "check_fields": ["field1", "field2"],
          "validation": {
            "minfields": 2,
            "maxfields": 5,
            "allow_fields": ["field1", "field2", "ftoken.*"]
          },
          "rules": {
            "field1": {
              "required": true,
              "minlength": 3,
              "maxlength": 50,
              "regex": "^[a-zA-Z]+$"
            },
            "field2": {
              "required": true,
              "minlength": 6,
              "maxlength": 200,
              "regex": "^[^@\s]+@[^@\s]+\.[^@\s]+$",
              "dns": "MX"
            }
          }
        }
      }
    },
    "component-specific": {
      "key": "value"
    }
  }
}
```

**Important Schema Rules:**

1. **Menu Structure**: Define BOTH `drawer` (tab) and `menu` (items) for navigation
2. **Session States**: Use `session:` for logged-out users, `session:true` for logged-in
3. **Route References**: Use `[:;data->uuid->manifest->route:]` in schema.json
4. **Form Validation**: Define rules under `data.core.forms.form_name.rules`
5. **Translations**: Place global translations in `inherit.locale.trans`

### 3.3 custom.json (Optional, Never Commit)

Local overrides for development or deployment-specific configuration.

```json
{
  "manifest": {
    "route": "/custom-route"
  },
  "schema": {
    "inherit": {
      "data": {
        "custom_setting": "override_value"
      }
    }
  }
}
```

**Important:**
- Never commit `custom.json` to version control
- Add to `.gitignore`
- Use for local development overrides only
- Production overrides should use `config/config.db` table `custom`

### 3.4 config/config.db Overrides

For centralized component overrides in production:

```sql
-- Table: custom
-- Columns: comp_uuid (TEXT), value_json (TEXT), enabled (INTEGER)

INSERT INTO custom (comp_uuid, value_json, enabled)
VALUES ('dashboard_8x90s', '{"manifest": {"route": "/prod-dashboard"}}', 1);
```

---

## 4. Backend Implementation

### 4.1 route/__init__.py (Blueprint Initialization)

```python
"""Component Blueprint Module."""
from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    """Initialize Flask Blueprint for this component."""
    bp = create_blueprint(component, component_schema)
    # Import routes after creating the blueprint
    from . import routes  # pylint: disable=import-error,C0415,W0611
```

**Key Points:**
- Must define `init_blueprint` function
- Use `create_blueprint` utility (sets `bp.neutral_route` automatically)
- Import routes module after blueprint creation
- Blueprint name is auto-generated: `bp_cmp_NNNN_name`

### 4.2 route/routes.py (Route Definitions)

#### Simple Component (Single Dispatcher)

```python
"""Component routes module."""
from flask import Response, request
from core.dispatcher import Dispatcher
from . import bp

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all GET requests."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

#### Complex Component (Multiple Dispatchers)

```python
"""Component routes module."""
from flask import Response, request
from app.config import Config
from app.extensions import limiter
from . import bp
from .dispatcher_main import DispatcherMain
from .dispatcher_form import DispatcherFormCustom

@bp.route("/", defaults={"route": ""}, methods=["GET"])
def index(route) -> Response:
    """Handle root route."""
    dispatch = DispatcherMain(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.load_data()
    return dispatch.view.render()

@bp.route("/form/<ltoken>", defaults={"route": "form"}, methods=["GET"])
def form_get(route, ltoken) -> Response:
    """Handle form GET request."""
    dispatch = DispatcherFormCustom(request, route, bp.neutral_route, ltoken, "my_form")
    dispatch.schema_data["dispatch_result"] = dispatch.form_get()
    return dispatch.view.render()

@bp.route("/form/<ltoken>", defaults={"route": "form"}, methods=["POST"])
@limiter.limit(Config.FORM_LIMITS, error_message="Please wait.")
def form_post(route, ltoken) -> Response:
    """Handle form POST request."""
    dispatch = DispatcherFormCustom(request, route, bp.neutral_route, ltoken, "my_form")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.view.render()

@bp.route("/ajax/<action>", methods=["GET"])
def ajax_action(route, action) -> Response:
    """Handle AJAX requests."""
    dispatch = DispatcherMain(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.ajax_action(action)
    return dispatch.view.render()
```

#### Static File Serving

```python
"""Component routes module with static file support."""
import os
from flask import Response, request, send_from_directory
from app.config import Config
from core.dispatcher import Dispatcher
from . import bp

STATIC = f"{bp.component['path']}/static"

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all GET requests, serve static files if they exist."""
    # Check if route is a static file
    if route:
        file_path = os.path.join(STATIC, route)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            response = send_from_directory(STATIC, route)
            response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
            return response

    # Use dispatcher for template routes
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

### 4.3 Custom Dispatcher (dispatcher_name.py)

#### Basic Custom Dispatcher

```python
"""Custom dispatcher for component."""
from core.dispatcher import Dispatcher

class DispatcherCustom(Dispatcher):
    """Custom dispatcher with business logic."""

    def __init__(self, request, comp_route, neutral_route=None):
        super().__init__(request, comp_route, neutral_route)
        # Set component-specific local data
        self.schema_local_data['component_key'] = "default_value"
        self.schema_local_data['show_sidebar'] = "true"

    def load_data(self) -> bool:
        """Load data for templates."""
        try:
            # Add data to templates
            self.schema_data["items"] = self._fetch_items()
            self.schema_data["items_count"] = str(len(self.schema_data["items"]))
            self.schema_local_data["message"] = "Data loaded successfully"
            return True
        except Exception as e:
            self.schema_data["error_message"] = str(e)
            self.schema_local_data["message"] = "Failed to load data"
            return False

    def _fetch_items(self) -> list:
        """Private helper to fetch items from database."""
        result = self.model.exec("component", "get-items", {})
        return result.get("rows", []) if result else []
```

#### Form Dispatcher (Extending DispatcherForm)

```python
"""Form dispatcher with validation."""
from core.dispatcher_form import DispatcherForm

class DispatcherFormCustom(DispatcherForm):
    """Form dispatcher with custom validation."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None, form_name="my_form"):
        super().__init__(req, comp_route, neutral_route, ltoken, form_name)
        self.schema_local_data['form_title'] = "Contact Form"

    def form_get(self) -> bool:
        """Validate GET request."""
        if not self.valid_form_tokens_get():
            self.error['form']['ltoken'] = "true"
            return False
        return True

    def form_post(self) -> bool:
        """Process form submission."""
        # Validate tokens
        if not self.valid_form_tokens_post():
            self.error['form']['ltoken'] = "true"
            return False

        # Validate form-level constraints
        if not self.valid_form_validation():
            self.error['form']['validation'] = "true"
            return False

        # Validate individual fields
        if self.any_error_form_fields("ref:my_form_error"):
            return False

        # Process valid form data
        try:
            email = self.schema_data["CONTEXT"]["POST"].get("email")
            message = self.schema_data["CONTEXT"]["POST"].get("message")

            # Store or process data
            self.model.exec("component", "save-message", {
                "email": email,
                "message": message
            })

            self.form_submit["result"] = {
                "success": "true",
                "message": f"Thank you, {email}! Your message has been sent."
            }
            return True
        except Exception as e:
            self.form_submit["result"] = {
                "success": "false",
                "error": "SUBMISSION_FAILED",
                "message": "Failed to process your request."
            }
            return False
```

#### Authentication Dispatcher (Extending DispatcherFormSign pattern)

```python
"""Authentication dispatcher example."""
from core.dispatcher_form import DispatcherForm
from core.mail import Mail
from constants import USER_EXISTS

class DispatcherFormAuth(DispatcherForm):
    """Authentication dispatcher with user management."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None, form_name="auth_form"):
        super().__init__(req, comp_route, neutral_route, ltoken, form_name)

    def validate_post(self, error_prefix) -> bool:
        """Validate POST request."""
        # Check session state
        if self.schema_data["CONTEXT"]["SESSION"]:
            self.error["form"]["already_session"] = "true"
            return False

        # Validate tokens
        if not self.valid_form_tokens_post():
            return False

        # Validate form constraints
        if not self.valid_form_validation():
            return False

        # Validate fields
        if self.any_error_form_fields(error_prefix):
            return False

        return True

    def create_user(self, user_data) -> dict:
        """Create new user account."""
        result = self.user.create(user_data)

        if not result.get("success"):
            self.form_submit["result"] = {
                "success": "false",
                "error": result.get("error", "REGISTRATION_FAILED"),
                "message": result.get("message", "Failed to create user"),
            }
            return self.form_submit["result"]

        # Send confirmation email
        mail = Mail(self.schema.properties)
        mail.send("register", result.get('user_data', {}))

        self.form_submit["result"] = {
            "success": "true",
            "message": "Registration completed. Please check your email."
        }
        return self.form_submit["result"]

    def create_session(self, user_data) -> bool:
        """Create user session after authentication."""
        from utils.utils import format_ua
        from app.config import Config

        session_data = {
            "PATH": self.schema_data["CONTEXT"]["PATH"],
            "METHOD": self.schema_data["CONTEXT"]["METHOD"],
            "HEADERS": self.schema_data["CONTEXT"]["HEADERS"],
            "UA": self.schema_data["CONTEXT"]["UA"],
            "user_data": user_data,
        }

        ua = self.schema_data["CONTEXT"].get("UA", "")
        session_ua = format_ua(ua) if ua else "none"

        session_cookie = self.session.create(user_data["userId"], session_ua, session_data)
        self.schema_data["CONTEXT"]["SESSION"] = session_cookie[Config.SESSION_KEY]["value"]
        self.view.add_cookie(session_cookie)

        return True
```

### 4.4 Database Interactions (Model)

#### Define SQL in src/model/component.json

```json
{
  "get-items": {
    "@portable": "SELECT id, name, description FROM component_items WHERE active = 1 ORDER BY created DESC"
  },
  "get-item-by-id": {
    "@portable": "SELECT id, name, description FROM component_items WHERE id = :id"
  },
  "save-message": {
    "@portable": [
      "INSERT INTO component_messages (email, message, created) VALUES (:email, :message, :created)",
      "UPDATE component_stats SET message_count = message_count + 1 WHERE id = 1"
    ]
  },
  "create-item": {
    "@portable": "INSERT INTO component_items (name, description, active, created) VALUES (:name, :description, 1, :created)"
  },
  "update-item": {
    "@portable": "UPDATE component_items SET name = :name, description = :description, modified = :modified WHERE id = :id"
  },
  "delete-item": {
    "@portable": "DELETE FROM component_items WHERE id = :id"
  }
}
```

#### Execute in Python

```python
# Get items
result = self.model.exec("component", "get-items", {})
items = result.get("rows", []) if result else []

# Get single item
result = self.model.exec("component", "get-item-by-id", {"id": item_id})
item = result.get("rows", [None])[0] if result else None

# Transaction (multiple statements)
result = self.model.exec("component", "save-message", {
    "email": email,
    "message": message,
    "created": int(time.time())
})
```

---

## 5. Frontend Templates (NTPL)

### 5.1 Template File Structure

```
neutral/route/
├── index-snippets.ntpl          # Component-level snippets
├── locale-xx.json               # Translations
├── data.json                    # Shared metadata
└── root/
    ├── data.json                # Root route metadata
    ├── content-snippets.ntpl    # Root route template
    └── subroute/
        ├── data.json            # Subroute metadata
        └── content-snippets.ntpl # Subroute template
```

### 5.2 Route Metadata (data.json)

```json
{
  "data": {
    "current": {
      "route": {
        "title": "Page Title",
        "description": "SEO description for search engines",
        "h1": "Visible Page Heading"
      }
    }
  }
}
```

### 5.3 Main Template (content-snippets.ntpl)

```html
{:* Copyright (C) 2025 Component Author *:}
{:*
Data for this route
-------------------
*:}
{:data; #/data.json :}

{:*
Locale for this route (optional)
--------------------------------
*:}
{:locale; {:flg; require :} >> #/locale.json :}

{:*
Disable carousel (optional)
---------------------------
*:}
{:snip; current:template:body-carousel >> :}

{:*
Disable lateral bar (optional)
------------------------------
*:}
{:snip; current:template:body-lateral-bar >> :}

{:*
Overwrite page heading (optional)
---------------------------------
*:}
{:snip; current:template:page-h1 >>
<div class="container my-3">
  <h1 class="border-bottom p-2">{:trans; {:;local::current->route->h1:} :}</h1>
</div>
:}

{:*
Main content snippet (REQUIRED)
-------------------------------
*:}
{:snip; current:template:body-main-content >>
<div class="{:;local::current->theme->class->container:}">
  <h3>{:trans; {:;local::current->route->h1:} :}</h3>
  <p>{:trans; Component content here. :}</p>

  {:* Access schema_data (immutable) *:}
  <p>Result: {:;dispatch_result:}</p>
  <p>Items Count: {:;items_count:}</p>

  {:* Access schema_local_data (mutable) *:}
  <p>Message: {:;local::message:}</p>

  {:* Conditional rendering *:}
  {:bool; dispatch_result >>
    <div class="alert alert-success">Success!</div>
  :}{:else;
    <div class="alert alert-danger">Failed!</div>
  :}

  {:* Session-aware content *:}
  {:bool; HAS_SESSION >>
    <p>Welcome back, {:;CURRENT_USER->profile->alias:}!</p>
  :}{:else;
    <p>Please sign in to access more features.</p>
  :}

  {:* Loop through data *:}
  {:each; items key item >>
    <div class="card mb-3">
      <div class="card-body">
        <h5 class="card-title">{:;item->name:}</h5>
        <p class="card-text">{:;item->description:}</p>
      </div>
    </div>
  :}

  {:* Link with LTOKEN for forms *:}
  <a href="{:;CURRENT_COMP_ROUTE:}/form/{:;LTOKEN:}" class="btn btn-primary">
    Go to Form
  </a>

  {:* CSP-compliant inline script *:}
  <script nonce="{:;CSP_NONCE:}">
    console.log("Component loaded");
  </script>
</div>
:}

{:*
Force output detection (REQUIRED)
---------------------------------
*:}
{:^;:}
```

### 5.4 Component-Level Snippets (index-snippets.ntpl)

```html
{:* Copyright (C) 2025 Component Author *:}
{:*
Data for all component routes
-----------------------------
*:}
{:data; {:flg; require :} >> #/data.json :}

{:*
Locale for all component routes
-------------------------------
Only current language file is loaded
*:}
{:locale;
  #/locale-{:lang;:}.json
:}{:else;
  {:locale; #/locale-en.json :}
:}

{:*
Reusable snippets for this component
------------------------------------
*:}
{:snip; component-custom-snippet >>
<div class="component-widget">
  <h4>{:trans; Widget Title :}</h4>
  <p>{:trans; Widget content here. :}</p>
</div>
:}

{:*
Modal definitions
-----------------
*:}
{:snip; component-modal >>
<div class="modal fade" id="componentModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">{:trans; Modal Title :}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        {:trans; Modal content here. :}
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
          {:trans; Close :}
        </button>
      </div>
    </div>
  </div>
</div>
:}

{:moveto; /body >>
{:snip; component-modal :}
:}
```

### 5.5 Global Snippets (component-init.ntpl)

```html
{:* Copyright (C) 2025 Component Author *:}
{:*
Snippets available globally across all components
-------------------------------------------------
*:}
{:snip; global-component-snippet >>
<div class="global-widget">
  {:trans; Global content available everywhere. :}
</div>
:}

{:*
Add CSS/JS to head
------------------
*:}
{:snip; current:template:head:component >>
<link nonce="{:;CSP_NONCE:}" rel="stylesheet" href="{:;CURRENT_COMP_ROUTE:}/static/component.css" />
<style nonce="{:;CSP_NONCE:}">
  .component-custom { color: blue; }
</style>
:}

{:*
Add JavaScript to body end
--------------------------
*:}
{:snip; current:template:body-end:component >>
<script nonce="{:;CSP_NONCE:}">
  (function() {
    console.log("Component initialized");
  })();
</script>
:}
```

### 5.6 Translation Files (locale-xx.json)

#### Single Language File (locale-es.json)

```json
{
  "_comment_:trans": "Translation file for Spanish",
  "trans": {
    "es": {
      "Component Name": "Nombre del Componente",
      "Page Title": "Título de la Página",
      "Welcome": "Bienvenido",
      "ref:form_error_required": "Campo requerido",
      "ref:form_error_invalid": "Valor inválido"
    }
  }
}
```

#### Multi-Language File (locale.json)

```json
{
  "_comment_:trans": "Multi-language translation file",
  "trans": {
    "en": {
      "Component Name": "Component Name",
      "Welcome": "Welcome"
    },
    "es": {
      "Component Name": "Nombre del Componente",
      "Welcome": "Bienvenido"
    },
    "fr": {
      "Component Name": "Nom du Composant",
      "Welcome": "Bienvenue"
    },
    "de": {
      "Component Name": "Komponentenname",
      "Welcome": "Willkommen"
    }
  }
}
```

### 5.7 Translation Scope Strategy

| Scope | Location | Use Case |
|-------|----------|----------|
| **Global (App-wide)** | `schema.json` → `inherit.locale.trans` | Menu items, navigation labels |
| **Component-wide** | `neutral/route/locale-xx.json` | Component-specific UI text |
| **Route-specific** | `neutral/route/root/subroute/locale.json` | Page-specific content |
| **Reference Keys** | Any locale file with `ref:` prefix | Error messages, validation texts |

**Priority Order:** Route → Component → Global (later overrides earlier)

---

## 6. Form Handling

### 6.1 Form Definition in schema.json

```json
{
  "data": {
    "core": {
      "forms": {
        "contact_form": {
          "check_fields": ["name", "email", "message", "agree"],
          "validation": {
            "minfields": 3,
            "maxfields": 5,
            "allow_fields": ["name", "email", "message", "agree", "ftoken.*"]
          },
          "rules": {
            "name": {
              "required": true,
              "minlength": 3,
              "maxlength": 50,
              "regex": "^[a-zA-Z\s]+$"
            },
            "email": {
              "required": true,
              "minlength": 6,
              "maxlength": 200,
              "regex": "^[^@\s]+@[^@\s]+\.[^@\s]+$",
              "dns": "MX"
            },
            "message": {
              "required": true,
              "minlength": 10,
              "maxlength": 1000
            },
            "agree": {
              "required": true,
              "value": "true"
            }
          }
        }
      }
    }
  }
}
```

### 6.2 Form Template (content-snippets.ntpl)

```html
{:* Form wrapper *:}
{:snip; contact_form-wrapper >>
<div id="form-wrapper-contact">
  {:coalesce;
    {:snip; forms:error-ltoken:{:;contact_form->error->form->ltoken:} :}
    {:snip; forms:error-ftoken:{:;contact_form->error->form->ftoken:} :}
    {:snip; forms:error-validation:{:;contact_form->error->form->validation:} :}
    {:snip; contact_form-form :}
  :}
</div>
:}

{:* Form fields *:}
{:snip; contact_form-form >>
{:fetch; |{:;CURRENT_COMP_ROUTE:}/form/{:;LTOKEN:}|form|form-wrapper-contact|{:;local::current->forms->class:}|contact_form| >>

  {:* Name field *:}
  <div class="input-group">
    <span class="input-group-text {:;local::x-icon-user:}"></span>
    <div class="form-floating">
      <input
        type="text"
        id="contact_form-name"
        name="name"
        value="{:;CONTEXT->POST->name:}"
        class="form-control"
        placeholder="{:trans; Your name :}"
        minlength="{:;core->forms->contact_form->rules->name->minlength:}"
        maxlength="{:;core->forms->contact_form->rules->name->maxlength:}"
        {:bool; core->forms->contact_form->rules->name->required >> required :}
      >
      <label for="contact_form-name">{:trans; Your name :}</label>
    </div>
  </div>
  {:snip; error-msg:name :}

  {:* Email field *:}
  <div class="input-group">
    <span class="input-group-text {:;local::x-icon-email:}"></span>
    <div class="form-floating">
      <input
        type="email"
        id="contact_form-email"
        name="email"
        value="{:;CONTEXT->POST->email:}"
        class="form-control ftoken-field-key ftoken-field-value"
        placeholder="{:trans; Your email :}"
        data-ftokenid="contact_form-ftoken"
      >
      <label for="contact_form-email">{:trans; Your email :}</label>
    </div>
  </div>
  {:snip; error-msg:email :}

  {:* Message field *:}
  <div class="form-floating">
    <textarea
      id="contact_form-message"
      name="message"
      class="form-control"
      placeholder="{:trans; Your message :}"
      minlength="{:;core->forms->contact_form->rules->message->minlength:}"
      maxlength="{:;core->forms->contact_form->rules->message->maxlength:}"
    >{:;CONTEXT->POST->message:}</textarea>
    <label for="contact_form-message">{:trans; Your message :}</label>
  </div>
  {:snip; error-msg:message :}

  {:* Agree checkbox *:}
  <div class="form-check">
    <input
      type="checkbox"
      id="contact_form-agree"
      name="agree"
      class="form-check-input"
      value="true"
      {:filled; CONTEXT->POST->agree >> checked :}
    >
    <label class="form-check-label" for="contact_form-agree">
      {:trans; I agree with the terms :}
    </label>
  </div>
  {:snip; error-msg:agree :}

  {:* FToken field *:}
  {:code;
    {:param; ftoken_fetch_id >> contact_form-ftoken :}
    {:param; ftoken_form_id >> contact_form :}
    {:snip; ftoken:form-field :}
  :}

  {:* Submit button *:}
  <button type="submit" class="btn btn-primary">
    {:trans; Send Message :}
  </button>
:}
:}
```

### 6.3 Form Error Handling

```html
{:* Error message snippet *:}
{:snip; error-msg:name >>
{:filled; contact_form->error->field->name >>
  <div class="invalid-feedback d-block">
    {:trans; {:;contact_form->error->field->name:} :}
  </div>
:}
:}

{:* Form-level error *:}
{:snip; forms:error-validation:{:;contact_form->error->form->validation:} >>
<div class="alert alert-danger">
  {:trans; Please check the form for errors. :}
</div>
:}
```

---

## 7. Security Standards

### 7.1 Critical Security Rules

| Rule | Description | Implementation |
|------|-------------|----------------|
| **No SQL in Python** | Never write raw SQL in Python code | Use `src/model/*.json` files |
| **Use CONTEXT** | Access user data through CONTEXT object | `self.schema_data['CONTEXT']['POST']` |
| **Translate UI Text** | All visible text must be translatable | Wrap with `{:trans; :}` |
| **Include LTOKEN** | Forms must have link tokens | `{:;LTOKEN:}` in form URLs |
| **CSP Nonce** | Inline scripts need nonce | `nonce="{:;CSP_NONCE:}"` |
| **Safe Includes** | Validate dynamic includes | Use `{:allow; :}` with whitelist |
| **Force Output** | End templates with output marker | `{:^;:}` at end of file |
| **AJAX Header** | AJAX requests need header | `Requested-With-Ajax: true` |

### 7.2 Secure Template Patterns

#### Safe Dynamic Include

```html
{:* Declare allowed files *:}
{:declare; valid_pages >> page1.ntpl page2.ntpl page3.ntpl :}

{:* Safe include with allow list *:}
{:include;
  {:allow; valid_pages >> {:;page_name:} :}
{:else;
  {:exit; 404 :}
:}
```

#### CSP-Compliant Scripts

```html
{:* Inline script with nonce *:}
<script nonce="{:;CSP_NONCE:}">
  (function() {
    console.log("Safe script");
  })();
</script>

{:* Inline style with nonce *:}
<style nonce="{:;CSP_NONCE:}">
  .custom-class { color: blue; }
</style>
```

#### Auto-Escaped User Data

```html
{:* CONTEXT data is auto-escaped *:}
<p>{:;CONTEXT->POST->username:}</p>

{:* Manual escaping for other data *:}
<p>{:&;untrusted_variable:}</p>
```

### 7.3 AJAX Request Security

```javascript
// JavaScript AJAX request
fetch("/component/route", {
  method: "POST",
  headers: {
    "Requested-With-Ajax": "true",
    "Content-Type": "application/x-www-form-urlencoded"
  },
  body: new URLSearchParams({ key: "value" })
});
```

**Server-Side AJAX Detection:**

```python
# In dispatcher
self.ajax_request = self.schema_data['CONTEXT']['HEADERS'].get("Requested-With-Ajax") or False

# AJAX-specific behavior
if self.ajax_request:
    # Skip cookie rotation
    # Use AJAX template
    pass
```

### 7.4 Rate Limiting

```python
from app.config import Config
from app.extensions import limiter

@bp.route("/form/<ltoken>", methods=["POST"])
@limiter.limit(Config.FORM_LIMITS, error_message="Please wait.")
@limiter.limit(
    Config.EMAIL_LIMITS,
    key_func=lambda: request.form.get("email", ""),
    error_message="Too many requests from this email."
)
def form_post(route, ltoken) -> Response:
    dispatch = DispatcherFormCustom(request, route, bp.neutral_route, ltoken, "my_form")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.view.render()
```

---

## 8. Testing

### 8.1 Test File Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_component.py        # Component tests
├── test_routes.py           # Route tests
├── test_dispatcher.py       # Dispatcher tests
└── test_templates.py        # Template tests
```

### 8.2 Test Configuration (conftest.py)

```python
"""Test configuration and fixtures."""
import pytest
from app import create_app
from app.config import Config

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
```

### 8.3 Component Tests (test_component.py)

```python
"""Component tests."""
import pytest

def test_component_route(client):
    """Test component root route."""
    response = client.get("/component-route")
    assert response.status_code == 200
    assert b"Component Content" in response.data

def test_component_subroute(client):
    """Test component subroute."""
    response = client.get("/component-route/subroute")
    assert response.status_code == 200

def test_component_404(client):
    """Test 404 handling."""
    response = client.get("/component-route/nonexistent")
    assert response.status_code == 404

def test_component_ajax(client):
    """Test AJAX endpoint."""
    response = client.get(
        "/component-route/ajax",
        headers={"Requested-With-Ajax": "true"}
    )
    assert response.status_code == 200
```

### 8.4 Form Tests (test_forms.py)

```python
"""Form validation tests."""
import pytest

def test_form_get_requires_ltoken(client):
    """Test form GET requires valid ltoken."""
    response = client.get("/component-route/form/invalid-token")
    assert response.status_code == 200
    assert b"ltoken" in response.data or b"error" in response.data

def test_form_post_validation(client):
    """Test form POST validation."""
    response = client.post(
        "/component-route/form/valid-token",
        data={
            "email": "invalid",  # Invalid email
            "message": "test"
        }
    )
    assert response.status_code == 200
    assert b"error" in response.data

def test_form_post_success(client):
    """Test successful form submission."""
    response = client.post(
        "/component-route/form/valid-token",
        data={
            "email": "valid@example.com",
            "message": "Test message",
            "agree": "true"
        }
    )
    assert response.status_code == 200
    assert b"success" in response.data or b"Thank you" in response.data
```

### 8.5 Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run component-specific tests
pytest src/component/cmp_NNNN_name/tests

# Run with verbose output
pytest -v src/component/cmp_NNNN_name/tests

# Run with coverage
pytest --cov=src/component/cmp_NNNN_name src/component/cmp_NNNN_name/tests

# Run full test suite
pytest

# Run with HTML report
pytest --html=report.html
```

### 8.6 Code Quality

```bash
# Run pylint on component
pylint src/component/cmp_NNNN_name

# Run pylint with specific options
pylint --disable=C0114,C0115,C0116 src/component/cmp_NNNN_name

# Check for security issues
bandit -r src/component/cmp_NNNN_name

# Check code style
flake8 src/component/cmp_NNNN_name
```

---

## 9. Implementation Checklist

### 9.1 New Component Checklist

- [ ] **Directory Structure**
  - [ ] Create `src/component/cmp_NNNN_name/`
  - [ ] Create `route/` subdirectory
  - [ ] Create `neutral/route/root/` subdirectory
  - [ ] Create `static/` subdirectory (if needed)
  - [ ] Create `tests/` subdirectory

- [ ] **Configuration Files**
  - [ ] Create `manifest.json` with unique UUID
  - [ ] Create `schema.json` with menu entries
  - [ ] Create `custom.json` for local overrides (add to .gitignore)
  - [ ] Create `README.md` with component documentation

- [ ] **Backend Implementation**
  - [ ] Create `route/__init__.py` with blueprint
  - [ ] Create `route/routes.py` with route definitions
  - [ ] Create `route/dispatcher_name.py` (if custom logic needed)
  - [ ] Create `src/model/component.json` (if database needed)

- [ ] **Frontend Templates**
  - [ ] Create `neutral/component-init.ntpl` (global snippets)
  - [ ] Create `neutral/route/index-snippets.ntpl` (component snippets)
  - [ ] Create `neutral/route/root/data.json` (route metadata)
  - [ ] Create `neutral/route/root/content-snippets.ntpl` (main template)
  - [ ] Create `locale-xx.json` files for translations

- [ ] **Security**
  - [ ] Wrap all UI text with `{:trans; :}`
  - [ ] Include LTOKEN in form URLs
  - [ ] Add CSP nonce to inline scripts
  - [ ] Use `{:allow; :}` for dynamic includes
  - [ ] End templates with `{:^;:}`

- [ ] **Testing**
  - [ ] Create `tests/conftest.py`
  - [ ] Create `tests/test_component.py`
  - [ ] Run `pytest` for component
  - [ ] Run `pylint` on Python files

- [ ] **Documentation**
  - [ ] Update component README.md
  - [ ] Document routes and endpoints
  - [ ] Document configuration options
  - [ ] Document dependencies

### 9.2 Modification Checklist

- [ ] **Analysis**
  - [ ] Review existing component structure
  - [ ] Identify files to modify
  - [ ] Check for custom.json overrides
  - [ ] Check for config.db overrides

- [ ] **Changes**
  - [ ] Modify configuration files
  - [ ] Update routes and dispatchers
  - [ ] Update templates
  - [ ] Add/update translations

- [ ] **Testing**
  - [ ] Run existing tests
  - [ ] Add tests for new functionality
  - [ ] Verify no regressions

- [ ] **Documentation**
  - [ ] Update README.md
  - [ ] Document changes in changelog

---

## 10. Common Patterns and Examples

### 10.1 Data Access in Templates

```html
{:* schema_data (immutable) *:}
{:;varname:}
{:;object->key:}
{:;array->0->name:}
{:;CONTEXT->POST->field:}
{:;CURRENT_COMP_UUID:}
{:;CSP_NONCE:}
{:;LTOKEN:}
{:;HAS_SESSION:}

{:* schema_local_data (mutable) *:}
{:;local::varname:}
{:;local::object->key:}
{:;local::current->route->h1:}
{:;local::current->theme->class->container:}
```

### 10.2 Conditional Rendering

```html
{:* Boolean check *:}
{:bool; HAS_SESSION >>
  <p>Logged in</p>
:}{:else;
  <p>Not logged in</p>
:}

{:* Filled check (has content) *:}
{:filled; variable >>
  <p>Has content</p>
:}{:else;
  <p>Empty</p>
:}

{:* Defined check (exists) *:}
{:defined; variable >>
  <p>Variable exists</p>
:}

{:* Same value check *:}
{:same; /{:;status:}/active/ >>
  <p>Status is active</p>
:}

{:* Contains check *:}
{:contains; /{:;roles:}/admin/ >>
  <p>User is admin</p>
:}
```

### 10.3 Iteration

```html
{:* Each loop *:}
{:each; items key item >>
  <div class="item">
    <span>{:;key:}</span>
    <span>{:;item->name:}</span>
  </div>
:}

{:* For loop *:}
{:for; i 1..10 >>
  <p>Number: {:;i:}</p>
:}

{:* Nested iteration *:}
{:each; categories cat_key category >>
  <h3>{:;category->name:}</h3>
  {:each; category->items item_key item >>
    <p>{:;item->name:}</p>
  :}
:}
```

### 10.4 Component References

```html
{:* Access component by UUID *:}
{:;uuid->manifest->route:}
{:;uuid->manifest->name:}
{:;uuid->path:}
{:;uuid->schema->data->key:}

{:* Access component by name *:}
{:;cmp_NNNN_name->manifest->route:}

{:* Cross-component links *:}
<a href="{:;sign_0yt2sa->manifest->route:}/in">Sign In</a>
<a href="{:;dashboard_8x90s->manifest->route:}">Dashboard</a>
```

### 10.5 Caching

```html
{:* Cache for 300 seconds *:}
{:cache; /300/ >>
  <div>Cached content</div>
:}

{:* Cache with custom ID *:}
{:cache; /300/custom-id/ >>
  <div>Cached with ID</div>
:}

{:* Exclude from cache *:}
{:!cache;
  <div>Never cached</div>
:}
```

### 10.6 AJAX Fetch in Templates

```html
{:* Auto-fetch on page load *:}
{:fetch; |/component/ajax|auto| >>
  <div class="loading">{:snip; spin-2x :}</div>
:}

{:* Fetch on click *:}
{:fetch; |/component/ajax|click| >>
  <button>Load Content</button>
:}

{:* Fetch on form submit *:}
{:fetch; |/component/form|form|form-wrapper| >>
  <form>...</form>
:}

{:* Fetch on visible (scroll) *:}
{:fetch; |/component/ajax|visible| >>
  <div>Load when visible</div>
:}
```

---

## 11. Debugging Tips

### 11.1 Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Component not loading | 404 on route | Check `cmp_` prefix |
| Schema changes not reflected | Old values showing | Check `custom.json` or `config.db` |
| Template not rendering | Blank page | Ensure `{:^;:}` at end |
| Form validation failing | Always shows errors | Check `schema.json` rules match fields |
| AJAX not working | Full page reload | Verify `Requested-With-Ajax` header |
| Translation not showing | English text only | Check locale file name and structure |
| Session not persisting | Logged out on refresh | Check cookie settings and domain |

### 11.2 Debug Mode

```python
# In component dispatcher
def __init__(self, request, comp_route, neutral_route=None):
    super().__init__(request, comp_route, neutral_route)

    # Debug output (remove in production)
    if self.schema.properties['config'].get('debug_expire'):
        self.schema_data["debug_info"] = {
            "route": comp_route,
            "session": self.schema_data.get("HAS_SESSION"),
            "user": self.schema_data.get("CURRENT_USER", {}).get("id"),
        }
```

### 11.3 Template Debug

```html
{:* Debug variable output *:}
{:debug; dispatch_result :}
{:debug; local::message :}
{:debug; CONTEXT->POST :}

{:* Debug all schema_data *:}
{:code;
  <pre>{:;__schema_data__:}</pre>
:}
```

### 11.4 Log Messages

```python
# In dispatcher or routes
import logging
logger = logging.getLogger(__name__)

def some_method(self):
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

---

## 12. Production Deployment

### 12.1 Pre-Deployment Checklist

- [ ] Remove `cmp_7000_hellocomp` if not needed
- [ ] Set `ALLOWED_HOSTS` in config
- [ ] Configure `TRUSTED_PROXY_CIDRS` for reverse proxies
- [ ] Set `DEBUG_EXPIRE=0` in production
- [ ] Remove debug BIFs from templates
- [ ] Remove `custom.json` from deployment
- [ ] Verify all translations are complete
- [ ] Run full test suite
- [ ] Run security scan (bandit, pylint)

### 12.2 Environment Variables

```bash
# Production .env
ALLOWED_HOSTS=localhost,*.example.com
TRUSTED_PROXY_CIDRS=10.0.0.0/8,172.16.0.0/12
DEBUG_EXPIRE=0
WSGI_DEBUG_ALLOWED=false
SECRET_KEY=<strong-random-key>
```

### 12.3 Performance Optimization

```json
// schema.json config section
{
  "config": {
    "cache_on_get": true,
    "cache_on_post": false,
    "cache_on_cookies": true,
    "cache_disable": false,
    "filter_all": false,
    "disable_js": true
  }
}
```

### 12.4 Monitoring

```python
# Add monitoring to dispatcher
def __init__(self, request, comp_route, neutral_route=None):
    super().__init__(request, comp_route, neutral_route)

    # Log request start
    import time
    self._start_time = time.time()

def __del__(self):
    # Log request duration
    if hasattr(self, '_start_time'):
        duration = time.time() - self._start_time
        if duration > 1.0:  # Log slow requests
            logger.warning(f"Slow request: {duration:.2f}s")
```

---

## 13. Usage Examples

### 13.1 Create a New Component

**Prompt:**
```
Please create a new component called "Dashboard" with:
- UUID: dashboard_8x90s
- Route: /dashboard
- Menu entries for both logged-in and logged-out users
- A simple page showing user statistics
- Spanish and English translations
- Basic test suite
```

### 13.2 Modify Existing Component

**Prompt:**
```
Please modify cmp_5100_sign to:
- Add a new route /sign/verify
- Create a dispatcher for email verification logic
- Add form validation for verification codes
- Create templates with proper translations
- Add tests for the new functionality
```

### 13.3 Add Form to Component

**Prompt:**
```
Please add a contact form to my component with:
- Email, name, message fields
- Server-side validation rules in schema.json
- CSRF protection with LTOKEN and FToken
- Success/error message handling
- AJAX submission support
- Rate limiting on POST
```

### 13.4 Create Admin Component

**Prompt:**
```
Please create an admin component with:
- UUID: admin_9x00s
- Route: /admin
- IP restriction to localhost only
- Admin credential check from environment
- No public menu entry
- CSRF protection on all state-changing actions
- Rate limiting on login attempts
- Audit logging for all actions
```

---

## 14. Best Practices Summary

### 14.1 Architecture

1. **Keep components isolated** - No direct dependencies between components
2. **Use UUID for references** - Folder names can change, UUIDs are stable
3. **Follow naming conventions** - `cmp_NNNN_name` for folders, `name_random` for UUIDs
4. **Separate concerns** - Routes for routing, dispatchers for logic, templates for view

### 14.2 Security

1. **Never trust user input** - Always validate and sanitize
2. **Use CONTEXT for data** - Auto-escaped and secure
3. **Implement rate limiting** - Protect against brute force
4. **Use tokens** - LTOKEN for links, FToken for forms, UTOKEN for sessions
5. **CSP compliance** - Nonce for all inline scripts/styles

### 14.3 Performance

1. **Cache appropriately** - Use `{:cache; :}` for expensive operations
2. **Lazy load** - Use AJAX for non-critical content
3. **Minimize queries** - Batch database operations
4. **Optimize templates** - Avoid nested loops in templates

### 14.4 Maintainability

1. **Document everything** - README.md, inline comments, docstrings
2. **Write tests** - Cover all routes and business logic
3. **Use translations** - All UI text should be translatable
4. **Version components** - Follow semantic versioning in manifest.json

---

## 15. Quick Reference

### 15.1 File Templates

See sections 3-5 for complete file templates.

### 15.2 NTPL BIF Reference

| BIF | Purpose | Example |
|-----|---------|---------|
| `{:;var:}` | Output variable | `{:;name:}` |
| `{:;local::var:}` | Output local variable | `{:;local::message:}` |
| `{:trans; text:}` | Translate text | `{:trans; Hello :}` |
| `{:bool; var >> :}` | Boolean conditional | `{:bool; logged_in >> :}` |
| `{:filled; var >> :}` | Has content conditional | `{:filled; items >> :}` |
| `{:each; arr k v >> :}` | Loop through array | `{:each; items key item >> :}` |
| `{:include; file :}` | Include template | `{:include; header.ntpl :}` |
| `{:snip; name >> :}` | Define snippet | `{:snip; my-snippet >> :}` |
| `{:cache; /300/ >> :}` | Cache content | `{:cache; /300/ >> :}` |
| `{:fetch; \|url\|ev\| >> :}` | AJAX fetch | `{:fetch; \|/ajax\|click\| >> :}` |

### 15.3 Dispatcher Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `Dispatcher.__init__()` | Initialize dispatcher | None |
| `dispatch.view.render()` | Render template | Response |
| `dispatch.model.exec()` | Execute database query | dict |
| `dispatch.session.create()` | Create session | dict |
| `dispatch.session.close()` | Close session | dict |
| `dispatch.user.create()` | Create user | dict |
| `dispatch.user.check_login()` | Verify credentials | dict/None |

### 15.4 Schema Data Keys

| Key | Access | Description |
|-----|--------|-------------|
| `CONTEXT` | `{:;CONTEXT->POST->field:}` | Request data |
| `CURRENT_COMP_UUID` | `{:;CURRENT_COMP_UUID:}` | Component UUID |
| `CURRENT_COMP_ROUTE` | `{:;CURRENT_COMP_ROUTE:}` | Component route |
| `CSP_NONCE` | `{:;CSP_NONCE:}` | CSP nonce |
| `LTOKEN` | `{:;LTOKEN:}` | Link token |
| `HAS_SESSION` | `{:;HAS_SESSION:}` | Session flag |
| `CURRENT_USER` | `{:;CURRENT_USER->id:}` | User data |

---

## 16. Additional Resources

- **Official Documentation**: https://franbarinstance.github.io/neutralts-docs/
- **GitHub Repository**: https://github.com/FranBarInstance/neutral-starter-py
- **NTPL Syntax Reference**: `docs/templates-neutrats.md`
- **Dispatcher Documentation**: `docs/dispatcher.md`
- **Component Guide**: `docs/component.md`
- **Model Documentation**: `docs/model.md`

---

*This skill document is comprehensive and should be used as the primary reference for creating or modifying Neutral TS components. Always refer to the latest documentation for updates and changes to the framework.*
```

This comprehensive skill document provides complete guidance for creating and modifying Neutral TS components. It covers all aspects from basic structure to advanced patterns, security, testing, and deployment. The AI can use this skill to:

1. **Create new components** from scratch following best practices
2. **Modify existing components** without breaking functionality
3. **Implement forms** with proper validation and security
4. **Add translations** following the correct scope strategy
5. **Write tests** for component functionality
6. **Debug issues** using the troubleshooting guide
7. **Deploy to production** with proper security configuration

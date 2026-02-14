# Components in Neutral PWA Starter

This directory is the core of project modularity. Components are isolated functional units that can contain server logic, routes, frontend templates, and configuration.

This document details how they work internally, how they interact with the core (Flask + Neutral Templating), and how to extend the application.

---

## 1. Definition and Naming Rules

A component lives in its own folder under `src/component/`.

### Loading rules and prefix
*   **Mandatory prefix**: The directory name must start with `cmp_`. Any folder that does not follow this pattern will be ignored.
*   **Deactivation**: A component can be deactivated simply by renaming its folder, for example, changing `cmp_0500_login` to `_cmp_0500_login`.
*   **Alphabetical Order**: Loading is done in alphabetical order. The number `NNNN` in the name is a useful convention to control this order.

### Priority and Overriding

**General Rule:**
Components are loaded in **alphabetical order**. A subsequent component extends or overrides the functionality of a previous one. This applies to Schema, Templates, Code Snippets, and routes.

A subsequent component with the same route, Schema key (merge), snippet, etc., overrides the previous one.

**Fallback Blueprints (Components starting with `cmp_9`)**
There is an exception for components starting with `cmp_9` (e.g., `cmp_9000_catchall`): their blueprints are not overwritten routes, allowing them to be used as fallbacks or catch-alls.

For all other component elements, such as schemas, snippets, etc., the behavior remains the same, and they will be overwritten.

---

## 2. File Architecture

A typical component (like `cmp_7000_hellocomp`) follows this structure:

```
src/component/cmp_name/
├── manifest.json                         # Registration metadata (UUID, name, route)
├── schema.json                           # Global data, menu, and translations
├── custom.json                           # Local user overrides (DO NOT DISTRIBUTE)
├── __init__.py                           # Main initialization (e.g., sys.path setup)
├── lib/                                  # Internal component libraries
├── static/                               # Component-specific static assets
├── tests/                                # Pytest test suite for the component
├── route/                                # Backend (Python/Flask)
│   ├── __init__.py                       # Blueprint creation & config
│   ├── routes.py                         # Route definitions
│   └── dispatcher_name.py                # Custom Business Logic (optional)
└── neutral/                              # Frontend (NTPL)
    ├── component-init.ntpl               # Global snippets (available app-wide)
    └── route/                            # Component-specific templates
        ├── index-snippets.ntpl           # Snippets shared across this component
        ├── locale.json                   # Translations (merged with schema)
        └── root/                         # Template mapping to routes
            ├── content-snippets.ntpl     # Template for the root route (/)
            └── [subroute]/               # Folder for subroutes (e.g., /test1)
                └── content-snippets.ntpl
```

---

## 3. Loading Life Cycle

When starting the application, the system performs the following steps:

1.  **Discovery**: Scans `src/component/` looking for folders starting with `cmp_`.
2.  **Registration**: Reads `manifest.json`. If `custom.json` exists, its `manifest` section overrides the original.
3.  **Data Merging**: Loads `schema.json`. If `custom.json` exists, its `schema` section is merged. Finally, it's merged into the global application schema.
4.  **Python Initialization**: Executes `init_component` in `__init__.py` (if it exists). This is often used to add the `lib/` directory to `sys.path`.
5.  **Routes**: Executes `init_blueprint` in `route/__init__.py`. This creates the Flask Blueprint and registers routes.
6.  **Global Templates**: Reads `neutral/component-init.ntpl`. Snippets here are registered globally. Evaluate on every request.

---

## 4. Configuration Files

### schema.json

Defines the data structure and configuration. It is divided into critical sections for the operation of the Neutral engine.

*   **config**: Internal engine configuration (cache, debug, etc.).
*   **inherit**: Defines the local context and inheritance tools.
    *   **data**: Variables accessible as `{:;local::varname:}`. Can be dynamically overridden.
    *   **locale**: Translation system.
        *   `current`: Current language.
        *   `trans`: Dictionary of translations.
    *   **snippets**: Definition of initial snippets (Global).
*   **data**: Global variables accessible as `{:;varname:}`. By convention, contains environment information and **cannot be dynamically overridden** at runtime; they are global.

### custom.json

Allows overriding configuration without touching the original code.
**Important Rule**: The component provider must never include this file; it is exclusively for local user customization.

---

## 5. Template System (NTPL)

Neutral Templating allows for code injection and extreme modularity.

### Global Level: `neutral/component-init.ntpl`
Loaded during discovery. It can include snippets, includes, and locales that will be available globally. Although loaded at startup, its content is evaluated on every request.

### Component Level: `neutral/route/index-snippets.ntpl`
Loaded dynamically for all routes served by the component. Ideal for common layouts or shared logic of the module.

### Route Level: `neutral/route/root/[ROUTE]/content-snippets.ntpl`
Contains the specific template for a page.
*   **Convention**: Must define the `current:template:body-main-content` snippet, which is what the main layout will render inside the `<main>` tag.
*   **Note**: The specific templates are located inside the `root/` subdirectory within `neutral/route/`.

---

## 6. Routes and Backend (Flask)

If the component requires server logic, the `route/` folder is used.

### Blueprints (`route/__init__.py`)
Must define `init_blueprint` and use `create_blueprint`. The system automatically sets `bp.neutral_route` to the absolute path of the component's `neutral/route` directory.

### Dispatcher
The `Dispatcher` class connects Flask with NTPL.
Use `core.dispatcher.Dispatcher` (or a subclass).
Signature: `Dispatcher(request, comp_route, neutral_route)`

*   `request`: Flask request object.
*   `comp_route`: Relative route path (e.g., `""` for root, `"test/page"` for subpages).
*   `neutral_route`: Base template directory, usually `bp.neutral_route`.

---

## 7. Guide: Real World Example (Hello Component)

This example is based on `src/component/cmp_7000_hellocomp`, which illustrates the full capabilities of a component.

### 1. Registration (`manifest.json`)
Defines the component's unique identity and its base URL prefix. UUID must be unique and follow the `name_random` format.


```json
{
    "uuid": "hellocomp_0yt2sa",
    "name": "Hello Component",
    "description": "Component example, ilustrates the basic structure of a component",
    "version": "1.0.0",
    "route": "/hello-component"
}
```

### 2. Initialization and Libraries (`__init__.py` & `lib/`)
Components can have their own libraries. Use `init_component` to expose them.

```python
import os
import sys

def init_component(component, component_schema, _schema):
    # Add 'lib' folder to sys.path to allow: from hellocomp_0yt2sa import ...
    lib_path = os.path.join(component['path'], 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
```

### 3. Configuration and Data (`schema.json`)
The `schema.json` file is merged into the global application schema.

To add a menu item, you **must** define both the `drawer` (the top-level tab) and the `menu` (the link items inside the tab). The menu may display different options depending on whether the user is logged in ("session:true") or not ("session:").

```json
{
    "inherit": {
        "locale": {
            "trans": {
                "es": {
                    "Hello Component": "Componente Hola"
                }
            }
        },
        "data": {
            "drawer": {
                "menu": {
                    "session:": {
                        "hello-tab": {
                            "name": "Hello Component",
                            "tabs": "hello-tab",
                            "icon": "x-icon-info"
                        }
                    },
                    "session:true": {
                        "hello-tab": {
                            "name": "Hello Component",
                            "tabs": "hello-tab",
                            "icon": "x-icon-info"
                        }
                    }
                }
            },
            "menu": {
                "session:": {
                    "hello-tab": {
                        "hello": {
                            "text": "Hello Component",
                            "link": "[:;data->hellocomp_0yt2sa->manifest->route:]",
                            "icon": "x-icon-greeting"
                        }
                    }
                },
                "session:true": {
                    "hello-tab": {
                        "hello": {
                            "text": "Hello Component",
                            "link": "[:;data->hellocomp_0yt2sa->manifest->route:]",
                            "icon": "x-icon-greeting"
                        }
                    }
                }
            }
        }
    },
    "data": {
        "hello-component": { "hello": "Hello from hello component" }
    }
}
```

### 4. Blueprint & Routes (`route/`)
Components use Flask Blueprints. The `create_blueprint` utility sets up the prefix and template paths.

**Blueprint (`route/__init__.py`)**:
```python
from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    bp = create_blueprint(component, component_schema)
    from . import routes
```

**Routes (`route/routes.py`)**:
```python
from flask import request
from . import bp
from .dispatcher_hellocomp import DispatcherHelloComp

@bp.route("/")
def index():
    # Dispatcher(request, relative_route, base_template_dir)
    dispatch = DispatcherHelloComp(request, "", bp.neutral_route)
    return dispatch.view.render()
```

### 5. Frontend Templates (NTPL)

**Global Snippets (`neutral/component-init.ntpl`)**:
```html
{:snip; hellocomp-global-header >>
    <div class="alert alert-info">Global Component Snippet</div>
:}
```

**Page Content (`neutral/route/root/content-snippets.ntpl`)**:
The specific view for the root route (`/hello-component`).
```html
{:snip; current:template:body-main-content >>
    <div class="container">
        <h3>{:trans; {:;hello-component->hello:} :}</h3>
        {:snip; hellocomp-global-header :}
    </div>
:}
{:^;:}
```

### 6. Static Files (`static/`)

Assets in the `static/` folder can be served by the component.

```python
STATIC = f"{bp.component['path']}/static"

@bp.route("/<path:route>")
def catch_all(route):
    file_path = os.path.join(STATIC, route)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        return send_from_directory(STATIC, route)
    # ... handle as a template route
```

### 7. Testing (`tests/`)

Components should include their own tests.

```bash
# Run tests for this specific component
pytest src/component/cmp_7000_hellocomp/tests
```

---

## 8. Debugging

*   If a component does not load, check the `cmp_` prefix.
*   If changes in `schema.json` are not reflected, check if an interfering `custom.json` exists.
*   Use `{:;local::varname:}` for mutable data and `{:;varname:}` for immutable request data.

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
├── manifest.json                     # Registration metadata
├── schema.json                       # Global data and inheritance
├── custom.json                       # Local overrides (for users)
├── route/                            # Backend (Python/Flask)
│   ├── __init__.py                   # Blueprint creation
│   └── routes.py                     # Route definitions
└── neutral/                          # Frontend (NTPL)
    ├── component-init.ntpl           # Global snippets (app-wide)
    └── route/                        # Component templates
        ├── index-snippets.ntpl       # Snippets shared by this component
        ├── custom-snippets.ntpl      # Local overrides (for users)
        ├── locale.json               # Translations
        └── root/                     # Pages mapping
            └── content-snippets.ntpl # Main content
```

---

## 3. Loading Life Cycle

When starting the application, the system performs the following steps:

1.  **Discovery**: Scans `src/component/` looking for `cmp_` folders.
2.  **Registration**: Reads `manifest.json`.
3.  **Data Merging**: Loads `schema.json` and merges it with `custom.json` (if it exists) and then with the global schema.
4.  **Python Initialization**: Executes `__init__.py` (main module) if it exists.
5.  **Routes**: Executes `init_blueprint` in `route/__init__.py`.
6.  **Global Templates**: Loads snippets from `neutral/component-init.ntpl`.

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

## 7. Guide: Create a Component from Scratch

Example of creating a "Hello World" component.

1.  **Directory**: `src/component/cmp_9900_hola`

2.  **Manifest (`manifest.json`)**:
    ```json
    {
        "uuid": "hola_x1y2z3",
        "name": "Hello World",
        "description": "Simple example",
        "version": "1.0.0",
        "route": "/hola"
    }
    ```

3.  **Translations (`schema.json`)**:
    ```json
    {
        "inherit": {
            "locale": {
                "trans": {
                    "es": { "Greeting": "Saludos Terrestre" },
                    "en": { "Greeting": "Greetings Earthling" }
                }
            }
        }
    }
    ```

4.  **Backend (`route/__init__.py`)**:
    ```python
    from app.components import create_blueprint

    def init_blueprint(component, component_schema, _schema):
        bp = create_blueprint(component, component_schema)
        # Import routes to register them
        from . import routes
        return bp
    ```

5.  **Routes (`route/routes.py`)**:
    ```python
    from flask import request
    from core.dispatcher import Dispatcher
    from . import bp

    @bp.route('/')
    def index():
        # Dispatcher will look in neutral/route/root/
        return Dispatcher(request, "", bp.neutral_route).view.render()
    ```

6.  **Global Template (`neutral/component-init.ntpl`)**:
    ```html
    {:snip; hola-menu-item >>
        <a href="/hola" class="nav-link">{:trans; Greeting :}</a>
    :}
    ```

7.  **View (`neutral/route/root/content-snippets.ntpl`)**:
    *(Note the `root` folder)*
    ```html
    {:snip; current:template:body-main-content >>
        <h1>{:trans; Greeting :}</h1>
    :}
    ```

---

## 8. Debugging

*   If a component does not load, check the `cmp_` prefix.
*   If changes in `schema.json` are not reflected, check if an interfering `custom.json` exists.
*   Use `{:;local::varname:}` for mutable data and `{:;varname:}` for immutable request data.

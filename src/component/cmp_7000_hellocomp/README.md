# Hello Component

This module is the reference implementation for components in the **Neutral PWA** framework. It demonstrates the complete lifecycle, from identity and registration to advanced backend logic, frontend templating, and integrated testing.

## 1. Identity and Registration

*   **Identifier (UUID)**: `hellocomp_0yt2sa` (Must be unique and follow the `name_random` format).
*   **Base Path**: `/HelloComponent` (Defined in `manifest.json`).
*   **Version**: `0.0.0`
*   **Default Route**: `/hello-component` (Defined in `manifest.json`)
*   **Active Route**: `/HelloComponent` (Overridden in `custom.json` for demonstration)

### Registration Lifecycle
1.  **Discovery**: The engine identifies the folder via the `cmp_` prefix.
2.  **Manifest Processing**: Reads `manifest.json` for metadata.
3.  **Path Manipulation**: `__init__.py` adds the `lib/` directory to `sys.path`.
4.  **Configuration Merging**: `schema.json` is merged into the global schema. `custom.json` provides the final layer of overrides.
5.  **Blueprint Initialization**: `route/__init__.py` creates the Flask Blueprint and links it to the `neutral/route` template directory.

## 2. File Architecture

```text
src/component/cmp_7000_hellocomp/
├── __init__.py                       # Component entry point & sys.path setup
├── manifest.json                     # Registration metadata
├── schema.json                       # Global data, menu entries, and locales
├── custom.json                       # Local overrides (overwrites manifest/schema)
├── lib/                              # Private Python libraries
│   └── hellocomp_0yt2sa/             # Namespaced library package
├── src/                              # Backend logic snippets
│   └── comp.py                       # Python logic called by the template engine
├── route/                            # Flask Backend
│   ├── __init__.py                   # Blueprint & Template setup
│   ├── routes.py                     # Endpoint definitions
│   └── dispatcher_hellocomp.py       # Custom Dispatcher with business logic
├── neutral/                          # Frontend (NTPL)
│   ├── component-init.ntpl           # Global snippets (available app-wide)
│   ├── obj/                          # Template-to-Python object mappings
│   │   └── comp.json                 # Maps a template call to src/comp.py
│   └── route/                        # Templates matching the URL structure
│       ├── data.json                 # Shared metadata for the route tree
│       ├── index-snippets.ntpl       # Shared snippets and localized file loader
│       ├── locale-*.json             # Language-specific translations
│       └── root/                     # Template root for the component
│           ├── content-snippets.ntpl # Main content for the base route
│           ├── test1/                # Logic/Templates for /test1
│           └── test2/                # Static templates for /test2
├── static/                           # Static assets (images, etc.)
└── tests/                            # Component-specific tests
    ├── conftest.py                   # Test configuration and fixtures
    └── test_hellocomp.py             # Route and Dispatcher verification
```

## 3. High-Level Concepts

### Data Schema and Inheritance (`schema.json`)
The `schema.json` allows a component to "inject" itself into the main application:
*   **`inherit:locale`**: Adds global translations (e.g., menu items).
*   **`inherit:data:drawer:menu`**: Automatically adds links to the sidebar.
*   **`inherit:data:menu`**: Adds links to the main navigation menu.
*   **`data` Section**: Local data namespaced to the component.

### Private Libraries (`lib/`)
The component can package its own dependencies in the `lib/` folder. By adding this folder to `sys.path` in `__init__.py`, the component can use `import hellocomp_0yt2sa` internally without global installation conflicts.

### Python Objects in Templates (`neutral/obj/`)
Using the `{:obj; ... :}` tag, templates can trigger Python logic:
1.  A JSON file in `neutral/obj/` defines the link to a Python file.
2.  The Python file (e.g., `src/comp.py`) returns a dictionary.
3.  The template renders this data dynamically.

### Dynamic Localization
Instead of a single `locale.json`, this component uses a dynamic loader in `index-snippets.ntpl`:
```html
{:locale; #/locale-{:lang;:}.json :}{:else; {:locale; #/locale-en.json :} :}
```

## 4. Backend Logic & Dispatcher

The backend uses a `Dispatcher` pattern to bridge Flask and the NTPL engine. Custom dispatchers (like `DispatcherHelloComp`) inherit from `core.dispatcher.Dispatcher` and allow for custom business logic execution before rendering.

### Custom Dispatcher Features
*   **Context Injection**: Sets values in `self.schema_local_data` (e.g., `'foo': 'bar'`).
*   **Business Logic**: Methods like `test1()` perform calculations or data fetching.

### Routing Strategies
1.  **Explicit Routes**: Use `@bp.route('/path')` for custom logic in `routes.py`.
2.  **Catch-all Routing**: Automatically maps URLs to the folder structure in `neutral/route/root/`.

## 5. Development Guide

### Adding a New Route
1.  **Filesystem-based (Static)**: Create `src/component/cmp_7000_hellocomp/neutral/route/root/my-page/content-snippets.ntpl`.
2.  **Logic-based (Dynamic)**: Add a route in `routes.py`, call a dispatcher method, and create the corresponding folder in `neutral/route/root/`.

### Running Tests
The component includes a `pytest` suite. From the project root, run:
```bash
pytest src/component/cmp_7000_hellocomp/tests
```

## 6. Request Flow Examples

### A. Base Route: `/HelloComponent`
*   **Backend**: Handled by `hellocomp_catch_all` (Generic Dispatcher).
*   **Template**: `neutral/route/root/content-snippets.ntpl`.
*   **Result**: Displays the default homepage.

### B. Custom Route: `/HelloComponent/test1`
*   **Backend**: Handled by `test1` (Uses `DispatcherHelloComp`).
*   **Logic**: `dispatch.test1()` is called, setting `dispatch_result` to `True`.
*   **Template**: `neutral/route/root/test1/content-snippets.ntpl`.

### C. Automatic Sub-route: `/HelloComponent/test2`
*   **Backend**: Captured by the catch-all regex.
*   **Template**: Automatically maps to `neutral/route/root/test2/`.

# Hello Component

This module is an example component designed to illustrate the modular architecture of the **Neutral PWA** framework. It serves as a reference for creating new components and follows the specifications defined in the core documentation.

## 1. Identity and Registration

*   **Identifier (UUID)**: `hellocomp_0yt2sa` (Must be unique and follow the `name_random` format).
*   **Base Path**: `/HelloComponent` (Defined in `manifest.json`).
*   **Version**: `0.0.0`

### Registration Lifecycle
1.  **Manifest Processing**: The system reads `manifest.json` to identify the component and its base route.
2.  **Configuration Merging**: `schema.json` is loaded and merged into the global application schema. If `custom.json` exists, it can override values.
3.  **Route Initialization**: The `route/__init__.py` file initializes the Flask Blueprint and sets up the template directories.

## 2. File Architecture

```
src/component/cmp_7000_hellocomp/
├── manifest.json                     # Registration metadata
├── schema.json                       # Global data and inheritance
├── custom.json                       # Local overrides
├── route/                            # Backend (Python/Flask)
│   ├── __init__.py                   # Blueprint & Template setup
│   ├── routes.py                     # Endpoints
│   └── dispatcher_hellocomp.py       # Custom business logic
└── neutral/                          # Frontend (NTPL)
    ├── component-init.ntpl           # (Optional) Global snippets for all app
    └── route/                        # Templates matching URL structure
        ├── index-snippets.ntpl       # (Optional) Shared snippets for this component
        ├── locale.json               # (Optional) Component-wide translations
        ├── data.json                 # (Optional) Shared data for the route tree
        └── root/                     # Templates
            ├── data.json             # (Optional) Route-specific metadata
            ├── locale.json           # (Optional) Translations for this route
            ├── content-snippets.ntpl # (Required or 404) Main content for /HelloComponent
            ├── test1/                # Templates for /HelloComponent/test1
            └── test2/                # Templates for /HelloComponent/test2
```

## 3. Data Schema and Inheritance (`schema.json`)

The `schema.json` file is powerful because it allows a component to "inject" itself into the main application.

*   **`inherit` Section**: Anything here is merged into the global schema.
    *   **`locale`**: Adds translations that are available globally.
    *   **`data:drawer:menu`**: Automatically adds links to the application's sidebar.
    *   **`data:menu`**: Adds links to the main navigation menu.
*   **`data` Section**: Local data namespaced by the component's UUID (or a custom name). In this component, it defines `hello-component` data accessible via `{:;hello-component->... :}`.

## 4. Backend Logic (`route/`)

The backend uses a `Dispatcher` pattern to bridge Flask and the NTPL engine.

### The Dispatcher (`dispatcher_hellocomp.py`)
Custom dispatchers inherit from `core.dispatcher.Dispatcher`. They must now accept `comp_route` and `neutral_route`.

```python
class DispatcherHelloComp(Dispatcher):
    def __init__(self, request, comp_route, neutral_route=None):
        super().__init__(request, comp_route, neutral_route)
        # Custom logic here
        self.schema_local_data['foo'] = "bar"
```

They have access to:
*   `self.req`: The Flask request object.
*   `self.schema_data`: A dictionary where you can inject data to be used in templates.
*   `self.view`: The template engine instance.

### Routing Strategies (`routes.py`)
1.  **Explicit Routes**: Use `@bp.route('/path')` for custom logic.
    ```python
    @bp.route('/test1', defaults={"route": "test1"}, methods=["GET"])
    def test1(route):
        # We pass the route and the neutral_route to the Dispatcher
        dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
        dispatch.schema_data['dispatch_result'] = dispatch.test1()
        return dispatch.view.render()
    ```
2.  **Catch-all Routing**: Automatically maps any other URL to the folder structure in `neutral/route/root/`.

## 5. Frontend Templating (NTPL)

### Key Syntax
*   **Data Access**: `{:;key->subkey:}` (e.g., `{:;hello-component->hello:}`).
*   **Translations**: `{:trans; Text to translate :}` (uses `locale.json`).
*   **Snippets**:
    *   **Define**: `{:snip; name >> content :}`
    *   **Use**: `{:snip; name :}`
*   **Main Content**: Every page must define the `current:template:body-main-content` snippet.

### File Hierarchy
1.  `neutral/route/index-snippets.ntpl`: Loaded for every route in the component. Good for shared `{:locale; ... :}` or common UI fragments.
2.  `neutral/route/root/<path>/content-snippets.ntpl`: Specific content for the requested URL.

## 6. Request Flow Examples

Each route in the component follows a flow determined by whether it uses a custom dispatcher or the generic one. The system automatically appends `root` (defined in `Config.COMP_ROUTE_ROOT`) to the route path to find templates.

### A. Base Route: `/HelloComponent`
*   **Trigger**: User accesses the base URL of the component.
*   **Backend**: Handled by `hellocomp_catch_all` in `routes.py` (Generic Dispatcher).
*   **Dispatcher**: Received `route=""`. Constructs `comp_route="root"`.
*   **Template Resolution**:
    1.  Looks for templates in `neutral/route/root/`.
    2.  Loads `data.json` for base metadata.
    3.  Renders `content-snippets.ntpl`.
*   **Result**: Displays the default component homepage.

### B. Custom Route: `/HelloComponent/test1`
*   **Trigger**: User accesses a specific endpoint requiring custom Python logic.
*   **Backend**: Handled by `test1` in `routes.py` using `DispatcherHelloComp`.
*   **Dispatcher**: Received `route="test1"`. Constructs `comp_route="root/test1"`.
*   **Execution**:
    1.  `DispatcherHelloComp` is instantiated with `bp.neutral_route`.
    2.  `dispatch.schema_data['dispatch_result']` is set via `dispatch.test1()`.
*   **Template Resolution**:
    1.  Looks for templates in `neutral/route/root/test1/`.
    2.  Loads `data.json` from the `test1` folder.
    3.  Renders `content-snippets.ntpl` from the `test1` folder.
*   **Result**: Displays content enriched with data injected from the Python backend.

### C. Generic Sub-route: `/HelloComponent/test2`
*   **Trigger**: User accesses a sub-path that has no explicit Flask route.
*   **Backend**: Captured by the `hellocomp_catch_all` regex in `routes.py`.
*   **Dispatcher**: Received `route="test2"`. Constructs `comp_route="root/test2"`.
*   **Template Resolution**:
    1.  Automatically maps the path to `neutral/route/root/test2/`.
    2.  Loads local `data.json` and renders `content-snippets.ntpl`.
*   **Result**: Displays the page content based purely on file structure, without extra Python code.

## 7. Development Guide: Adding a New Route

To add a new sub-route `/HelloComponent/my-page`:

1.  **Create the directory**: `mkdir -p src/component/cmp_7000_hellocomp/neutral/route/root/my-page`
    *(Note the `root` directory in the path)*
2.  **Define metadata**: Create `data.json` in that directory:
    ```json
    {
        "data": {
            "current": {
                "route": {
                    "title": "Page title",
                    "description": "Page description",
                    "h1": "H1 title"
                }
            }
        }
    }
    ```
3.  **Create the content**: Create `content-snippets.ntpl`:
    ```html
    {:snip; current:template:body-main-content >>
        <div class="container">
            <h1>Dynamic Content</h1>
            <p>This is my new page.</p>
        </div>
    :}
    ```
4.  **Optional Python Logic**: If you need backend processing, add an explicit route in `routes.py` and create a matching folder in `neutral/route/root/`. If you don't need Python, the **Catch-all** handler will find your new folder automatically.

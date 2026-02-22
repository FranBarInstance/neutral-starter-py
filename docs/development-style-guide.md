# Routes and Templates in Neutral TS: Style Guide

This guide compiles best practices and lessons learned on how to organize routes (Backend with `flask`) and templates (Frontend with `.ntpl`) when developing components for the Neutral TS framework. It should be used as a reference alongside [manage-component](../.agent/skills/manage-component/SKILL.md) and [manage-neutral-templates](../.agent/skills/manage-neutral-templates/SKILL.md).

---

## 1. The Route Controller (`routes.py`)

The `routes.py` file is **exclusively** the logical router that associates an access point (Flask) with the underlying custom dispatcher. **No business logic, validation rules, or database access should reside in this file**.

### 1.1 Strict Division of Route Handlers
There are two main strategies for defining route handlers depending on the complexity of your component.

#### Simple components (Single Dispatcher)
For simple use cases, you define two separate handlers: one for the root, and a general `catch-all` that delegate to a single generic dispatcher.

```python
# src/component/cmp_0000_example/route/routes.py
from flask import Response, request
from . import bp
from .dispatcher_example import DispatcherExample

@bp.route("/", methods=["GET", "POST"])
def index() -> Response:
    """Explicit handler for the component's route root."""
    dispatch = DispatcherExample(request, "", bp.neutral_route)
    return dispatch.render_route()

@bp.route("/<path:route>", methods=["GET", "POST"])
def default_handler(route) -> Response:
    """Default handler (catch-all) for any other sub-route within the component."""
    dispatch = DispatcherExample(request, route, bp.neutral_route)
    return dispatch.render_route()
```

#### Complex components (Multiple Specialized Dispatchers)
When a component has many distinct business flows (like forms, data processing, etc.), **avoid creating a monolithic dispatcher map over the `route` string**. Instead, define specialized handlers for specific endpoints and delegate the execution to specific dispatcher subclasses.

```python
# src/component/cmp_0000_complex_example/route/routes.py (Example excerpt)
from flask import Response, request
from . import bp
from .dispatcher_form_item import DispatcherFormCreateItem, DispatcherFormEditItem

@bp.route("/create/form/<ltoken>", defaults={"route": "create/form"}, methods=["POST"])
def create_item_form_post(route, ltoken) -> Response:
    """Explicitly map Item Creation logic to the DispatcherFormCreateItem subclass."""
    dispatch = DispatcherFormCreateItem(request, route, bp.neutral_route, ltoken, "create_form", "item_id")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.view.render()

@bp.route("/edit/form/<ltoken>", defaults={"route": "edit/form"}, methods=["POST"])
def edit_item_form_post(route, ltoken) -> Response:
    """Explicitly map Item Editing logic to the DispatcherFormEditItem subclass."""
    dispatch = DispatcherFormEditItem(request, route, bp.neutral_route, ltoken, "edit_form", "item_id")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.view.render()
```

---

## 2. The Custom Dispatcher (`dispatcher_*.py`)

Neutral TS's structure delegates all authorization, database checks, and the creation of the context for our frontend templates to a delegated class known as a `Custom Dispatcher` that inherits from the base `Dispatcher` or derivatives (e.g. `DispatcherForm`).

### 2.1 Provide Omnipresent Local Variables Early
If you are using the single dispatcher pattern (for multiple sub-routes like `/`, `/profile`, `/settings`), they often all need to rely on common state variables (such as a session flag, base permissions, or CSRF tokens).

When populating the global property (`self.schema_data["my_component"]`) in the `render_route()` method, you must ensure you supply the structural variables that will apply to all sub-routes **before** returning conditionally by route.

```python
# src/component/cmp_0000_example/route/dispatcher_example.py
from flask import Response
from core.dispatcher import Dispatcher

class DispatcherExample(Dispatcher):
    def render_route(self) -> Response:

        # 1. Resolve global/omnipresent state (e.g. Auth, CSRF Token)
        state = {
            "auth_ok": self._auth_ok(),
            "errors": []
        }

        # 2. Assign final state to schema_data at a common return point.
        # This ensures that *all* NTPL sub-routes will have, for
        # example, my_comp->auth_ok available.
        self.schema_data["my_comp"] = state

        # 3. Detect which route we are on and execute specifics if needed
        # Overly complex component logic here indicates you should move to
        # the multiple specialized dispatchers pattern (see above section 1.1).
        current = (self._raw_route or "").strip("/")
        if current == "":
            self._handle_root_logic(state)

        return self.view.render()
```

---

## 3. Global Templates and *Snippets*

To achieve maximum re-use of rendered code and respect the *DRY* principle in Neutral TS templates, we use the "Snippets" system (marked with `{:snip; name >> ... :}`).

### 3.1 `index-snippets.ntpl` defines global blocks
Any interface fragment that transversely serves multiple areas or sub-routes (e.g. a general login form blocking routes, repetitive listings, modals) should NOT be replicated.

The root file with global scope to the component must be `src/component/cmp_0000_example/neutral/route/index-snippets.ntpl`:

```html
{:* src/component/cmp_0000_example/neutral/route/index-snippets.ntpl *:}

{:* Load locales (Languages) *:}
{:locale;
    #/locale-{:lang;:}.json
:}

{:* Global form macro, rendered only on demand *:}
{:snip; my-general-login-form >>
    <form method="post" class="card mt-3">
        ... All html markup, hidden inputs, etc...
    </form>
:}
```

### 3.2 Usage with Conditional Flow Control in `content-snippets.ntpl`
Then, the terminal views (a child template in a specific subdirectory) consume this global snippet instead of hosting raw code. Ideally they do this by evaluating the structural properties of the Dispatcher mounted in `schema_data` using NTPL language's own advanced conditionals (`{:bool; var >> ... :}{:else; ... :}`).

For example, conditioning the display of its own content or the Login snippet:

```html
{:* src/component/cmp_0000_example/neutral/route/root/settings/content-snippets.ntpl *:}

{:snip; current:template:body-main-content >>
    <div class="my-container">
        {:!bool; my_comp->auth_ok >>

            {:* User is NOT authorized. Invokes the general access snippet: *:}
            {:snip; my-general-login-form :}

        :}{:else;

            {:* User IS authorized. Shows original content: *:}
            <h2>Personal Settings</h2>
            <!-- Rest of HTML content and macros specific to this route -->

        :}
    </div>
:}
{:^;:}
```

### Summary of best practices

1. Decouple `routes.py` by isolating the Controller in its own `dispatcher_*.py`.
2. Create pure Flask handlers (one for the root, specific ones when needed, and one for `catch-all`), but delegating to a single Dispatcher function or mapping them cleanly.
3. Pre-calculate the base variables that affect multiple sub-directions and store them in `schema_data` deterministically so that any route can access them.
4. Large transversal fragments (like forms) should be encapsulated with `{:snip; name >> ... :}` in the transversal and upper file `index-snippets.ntpl`.
5. The final route templates invoke the snippets conditionally through template block control (e.g. evaluating booleans injected by the backend in `schema_data`).

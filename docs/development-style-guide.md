# Development Style Guide

## 1. Flask Routes Pattern (`routes.py`)

The `routes.py` file is **exclusively** the logical router that associates an access point (Flask) with the underlying custom request handler. **No business logic, validation rules, or database access should reside in this file**.

### 1.1 Route Handler Patterns

#### Simple components (Single RequestHandler)
For simple use cases, you define two separate handlers: one for the root, and a general `catch-all` that delegate to a single generic handler.

```python
# src/component/cmp_0000_example/route/routes.py

from flask import Response, g
from core.request_handler import RequestHandler
from . import bp


@bp.route("/", defaults={"route": ""}, methods=["GET"])
def index(route) -> Response:
    """Explicit handler for the component's route root."""
    handler = RequestHandler(g.pr, "", bp.neutral_route)
    return handler.render_route()


@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Default handler (catch-all) for any other sub-route within the component."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
```

#### Complex components (Multiple Specialized Handlers)
When a component has many distinct business flows (like forms, data processing, etc.), **avoid creating a monolithic handler map over the `route` string**. Instead, define specialized handlers for specific endpoints and delegate the execution to specific handler subclasses.

```python
# src/component/cmp_0000_example/route/routes.py

from flask import Response, g
from core.request_handler_form import FormRequestHandler
from . import bp
from .form_item_handler import FormCreateItemHandler, FormEditItemHandler


def create_item_form_post(route, ltoken) -> Response:
    """Explicitly map Item Creation logic to the FormCreateItemHandler subclass."""
    handler = FormCreateItemHandler(g.pr, route, bp.neutral_route, ltoken, "create_form")
    handler.schema_data["form_result"] = handler.form_post()
    return handler.render_route()


def edit_item_form_post(route, ltoken) -> Response:
    """Explicitly map Item Editing logic to the FormEditItemHandler subclass."""
    handler = FormEditItemHandler(g.pr, route, bp.neutral_route, ltoken, "edit_form")
    handler.schema_data["form_result"] = handler.form_post()
    return handler.render_route()
```

---

## 2. The Custom Request Handler (`*_handler.py`)

Neutral TS's structure delegates all authorization, database checks, and the creation of the context for our frontend templates to a delegated class known as a `Custom RequestHandler` that inherits from the base `RequestHandler` or derivatives (e.g. `FormRequestHandler`).

### 2.1 Provide Omnipresent Local Variables Early
If you are using the single handler pattern (for multiple sub-routes like `/`, `/profile`, `/settings`), they often all need to rely on common state variables (such as a session flag, base permissions, or CSRF tokens).

Pre-calculate these at the end of your constructor and store them directly in `schema_data` or `schema_local_data` so they are available in all sub-routes.

```python
# src/component/cmp_0000_example/route/example_handler.py
from core.request_handler import RequestHandler

class ExampleRequestHandler(RequestHandler):
    def __init__(self, prepared_request, comp_route, neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        # Pre-calculate common state
        self.schema_data["has_session"] = self.schema_data.get("HAS_SESSION") == "true"
        self.schema_data["current_user_id"] = self.schema_data.get("CURRENT_USER", {}).get("id")

    def render_route(self):
        # Route-specific logic can access pre-calculated state
        current = (self.comp_route or "").strip("/")

        # Add route-specific data
        if current == "profile":
            self.schema_data["profile_data"] = self._load_profile()

        return super().render_route()
```

**Rule of Thumb:** If you find yourself writing multiple `if/elif` blocks checking the same condition in `render_route()`, move that logic to the constructor.

---

## 3. State Management Between Handler and Templates

### 3.1 Provide Structural Properties in `schema_data`
The `schema_data` dictionary is the primary bridge between Python handlers and NTPL templates.

**Handler Side (Python):**
```python
class DashboardHandler(RequestHandler):
    def load_dashboard(self):
        self.schema_data["dashboard"] = {
            "show_admin_panel": self._user_is_admin(),
            "pending_count": self._get_pending_count(),
            "recent_items": self._get_recent_items(),
        }
```

**Template Side (NTPL):**
```html
{:struct; dashboard :}
<div class="dashboard">
  {:bool; dashboard->show_admin_panel >> :}
    <div class="admin-panel">...</div>
  {:else; :}
  {:/bool;}

  <span>{:; dashboard->pending_count :} items pending</span>
</div>
```

### 3.2 Usage with Conditional Flow Control in `content-snippets.ntpl`
Then, the terminal views (a child template in a specific subdirectory) consume this global snippet instead of hosting raw code. Ideally they do this by evaluating the structural properties of the RequestHandler mounted in `schema_data` using NTPL language's own advanced conditionals (`{:bool; var >> ... :}{:else; ... :}`).

**The Golden Path:**

1. Decouple `routes.py` by isolating the Controller in its own `*_handler.py`.
2. Create pure Flask handlers (one for the root, specific ones when needed, and one for `catch-all`), but delegating to a single RequestHandler function or mapping them cleanly.
3. Pre-calculate the base variables that affect multiple sub-directions and store them in `schema_data` deterministically so that any route can access them.

---

## Summary

| Aspect | Rule |
|--------|------|
| **Routes** | Only routing logic, no business logic |
| **Handlers** | Business logic, database access, state preparation |
| **Templates** | Pure presentation, use `{:struct;}` for handler data |
| **State** | Pre-calculate common state in handler constructor |

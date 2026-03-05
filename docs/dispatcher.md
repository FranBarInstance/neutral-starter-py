# RequestHandler Class — Developer Documentation

## Table of Contents

1. [Overview](#1-overview)
2. [RequestHandler Lifecycle](#2-requesthandler-lifecycle)
3. [Using RequestHandler in Routes](#3-using-requesthandler-in-routes)
4. [FormRequestHandler — Form Handling](#4-formrequesthandler--form-handling)
5. [Security Context](#5-security-context)
6. [Complete Example: HelloComp Component](#6-complete-example-hellocomp-component)

---

## 1. Overview

The `RequestHandler` class is the bridge between Flask route handlers and the Neutral Template rendering engine. It consumes the `PreparedRequest` context (`g.pr`) created in the global `before_request` hook.

> **Note:** This replaces the old `Dispatcher` class. The security and bootstrap logic is now handled by `PreparedRequest` in the global `before_request`.

**Location**: `src/core/request_handler.py`

### Import

```python
from core.request_handler import RequestHandler
```

### Constructor

```python
RequestHandler(prepared_request, comp_route, neutral_route=None)
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prepared_request` | `PreparedRequest` | **Yes** | The prepared request object from `g.pr` |
| `comp_route` | `str` | **Yes** | The relative route path within the component |
| `neutral_route` | `str` or `None` | No | The filesystem path to the component's `neutral/route` directory |

---

## 2. RequestHandler Lifecycle

The request flow has changed with the `PreparedRequest` refactor:

```
HTTP Request
    ↓
Flask before_request (global)
    ↓
PreparedRequest.build() — Security, Auth, Roles checked here
    ↓
If denied → Return 401 (before route handler runs)
    ↓
If allowed → Store in g.pr
    ↓
Route Handler executes
    ↓
RequestHandler(g.pr, route, bp.neutral_route) — Thin adapter
    ↓
Template.render()
    ↓
HTTP Response
```

### Key Differences from Old Dispatcher

| Old (Dispatcher) | New (RequestHandler) |
|------------------|----------------------|
| `Dispatcher(request, route, bp.neutral_route)` | `RequestHandler(g.pr, route, bp.neutral_route)` |
| Security checked in Dispatcher | Security checked in PreparedRequest (before_request) |
| Heavy initialization per route | Thin adapter, reuse PreparedRequest context |
| `self.req` is Flask request | `self.req` is Flask request (from g.pr) |

---

## 3. Using RequestHandler in Routes

### Basic Usage

```python
from flask import Response, g
from core.request_handler import RequestHandler
from . import bp


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all GET requests for this component."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
```

### Custom RequestHandler Subclass

For components with custom business logic:

```python
# src/component/cmp_7000_hellocomp/route/hellocomp_handler.py

from core.request_handler import RequestHandler


class HelloCompRequestHandler(RequestHandler):
    """Custom request handler for Hello Component."""

    def __init__(self, prepared_request, comp_route, neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        # Set default data for all routes
        self.schema_data["foo"] = "bar"

    def test1(self) -> bool:
        """Business logic for test1 route."""
        self.schema_data["test1_result"] = True
        return True
```

```python
# src/component/cmp_7000_hellocomp/route/routes.py

from flask import Response, g
from core.request_handler import RequestHandler
from . import bp
from .hellocomp_handler import HelloCompRequestHandler


@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    """Handle test1 with custom logic."""
    handler = HelloCompRequestHandler(g.pr, route, bp.neutral_route)
    handler.test1()
    return handler.render_route()


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all other routes with base handler."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
```

---

## 4. FormRequestHandler — Form Handling

The `FormRequestHandler` extends `RequestHandler` with form validation capabilities. It replaces the old `DispatcherForm`.

**Location**: `src/core/request_handler_form.py`

### Import

```python
from core.request_handler_form import FormRequestHandler
```

### Constructor

```python
FormRequestHandler(
    prepared_request,
    comp_route,
    neutral_route=None,
    ltoken=None,
    form_name="form"
)
```

### Basic Form Pattern

```python
from flask import Response, g
from core.request_handler_form import FormRequestHandler
from . import bp


@bp.route("/contact", defaults={"route": "contact"}, methods=["GET", "POST"])
def contact(route) -> Response:
    """Handle contact form."""
    handler = FormRequestHandler(g.pr, route, bp.neutral_route, None, "contact_form")

    if handler.req.method == "POST":
        if handler.form_post():
            # Form valid, process data
            return handler.render_route()
    else:
        handler.form_get()

    return handler.render_route()
```

### Custom Form Handler

```python
from core.request_handler_form import FormRequestHandler


class ContactFormHandler(FormRequestHandler):
    """Custom form handler for contact form."""

    def validate_custom(self) -> bool:
        """Add custom validation beyond schema rules."""
        # Custom validation logic
        return True
```

---

## 5. Security Context

The `RequestHandler` provides access to the security context from `PreparedRequest`:

```python
# Access security decision
if handler.pr.allowed:
    # Request passed auth/status/role checks
    pass

# Access current user roles
roles = handler.schema_data.get("CURRENT_USER", {}).get("roles", {})

# Check if user is authenticated
is_authenticated = handler.schema_data.get("CURRENT_USER", {}).get("auth", False)
```

> **Important:** Security checks (auth, status, roles) are now performed in `PreparedRequest` during the global `before_request`. The route handler only executes if all checks pass.

---

## 6. Complete Example: HelloComp Component

### File Structure

```
src/component/cmp_7000_hellocomp/
├── route/
│   ├── __init__.py
│   ├── routes.py              # Flask routes
│   └── hellocomp_handler.py   # Custom handler (optional)
├── neutral/
│   └── route/
│       └── root/
│           └── content-snippets.ntpl
└── manifest.json
```

### route/hellocomp_handler.py

```python
"""Custom request handler for Hello Component."""

from core.request_handler import RequestHandler


class HelloCompRequestHandler(RequestHandler):
    """Hello component request handler."""

    def __init__(self, prepared_request, comp_route, neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        # Set default data available to all routes
        self.schema_data["foo"] = "bar"

    def test1(self) -> bool:
        """Business logic for test1 route."""
        self.schema_data["test1_result"] = True
        return True
```

### route/routes.py

```python
"""Hello Component routes."""

from flask import Response, g
from core.request_handler import RequestHandler
from . import bp
from .hellocomp_handler import HelloCompRequestHandler


@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    """Handle test1 with custom logic."""
    handler = HelloCompRequestHandler(g.pr, route, bp.neutral_route)
    handler.test1()
    return handler.render_route()


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all other routes."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
```

### manifest.json

```json
{
    "uuid": "hellocomp_0yt2sa",
    "name": "Hello Component",
    "route": "/hello-component",
    "security": {
        "routes_auth": {
            "/": false
        },
        "routes_role": {
            "/": ["*"]
        }
    }
}
```

---

## Migration from Dispatcher

### Old Pattern (Dispatcher)

```python
# OLD - DO NOT USE
from core.dispatcher import Dispatcher

def index(route):
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

### New Pattern (RequestHandler)

```python
# NEW - Use this
from flask import g
from core.request_handler import RequestHandler

def index(route):
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
```

### Key Changes

| Aspect | Old | New |
|--------|-----|-----|
| Import | `from core.dispatcher import Dispatcher` | `from core.request_handler import RequestHandler` |
| Constructor | `Dispatcher(request, route, bp.neutral_route)` | `RequestHandler(g.pr, route, bp.neutral_route)` |
| Request object | Pass `request` directly | Use `g.pr.req` internally |
| Security | Checked in Dispatcher | Checked in `before_request` (PreparedRequest) |
| Render | `dispatch.view.render()` | `handler.render_route()` |

---

## See Also

- [component-security.md](component-security.md) - Security configuration
- [component.md](component.md) - Component development guide
- [component-quickstart.md](component-quickstart.md) - Quick start guide

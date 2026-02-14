

# Dispatcher Class — Developer Documentation

## Table of Contents

1. [Overview](#1-overview)
2. [Constructor Parameters](#2-constructor-parameters)
3. [Instance Attributes](#3-instance-attributes)
4. [Basic Usage](#4-basic-usage)
5. [Schema Data](#5-schema-data-schema_data-and-schema_local_data)
6. [Session, User, and Rendering](#6-session-user-and-rendering)
7. [Nonce and Tokens](#7-nonce-and-tokens)
8. [AJAX Requests](#8-ajax-requests)
9. [Deriving the Dispatcher Class](#9-deriving-the-dispatcher-class)
10. [DispatcherForm — Form Handling Subclass](#10-dispatcherform--form-handling-subclass)
11. [Complete Example: HelloComp Component](#11-complete-example-hellocomp-component)
12. [Quick Reference](#12-quick-reference)

---

## 1. Overview

The `Dispatcher` class is the central bridge between Flask route handlers and the Neutral Template rendering engine. Every HTTP request that needs to render a page flows through a `Dispatcher` instance (or a subclass thereof).

Its responsibilities include:

- **Request context initialization**: Parsing the incoming Flask request and mapping it to component routes and template paths.
- **Schema management**: Providing access to global (`schema_data`) and local (`schema_local_data`) data dictionaries that are passed to the template engine.
- **Session handling**: Initializing and managing the user session.
- **Security tokens**: Generating and validating UTOKEN (user tokens), LTOKEN (link tokens), and CSP nonces.
- **Cookie management**: Setting response cookies for session, theme, language, and security tokens.
- **Template rendering**: Exposing the `view` object (a `Template` instance) used to render the final HTTP response.

**Location**: `src/core/dispatcher.py`

**Import**:
```python
from core.dispatcher import Dispatcher
```

---

## 2. Constructor Parameters

```python
Dispatcher(req, comp_route, neutral_route=None, ltoken=None)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `req` | `flask.Request` | **Yes** | The Flask request object for the current HTTP request. Passed directly from the route handler via `request`. |
| `comp_route` | `str` | **Yes** | The relative route path within the component. For a root route, pass `""`. For subroutes, pass the path segment (e.g., `"test1"`, `"settings/profile"`). This value is prefixed with `Config.COMP_ROUTE_ROOT` internally. |
| `neutral_route` | `str` or `None` | No | The absolute filesystem path to the component's `neutral/route` directory. Typically provided via `bp.neutral_route`, which is automatically set when the blueprint is created. When `None`, the dispatcher uses the default neutral route from the schema. |
| `ltoken` | `str` or `None` | No | A link token used for CSRF-like protection on form entry points. Extracted from the URL path (e.g., `/in/form/<ltoken>`). Primarily used by `DispatcherForm` subclasses. |

### Parameter Details

#### `req` — The Flask Request

The full Flask `request` object. The dispatcher reads from it:

- `req.method` — HTTP method (`GET`, `POST`, etc.)
- `req.cookies` — Client cookies (session, utoken, theme, etc.)
- Headers, form data, and other request attributes are parsed by the `Schema` class during initialization.

#### `comp_route` — Component Route

This string identifies which template to load within the component's `neutral/route/root/` directory structure. The dispatcher constructs the full route by combining `Config.COMP_ROUTE_ROOT` with the provided value.

| `comp_route` value | Resolved template path |
|---|---|
| `""` | `neutral/route/root/content-snippets.ntpl` |
| `"test1"` | `neutral/route/root/test1/content-snippets.ntpl` |
| `"settings/profile"` | `neutral/route/root/settings/profile/content-snippets.ntpl` |

#### `neutral_route` — Template Base Directory

This is the absolute path to the component's template directory. It tells the rendering engine where to find the `content-snippets.ntpl` files. Typically obtained from the blueprint:

```python
dispatch = Dispatcher(request, route, bp.neutral_route)
```

`bp.neutral_route` is automatically set by `create_blueprint()` to point to `<component_path>/neutral/route`.

#### `ltoken` — Link Token

A token embedded in URLs to validate that the user arrived at a form through the expected link flow. It is validated against the current `UTOKEN`. This parameter is primarily consumed by `DispatcherForm` and its subclasses.

---

## 3. Instance Attributes

After construction, a `Dispatcher` instance exposes the following attributes:

| Attribute | Type | Description |
|---|---|---|
| `req` | `flask.Request` | The original Flask request object. |
| `schema` | `Schema` | The full schema object containing all configuration, data, and template engine properties. |
| `schema_data` | `dict` | **Global data dictionary** (`schema.properties['data']`). Values are immutable from the template side (accessed via `{:;varname:}`). Use this for request-scoped data that templates read but cannot override. |
| `schema_local_data` | `dict` | **Local/inheritable data dictionary** (`schema.properties['inherit']['data']`). Values are mutable from the template side (accessed via `{:;local::varname:}`). Use this for data that templates may override or extend. |
| `ajax_request` | `bool` or `str` | Indicates whether the request was made via AJAX. Determined by the `Requested-With-Ajax` custom header. `False` if not an AJAX request. |
| `session` | `Session` | Session manager instance. Provides methods for session creation, retrieval, and destruction. |
| `user` | `User` | User manager instance. Provides methods for user lookup, authentication, and creation. |
| `view` | `Template` | Template/rendering engine instance. Exposes `render()`, `add_cookie()`, and access to the response object. |

### Automatically Set Schema Data Keys

During initialization, the dispatcher automatically populates several keys in `schema_data`:

| Key | Description |
|---|---|
| `CURRENT_COMP_ROUTE` | Full component route (e.g., `root/test1`). |
| `CURRENT_COMP_ROUTE_SANITIZED` | Same as above but with `/` replaced by `:` (e.g., `root:test1`). |
| `CURRENT_NEUTRAL_ROUTE` | Filesystem path to the component's neutral route directory. |
| `CURRENT_COMP_NAME` | Component directory name (e.g., `cmp_7000_hellocomp`). |
| `CURRENT_COMP_UUID` | Component UUID from the manifest (e.g., `hellocomp_0yt2sa`). |
| `CONTEXT` | Dictionary with request context: `SESSION`, `HEADERS`, `POST`, `GET`, `PATH`, `METHOD`, `UA`, `LANGUAGE`, etc. |
| `HAS_SESSION` | `"true"` if a session is active, `None` otherwise. |
| `HAS_SESSION_STR` | `"true"` or `"false"` string. |
| `CSP_NONCE` | A unique nonce string for Content Security Policy inline scripts/styles. |
| `LTOKEN` | A freshly generated link token derived from the current UTOKEN. |
| `COMPONENTS_MAP_BY_NAME` | Map of component names to their UUIDs. |

---

## 4. Basic Usage

The simplest usage of the `Dispatcher` is in a catch-all route that renders a template without any custom business logic.

### Minimal Route Example

```python
# src/component/cmp_7000_hellocomp/route/routes.py

from flask import Response, request
from core.dispatcher import Dispatcher
from . import bp

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all GET requests for this component."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

### What Happens Internally

1. The `Dispatcher` constructor receives the Flask `request`, the relative route, and the template base path.
2. It initializes the `Schema`, `Session`, `User`, and `Template` objects.
3. `_set_current_comp()` resolves the current component name and UUID from the neutral route path.
4. `common()` runs shared initialization:
   - Retrieves or creates the session.
   - Generates a CSP nonce.
   - Parses and updates the UTOKEN.
   - Generates a new LTOKEN.
   - Sets response cookies (session, theme, language, tab detection).
5. `dispatch.view.render()` processes the Neutral templates and returns a Flask `Response`.

### Adding Data to Templates

You can inject data into templates by writing to `schema_data` (global/immutable in templates) or `schema_local_data` (local/mutable in templates):

```python
@bp.route("/", defaults={"route": ""}, methods=["GET"])
def index(route) -> Response:
    dispatch = Dispatcher(request, route, bp.neutral_route)

    # Global data — accessed in templates as {:;greeting:}
    dispatch.schema_data["greeting"] = "Hello, World!"

    # Local data — accessed in templates as {:;local::message:}
    dispatch.schema_local_data["message"] = "This can be overridden by templates"

    return dispatch.view.render()
```

### Setting a Dispatch Result

A common pattern is to set a `dispatch_result` flag that templates can use to branch rendering logic:

```python
dispatch.schema_data["dispatch_result"] = True
return dispatch.view.render()
```

In the template:
```
{:bool; dispatch_result >>
    <p>Operation was successful.</p>
:}
{:!bool; dispatch_result >>
    <p>Something went wrong.</p>
:}
```

Or:
```
{:bool; dispatch_result >>
    <p>Operation was successful.</p>
:}{:else; dispatch_result >>
    <p>Something went wrong.</p>
:}
```

---

## 5. Schema Data: `schema_data` and `schema_local_data`

Understanding the difference between these two data dictionaries is critical for correct component development.

### `dispatch.schema_data` — Global Immutable Data

- **Python path**: `schema.properties['data']`
- **Template access**: `{:;varname:}` or `{:;object->key:}`
- **Mutability**: Can be set from Python code. **Cannot** be dynamically overridden by templates at runtime.
- **Use case**: Request context, environment variables, security tokens, component manifests, dispatch results, and any data that must remain consistent throughout the entire rendering pipeline.

```python
# Python
dispatch.schema_data["page_title"] = "Dashboard"
dispatch.schema_data["items"] = {"count": 42, "label": "widgets"}
```

```
<!-- Template (NTPL) -->
<h1>{:;page_title:}</h1>
<p>{:;items->count:} {:;items->label:}</p>
```

#### Key Conventions for `schema_data`

| Key Pattern | Purpose |
|---|---|
| `CONTEXT` | Request metadata (headers, POST, GET, session, etc.). Auto-escaped in templates. |
| `CURRENT_COMP_*` | Current component identification. |
| `CSP_NONCE` | Content Security Policy nonce. |
| `LTOKEN` | Link token for form CSRF protection. |
| `HAS_SESSION` / `HAS_SESSION_STR` | Session state flags. |
| `dispatch_result` | Convention: boolean result of business logic. |
| `core` | Core configuration data (forms, validation rules, etc.). |
| `COMPONENTS_MAP_BY_NAME` | Component name → UUID mapping. |
| `<component_uuid>` | Component-specific manifest and schema data. |

### `dispatch.schema_local_data` — Local Mutable Data

- **Python path**: `schema.properties['inherit']['data']`
- **Template access**: `{:;local::varname:}` or `{:;local::object->key:}`
- **Mutability**: Can be set from Python code **and** can be overridden by templates at runtime (via `{:data; ... :}` in NTPL).
- **Use case**: Theme settings, menu configuration, per-route content data, and any data that templates may need to customize.

```python
# Python
dispatch.schema_local_data["message"] = "Default message"
dispatch.schema_local_data["sidebar_visible"] = "true"
```

```
<!-- Template (NTPL) -->
<p>{:;local::message:}</p>

{:bool; local::sidebar_visible >>
    {:snip; sidebar-content :}
:}
```

#### Common `schema_local_data` Keys

| Key | Purpose |
|---|---|
| `current` | Current route/theme configuration (often loaded from `data.json` files). |
| `drawer` | Navigation drawer configuration. |
| `menu` | Menu items configuration. |
| `foo` (custom) | Any component-specific local data. |

### Comparison Summary

| Aspect | `schema_data` | `schema_local_data` |
|---|---|---|
| Template syntax | `{:;varname:}` | `{:;local::varname:}` |
| Set from Python | ✅ Yes | ✅ Yes |
| Overridden by templates | ❌ No | ✅ Yes |
| Typical content | Context, tokens, flags | Theme, menu, route data |
| Security-sensitive | Yes (tokens, session) | No (display data) |

### Accessing Nested Data

Both dictionaries support nested object access in templates:

```python
dispatch.schema_data["user_info"] = {
    "name": "Alice",
    "role": "admin",
    "prefs": {"theme": "dark"}
}
```

```
<!-- Template -->
{:;user_info->name:}              <!-- Alice -->
{:;user_info->prefs->theme:}      <!-- dark -->
```

---

## 6. Session, User, and Rendering

### Session (`dispatch.session`)

The `Session` object manages server-side session state. It is initialized from `schema_data['CONTEXT']['SESSION']` (which comes from the session cookie).

| Method | Description |
|---|---|
| `session.get()` | Returns a tuple `(session_id, session_cookie_dict)`. The session ID is a string if active, or `None` if no session exists. |
| `session.create(user_id, session_ua, session_data)` | Creates a new session. Returns a cookie dictionary to be added to the response. |
| `session.close()` | Destroys the current session. Returns a cookie dictionary to clear the session cookie. |

#### Checking Session State in Python

```python
dispatch = Dispatcher(request, route, bp.neutral_route)

if dispatch.schema_data["HAS_SESSION"]:
    # User is logged in
    pass
else:
    # No active session
    pass
```

#### Checking Session State in Templates

```
{:bool; HAS_SESSION >>
    <p>Welcome back!</p>
:}
{:!bool; HAS_SESSION >>
    <p>Please sign in.</p>
:}
```

The purpose of HAS_SESSION_STR is to perform dynamic evaluation:
```
{:snip; session:true >>
    <p>Welcome back!</p>
:}

{:snip; session:false >>
    <p>Please sign in.</p>
:}

{:snip; session:{:;HAS_SESSION_STR:} :}
```

### User (`dispatch.user`)

The `User` object provides methods for user data operations:

| Method | Description |
|---|---|
| `user.get_user(email)` | Look up a user by email. |
| `user.check_login(email, password, pin)` | Verify credentials. Returns user data or `None`. |
| `user.create(user_data)` | Create a new user account. |
| `user.user_reminder(user_data)` | Generate a password reminder. |

The `User` object is typically used in `DispatcherForm` subclasses for authentication flows, but is available on the base `Dispatcher` for any component that needs user data.

### Rendering (`dispatch.view`)

The `Template` object handles response construction and rendering.

| Method / Attribute | Description |
|---|---|
| `view.render()` | Processes all templates and returns a `flask.Response`. |
| `view.add_cookie(cookie_dict)` | Adds cookies to the response. Accepts a dictionary of cookie definitions. |
| `view.response` | The underlying Flask `Response` object. Can be used to set custom headers. |

#### Setting Custom Response Headers

```python
dispatch = Dispatcher(request, route, bp.neutral_route)
dispatch.view.response.headers["Cache-Control"] = "public, max-age=3600"
return dispatch.view.render()
```

#### Adding Custom Cookies

```python
dispatch.view.add_cookie({
    "my_cookie": {
        "key": "my_cookie",
        "value": "cookie_value",
    }
})
```

---

## 7. Nonce and Tokens

The dispatcher manages three types of security tokens automatically.

### CSP Nonce (`CSP_NONCE`)

A unique random nonce generated per request for Content Security Policy compliance. It allows inline scripts and styles that include the nonce to execute while blocking unauthorized inline code.

- **Generated by**: `get_nonce()` in the `common()` method.
- **Stored in**: `schema_data['CSP_NONCE']`
- **Template usage**:

```html
<script nonce="{:;CSP_NONCE:}">
    // This inline script is allowed by CSP
    console.log("Hello");
</script>

<style nonce="{:;CSP_NONCE:}">
    /* This inline style is allowed by CSP */
    body { margin: 0; }
</style>
```

### UTOKEN — User Token

A persistent token stored in a client cookie that identifies the browser/tab session. It is used as the basis for generating LTOKENs and form tokens.

- **Behavior on GET requests**: The UTOKEN is **rotated** (updated with a new value). This means each page load generates a fresh token.
- **Behavior on POST / AJAX requests**: The UTOKEN is **extracted** but not rotated. This prevents token mismatch during form submissions.
- **Stored in**: `schema_data['CONTEXT']['UTOKEN']`
- **Cookie name**: Configured via `Config.UTOKEN_KEY`

```python
# Internal logic (in parse_utoken):
if self.req.method == 'GET' and not self.ajax_request:
    # Rotate token
    utoken_token, utoken_cookie = utoken_update(...)
else:
    # Keep current token
    utoken_token, utoken_cookie = utoken_extract(...)
```

> **Important**: Because the UTOKEN rotates on every GET request, form links generated on one page must be submitted before the next GET navigation, or the LTOKEN derived from the old UTOKEN will become invalid.

### LTOKEN — Link Token

A token derived from the current UTOKEN, used to validate that a form was accessed through a legitimate link. It is automatically generated and made available for templates to embed in form action URLs.

- **Generated by**: `ltoken_create(utoken)` in the `common()` method.
- **Stored in**: `schema_data['LTOKEN']`
- **Template usage**:

```html
<!-- Link to a form page with the LTOKEN in the URL -->
<a href="/hello-component/form/{:;LTOKEN:}">Go to Form</a>
```

- **Validation**: Performed by `DispatcherForm.valid_form_tokens_get()` and `valid_form_tokens_post()` using `ltoken_check()`.

### Tab Change Detection

The dispatcher creates a fingerprint cookie to detect when users open new tabs or windows:

```python
def cookie_tab_changes(self) -> None:
    detect = "start"
    detect += self.schema_data['CONTEXT'].get("UTOKEN") or "none"
    detect += self.schema_data['CONTEXT'].get("SESSION") or "none"
    self.view.add_cookie({
        Config.TAB_CHANGES_KEY: {
            "key": Config.TAB_CHANGES_KEY,
            "value": sbase64url_md5(detect),
        }
    })
```

This allows client-side JavaScript to detect state changes across tabs.

---

## 8. AJAX Requests

The dispatcher detects AJAX requests via the custom `Requested-With-Ajax` header:

```python
self.ajax_request = self.schema_data['CONTEXT']['HEADERS'].get("Requested-With-Ajax") or False
```

When a request is identified as AJAX:

- **UTOKEN is not rotated** — It is only extracted, preserving the current token state.
- **Cookies are not set** — Session, theme, language, and tab-change cookies are skipped (they are already set by the parent page).
- **Template rendering may differ** — The template engine typically loads `template-ajax.ntpl` instead of the full `template.ntpl`, returning only the relevant content fragment instead of the entire HTML page.

This behavior ensures that AJAX requests are lightweight and do not interfere with the cookie/token state established by the parent page.

---

## 9. Deriving the Dispatcher Class

For components that require custom business logic, you should create a subclass of `Dispatcher`. This keeps route handlers clean and encapsulates logic in a reusable, testable class.

### File Location Convention

Custom dispatchers live in the component's `route/` directory:

```
cmp_7000_hellocomp/
└── route/
    ├── __init__.py
    ├── routes.py
    └── dispatcher_hellocomp.py    # Custom dispatcher
```

### Step 1: Create the Dispatcher Subclass

```python
# src/component/cmp_7000_hellocomp/route/dispatcher_hellocomp.py

from core.dispatcher import Dispatcher


class DispatcherHelloComp(Dispatcher):
    """Custom dispatcher for the Hello Component."""

    def __init__(self, request, comp_route, neutral_route=None):
        # Call the parent constructor — this handles all common initialization
        super().__init__(request, comp_route, neutral_route)

        # Set component-specific local data
        self.schema_local_data['foo'] = "bar"

    def test1(self):
        """Business logic for the test1 route."""
        # Perform any processing here
        # Return True/False to indicate success/failure
        return True
```

**Key points**:

- Always call `super().__init__(...)` first. This runs all common initialization (session, tokens, cookies, schema setup).
- The `__init__` signature can omit `ltoken` if your component does not handle forms with link tokens.
- Set default data in the constructor — this runs for every route that uses this dispatcher.
- Define business logic methods that routes can call before rendering.

### Step 2: Use the Dispatcher in Routes

```python
# src/component/cmp_7000_hellocomp/route/routes.py

from flask import Response, request
from core.dispatcher import Dispatcher
from . import bp
from .dispatcher_hellocomp import DispatcherHelloComp


# Route WITH custom business logic
@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    """Handle test1 requests with business logic."""
    dispatch = DispatcherHelloComp(request, route, bp.neutral_route)

    # Add route-specific data
    dispatch.schema_local_data["message"] = "Hello from test1!"

    # Execute business logic and store result
    dispatch.schema_data["dispatch_result"] = dispatch.test1()

    return dispatch.view.render()


# Route WITHOUT custom business logic (uses base Dispatcher)
@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    """Handle all other GET requests with generic dispatcher."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

### Step 3: Advanced Subclass Example

Here is a more complete example showing common patterns:

```python
# src/component/cmp_7000_hellocomp/route/dispatcher_hellocomp.py

from core.dispatcher import Dispatcher


class DispatcherHelloComp(Dispatcher):
    """Custom dispatcher for the Hello Component."""

    def __init__(self, request, comp_route, neutral_route=None):
        super().__init__(request, comp_route, neutral_route)

        # Default local data for all routes in this component
        self.schema_local_data['component_name'] = "Hello Component"
        self.schema_local_data['show_sidebar'] = "true"

    def test1(self) -> bool:
        """Business logic for test1: fetch and prepare data."""
        try:
            # Example: prepare some data
            items = self._fetch_items()
            self.schema_data["items"] = items
            self.schema_data["items_count"] = str(len(items))
            return True
        except Exception:
            self.schema_data["error_message"] = "Failed to load items"
            return False

    def dashboard(self) -> bool:
        """Business logic for the dashboard route."""
        # Check if user is logged in
        if not self.schema_data.get("HAS_SESSION"):
            self.schema_data["requires_login"] = "true"
            return False

        # Load user-specific data
        self.schema_local_data["welcome"] = "Welcome to your dashboard"
        return True

    def _fetch_items(self) -> list:
        """Private helper to fetch items (e.g., from database)."""
        return [
            {"id": "1", "name": "Item A"},
            {"id": "2", "name": "Item B"},
        ]
```

Using it in routes:

```python
@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.test1()
    return dispatch.view.render()


@bp.route("/dashboard", defaults={"route": "dashboard"}, methods=["GET"])
def dashboard(route) -> Response:
    dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.dashboard()
    return dispatch.view.render()
```

### Inheritance Chain

The dispatcher class hierarchy is designed for progressive specialization:

```
Dispatcher                          ← Base: session, tokens, rendering
  └── DispatcherForm                ← Adds: form validation, field rules, error handling
        └── DispatcherFormSign      ← Adds: auth-specific logic (ftoken, session check)
              ├── DispatcherFormSignIn    ← Sign-in flow
              ├── DispatcherFormSignUp    ← Registration flow
              ├── DispatcherFormSignOut   ← Logout flow
              └── DispatcherFormSignReminder  ← Password reminder
```

Your custom dispatchers can extend any level of this hierarchy depending on your needs:

- Extend `Dispatcher` for pages with business logic but no forms.
- Extend `DispatcherForm` for pages with form validation.
- Extend `DispatcherForm` subclasses for specialized form workflows.

---

## 10. DispatcherForm — Form Handling Subclass

`DispatcherForm` extends `Dispatcher` with form validation capabilities. It is the base class for any route that processes HTML forms.

**Location**: `src/core/dispatcher_form.py`

**Import**:
```python
from core.dispatcher_form import DispatcherForm
```

### Constructor

```python
DispatcherForm(req, comp_route, neutral_route=None, ltoken=None, form_name="form")
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `req` | `flask.Request` | **Yes** | The Flask request object. |
| `comp_route` | `str` | **Yes** | Relative route path within the component. |
| `neutral_route` | `str` or `None` | No | Path to the component's `neutral/route` directory. |
| `ltoken` | `str` or `None` | No | Link token from URL for CSRF validation. |
| `form_name` | `str` | No | The key used to look up form rules in `schema_data['core']['forms']`. Defaults to `"form"`. |

### Additional Attributes

| Attribute | Type | Description |
|---|---|---|
| `error` | `dict` | Error state dictionary with `form` (form-level errors) and `field` (per-field errors) sub-keys. Written to `schema_data[form_name]['error']`. |
| `form_submit` | `dict` | Submission result data. Written to `schema_data[form_name]['is_submit']`. |
| `field_rules` | `dict` | Validation rules for each field, loaded from `schema_data['core']['forms'][form_name]['rules']`. |
| `form_validation` | `dict` | Form-level validation constraints (min/max fields, allowed field patterns). |
| `form_check_fields` | `list` | List of field names to validate. |

### Validation Methods

| Method | Description |
|---|---|
| `valid_form_tokens_get()` | Validates the LTOKEN for GET requests. Returns `bool`. |
| `valid_form_tokens_post()` | Validates the LTOKEN for POST requests. Returns `bool`. |
| `valid_form_validation()` | Validates form-level constraints (field count, allowed field names). Returns `bool`. |
| `any_error_form_fields(error_prefix)` | Iterates through `form_check_fields` and validates each field. Returns `True` if any errors exist. |
| `get_error_field(field_name, error_prefix)` | Validates a single field against its rules. Returns `True` if the field has errors. |

### Supported Field Validation Rules

Rules are defined in `schema.json` under `data.core.forms.<form_name>.rules`:

| Rule | Description | Example |
|---|---|---|
| `set` | Field must be set (or not set). | `"set": true` |
| `required` | Field must have a non-empty value. | `"required": true` |
| `minlength` | Minimum string length. | `"minlength": 3` |
| `maxlength` | Maximum string length. | `"maxlength": 255` |
| `regex` | Must match a regular expression. | `"regex": "^[a-z]+$"` |
| `value` | Must equal a specific value. | `"value": "agree"` |
| `match` | Must equal the value of another field. | `"match": "password"` |
| `minage` | Minimum age in years (for dates). | `"minage": 13` |
| `maxage` | Maximum age in years (for dates). | `"maxage": 120` |
| `dns` | Domain must have valid DNS records. | `"dns": "MX"` |

### Error Structure in `schema_data`

After validation, errors are stored in `schema_data[form_name]`:

```json
{
    "form_name": {
        "error": {
            "form": {
                "ltoken": null,
                "validation": null,
                "already_session": null
            },
            "field": {
                "email": "ref:sign_in_form_error_required_true",
                "password": "ref:sign_in_form_error_minlength"
            }
        },
        "is_submit": {
            "result": {
                "success": "true",
                "error": null,
                "message": null
            }
        }
    }
}
```

### Example: Custom Form Dispatcher

```python
# src/component/cmp_7000_hellocomp/route/dispatcher_hellocomp_form.py

from core.dispatcher_form import DispatcherForm


class DispatcherHelloForm(DispatcherForm):
    """Form dispatcher for the Hello Component contact form."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None):
        super().__init__(req, comp_route, neutral_route, ltoken, "contact_form")

    def form_get(self) -> bool:
        """Validate GET request for the contact form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def form_post(self) -> bool:
        """Process contact form submission."""
        if not self.valid_form_tokens_post():
            return False

        if not self.valid_form_validation():
            return False

        if self.any_error_form_fields("ref:contact_form_error"):
            return False

        # All validation passed — process the form
        name = self.schema_data["CONTEXT"]["POST"].get("name")
        message = self.schema_data["CONTEXT"]["POST"].get("message")

        # Do something with the data...
        self.form_submit["result"] = {
            "success": "true",
            "message": f"Thank you, {name}!",
        }

        return True
```

Routes for the form:

```python
@bp.route("/contact/form/<ltoken>", defaults={"route": "contact/form"}, methods=["GET"])
def contact_form_get(route, ltoken) -> Response:
    dispatch = DispatcherHelloForm(request, route, bp.neutral_route, ltoken)
    dispatch.schema_data["dispatch_result"] = dispatch.form_get()
    return dispatch.view.render()


@bp.route("/contact/form/<ltoken>", defaults={"route": "contact/form"}, methods=["POST"])
def contact_form_post(route, ltoken) -> Response:
    dispatch = DispatcherHelloForm(request, route, bp.neutral_route, ltoken)
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.view.render()
```

Template with the form link:

```html
<!-- In a page template -->
<a href="/hello-component/contact/form/{:;LTOKEN:}">Contact Us</a>
```

---

## 11. Complete Example: HelloComp Component

This section shows the full lifecycle of a component using the `Dispatcher`, from file structure to rendering.

### File Structure

```
src/component/cmp_7000_hellocomp/
├── manifest.json
├── schema.json
├── __init__.py
├── lib/
│   └── hellocomp_0yt2sa/
│       └── __init__.py
├── route/
│   ├── __init__.py
│   ├── routes.py
│   └── dispatcher_hellocomp.py
├── neutral/
│   ├── component-init.ntpl
│   └── route/
│       ├── index-snippets.ntpl
│       └── root/
│           ├── content-snippets.ntpl
│           └── test1/
│               └── content-snippets.ntpl
└── static/
    ├── component.css
    └── component.js
```

### manifest.json

```json
{
    "uuid": "hellocomp_0yt2sa",
    "name": "Hello Component",
    "description": "Example component illustrating the basic structure",
    "version": "1.0.0",
    "route": "/hello-component"
}
```

### route/\_\_init\_\_.py — Blueprint Setup

```python
from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    bp = create_blueprint(component, component_schema)
    from . import routes
```

### route/dispatcher_hellocomp.py — Custom Dispatcher

```python
from core.dispatcher import Dispatcher


class DispatcherHelloComp(Dispatcher):
    """Hello component dispatcher."""

    def __init__(self, request, comp_route, neutral_route=None):
        super().__init__(request, comp_route, neutral_route)
        self.schema_local_data['foo'] = "bar"

    def test1(self):
        """Business logic for test1 requests."""
        return True
```

### route/routes.py — Route Definitions

```python
import os
from flask import Response, request, send_from_directory
from app.config import Config
from core.dispatcher import Dispatcher
from . import bp
from .dispatcher_hellocomp import DispatcherHelloComp

STATIC = f"{bp.component['path']}/static"


# Route with custom business logic
@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
    dispatch.schema_local_data["message"] = "Hello from test1"
    dispatch.schema_data["dispatch_result"] = dispatch.test1()
    return dispatch.view.render()


# Catch-all route (generic dispatcher or custom)
@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    # Serve static files if they exist
    if route:
        file_path = os.path.join(STATIC, route)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            response = send_from_directory(STATIC, route)
            response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
            return response

    # Use generic dispatcher for template routes
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

### Template: `neutral/route/root/test1/content-snippets.ntpl`

```html
{:snip; current:template:body-main-content >>
    <div class="container">
        <h3>{:;local::message:}</h3>

        {:bool; dispatch_result >>
            <div class="alert alert-success">
                Operation successful! foo = {:;local::foo:}
            </div>
        :}
        {:!bool; dispatch_result >>
            <div class="alert alert-danger">
                Operation failed.
            </div>
        :}

        <!-- Link with LTOKEN for form navigation -->
        <a href="/hello-component/contact/form/{:;LTOKEN:}">Contact Form</a>

        <!-- CSP-compliant inline script -->
        <script nonce="{:;CSP_NONCE:}">
            console.log("Hello from test1");
        </script>

        <!-- Session-aware content -->
        {:bool; HAS_SESSION >>
            <p>You are logged in.</p>
        :}{:else;
            <p>You are not logged in.</p>
        :}
    </div>
:}
{:^;:}
```

---

## 12. Quick Reference

### Dispatcher Initialization Flow

```
Dispatcher.__init__(req, comp_route, neutral_route, ltoken)
    │
    ├── Schema(req)                     # Parse request into schema
    ├── schema_data = schema['data']    # Global data reference
    ├── schema_local_data = schema['inherit']['data']  # Local data reference
    ├── Session(session_id)             # Session manager
    ├── User()                          # User manager
    ├── Template(schema)                # Rendering engine
    ├── _set_current_comp()             # Resolve component identity
    │     ├── CURRENT_COMP_ROUTE
    │     ├── CURRENT_COMP_ROUTE_SANITIZED
    │     ├── CURRENT_NEUTRAL_ROUTE
    │     ├── CURRENT_COMP_NAME
    │     └── CURRENT_COMP_UUID
    │
    └── common()                        # Shared initialization
          ├── session.get()             # Retrieve/create session
          ├── get_nonce()               # Generate CSP nonce
          ├── parse_utoken()            # Handle user token
          ├── ltoken_create()           # Generate link token
          └── [if not AJAX]:
                ├── cookie_tab_changes()
                └── view.add_cookie(session, theme, lang)
```

### Common Patterns Cheat Sheet

```python
# Basic page render
dispatch = Dispatcher(request, route, bp.neutral_route)
return dispatch.view.render()

# With business logic
dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
dispatch.schema_data["dispatch_result"] = dispatch.my_logic()
return dispatch.view.render()

# Set global data (immutable in templates)
dispatch.schema_data["key"] = "value"        # {:;key:}

# Set local data (mutable in templates)
dispatch.schema_local_data["key"] = "value"  # {:;local::key:}

# Check session
if dispatch.schema_data["HAS_SESSION"]:
    ...

# Add custom cookie
dispatch.view.add_cookie({"name": {"key": "name", "value": "val"}})

# Set response header
dispatch.view.response.headers["X-Custom"] = "value"

# Form with LTOKEN validation
dispatch = DispatcherForm(request, route, bp.neutral_route, ltoken, "my_form")
```

### Template Quick Reference

```
{:;varname:}                  ← schema_data value (global/immutable)
{:;local::varname:}           ← schema_local_data value (local/mutable)
{:;CSP_NONCE:}                ← CSP nonce for inline scripts/styles
{:;LTOKEN:}                   ← Link token for form URLs
{:;HAS_SESSION:}              ← "true" or null
{:;HAS_SESSION_STR:}          ← "true" or "false"
{:;CURRENT_COMP_ROUTE:}       ← Current route path
{:;CONTEXT->POST->fieldname:} ← POST data (auto-escaped)
```

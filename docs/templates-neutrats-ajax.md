## **GUIDE: AJAX Content Implementation in Neutral TS**

### **1. AJAX Architecture in Neutral TS**

Neutral TS detects AJAX requests via the `Requested-With-Ajax` header. The template component at `src/component/cmp_XXXX_template/neutral/layout/index.ntpl` detects if the request is an AJAX request:

```
{:bool; CONTEXT->HEADERS->Requested-With-Ajax >>
    {:include; {:flg; require :} >> #/template-ajax.ntpl :}
:}{:else;
    {:include; {:flg; require :} >> #/template.ntpl :}
:}
```

When an AJAX request is detected, only the content of the snippet `current:template:body-main-content` is rendered — without the surrounding `<html>`, `<head>`, or `<body>` elements. This behavior is automatic and transparent for the developer: the same `content-snippets.ntpl` file works for both full-page and AJAX responses.

---

### **2. The `{:fetch;}` BIF Reference**

The `{:fetch;}` BIF (Built-In Function) is Neutral TS's declarative way to create AJAX-enabled elements. It generates the appropriate HTML element with Neutral JS classes and attributes, handling all request mechanics automatically.

#### **2.1 Syntax**

```ntpl
{:fetch; |url|event|wrapperId|class|id|name| >> initial_content :}
```

| Position | Parameter | Required | Description |
|----------|-----------|----------|-------------|
| 1 | `url` | Yes | Endpoint URL to fetch |
| 2 | `event` | Yes | Trigger event type |
| 3 | `wrapperId` | No | ID of the element to replace with the response |
| 4 | `class` | No | CSS class(es) added to the generated element |
| 5 | `id` | No | ID attribute for the generated element |
| 6 | `name` | No | Name attribute for the generated element |

The content between `>>` and `:}` is the **initial content** — what the user sees before the fetch resolves. For forms this is the server-rendered form fields; for lazy-loaded sections it is typically a loading spinner.

#### **2.2 Event Types**

| Event | Generated Element | HTTP Method | Trigger | Primary Use Case |
|-------|-------------------|-------------|---------|------------------|
| `form` | `<form>` | POST | Form submit | Form submissions |
| `visible` | `<div>` | GET | Element enters viewport | Modal content, lazy loading |
| `click` | `<div>` | GET | User click | Load-on-demand buttons |
| `auto` | `<div>` | GET | Immediate on page load | Auto-loading content blocks |
| `none` | `<div>` | — | Manual JS trigger only | Custom JavaScript control |

#### **2.3 URL Construction**

AJAX URLs typically include the component route (from the manifest) and the `LTOKEN` security token:

```ntpl
{:fetch; |{:;cmp_uuid->manifest->route:}/subroute/ajax/{:;LTOKEN:}|form||{:;local::current->forms->class:}| >>
    ...
:}
```

- `{:;cmp_uuid->manifest->route:}` — Resolves to the component's base URL path (e.g., `/example-sign`).
- `{:;LTOKEN:}` — A per-page security token used to validate that the AJAX request originated from a legitimately rendered page.

#### **2.4 How `{:fetch; ... :}` Maps to HTML**

When `event` is `form`, the BIF generates a `<form>` element:

```html
<form id="my-id" name="my-name" class="neutral-fetch-form my-class"
      method="POST" action="/url" data-wrap="form-wrapper">
    <!-- initial_content rendered here -->
</form>
```

For all other events, it generates a `<div>` with the corresponding Neutral JS class (`neutral-fetch-auto`, `neutral-fetch-visible`, etc.) and a `data-url` attribute.

---

### **3. AJAX Response Templates**

#### **3.1 Directory Convention**

AJAX response templates live in an `ajax/` subdirectory beneath the route they serve:

```text
neutral/route/root/
├── subroute/
│   ├── content-snippets.ntpl    ← Full-page template (GET /subroute)
│   ├── data.json
│   └── ajax/
│       └── content-snippets.ntpl  ← AJAX fragment template (GET|POST /subroute/ajax/<ltoken>)
```

The URL-to-directory mapping follows the same pattern as all Neutral TS routes. If the component's manifest route is `/my-component`:

| URL Path | Template Directory |
|----------|--------------------|
| `/my-component/subroute` | `root/subroute/` |
| `/my-component/subroute/ajax/<ltoken>` | `root/subroute/ajax/` |

#### **3.2 AJAX Template Structure**

An AJAX `content-snippets.ntpl` defines the `current:template:body-main-content` snippet with only the fragment that should replace the existing content:

```ntpl
{:snip; current:template:body-main-content >>
    {:snip; cmp_uuid:my-content-snippet :}
:}

{:^;:}
```

**Critical rules:**

| Rule | Reason |
|------|--------|
| Do **NOT** include `{:data; ... :}` | Data is provided by the handler and schema, not by a data file |
| Do **NOT** add structural HTML (`<html>`, `<head>`, `<body>`) | The AJAX layout (`template-ajax.ntpl`) handles this |
| Do **NOT** add extra wrapper `<div>` elements | The content snippet already provides its own wrapper |
| **MUST** end with `{:^;:}` | The render trigger is required for every `content-snippets.ntpl` |

#### **3.3 Snippet Reuse Between Page and AJAX**

The key architectural pattern is that both the full-page template and the AJAX template render the **same snippet**. The snippet is defined once in `form-snippets.ntpl` (or any shared file included by `index-snippets.ntpl`) and referenced from both places:

**Full-page template** (`root/subroute/content-snippets.ntpl`):
```ntpl
{:data; #/data.json :}

{:snip; current:template:body-main-content >>
    <div class="{:;current->theme->class->container:}">
        {:snip; cmp_uuid:my-content-snippet :}
    </div>
:}

{:^;:}
```

**AJAX template** (`root/subroute/ajax/content-snippets.ntpl`):
```ntpl
{:snip; current:template:body-main-content >>
    {:snip; cmp_uuid:my-content-snippet :}
:}

{:^;:}
```

The full-page version loads its `data.json` and adds page-level wrappers (container, cards, headings). The AJAX version returns only the inner content fragment. Both call the same `cmp_uuid:my-content-snippet`, so form logic, coalesce patterns, and error handling are defined in one place.

#### **3.4 Auto-loaded Files**

Neutral TS auto-loads certain template files based on their location:

| File | Scope | Auto-loaded |
|------|-------|-------------|
| `component-init.ntpl` | App-wide (all components) | Yes — do NOT `{:include;}` it |
| `index-snippets.ntpl` | Component-wide (all routes in this component) | Yes — do NOT `{:include;}` it |
| `form-snippets.ntpl` | Component-wide | **No** — must be included from `index-snippets.ntpl` |

A typical `index-snippets.ntpl`:

```ntpl
{:* Include shared form/content snippets *:}
{:include; {:flg; require :} >> #/form-snippets.ntpl :}

{:* Move modals to end of body for proper Bootstrap z-indexing *:}
{:moveto; </body >>
    {:snip; cmp_uuid:modals :}
:}
```

---

### **4. Content Loading Patterns**

This section covers non-form AJAX patterns. For form-specific implementation, see Section 5.

#### **4.1 Auto-Loading Content**

Use the `auto` event to load content immediately when the page renders:

```ntpl
{:fetch; |{:;cmp_uuid->manifest->route:}/dashboard/ajax/{:;LTOKEN:}|auto|dashboard-content|my-class| >>
    <div class="text-center p-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">{:trans; Loading... :}</span>
        </div>
    </div>
:}
```

The spinner is shown immediately; as soon as the page loads, a GET request fires to the URL and the response replaces the spinner.

#### **4.2 Visible (Lazy Loading)**

Use the `visible` event to defer loading until the element scrolls into the viewport:

```ntpl
{:fetch; |{:;cmp_uuid->manifest->route:}/stats/ajax/{:;LTOKEN:}|visible|stats-section|| >>
    <div class="placeholder-glow p-3">
        <span class="placeholder col-12"></span>
    </div>
:}
```

This is the primary pattern for **modal content**: the `{:fetch;}` is placed inside `.modal-body`, and the `visible` event fires when the modal opens and the element becomes visible.

#### **4.3 Click-Triggered Loading**

Use the `click` event to load content on user interaction:

```ntpl
{:fetch; |{:;cmp_uuid->manifest->route:}/details/ajax/{:;LTOKEN:}|click|details-area|btn btn-outline-primary| >>
    {:trans; Load more details :}
:}
```

The generated `<div>` behaves like a clickable element. On click, it sends a GET request and replaces itself (or the element identified by `wrapperId`) with the response.

#### **4.4 Modal Integration Pattern**

Modals are the most common use of `visible` loading. The complete pattern involves three parts:

**1. Define the modal snippet** (in `form-snippets.ntpl` or a shared snippets file):

```ntpl
{:snip; cmp_uuid:modals >>
    <div class="modal fade" id="contentModal" tabindex="-1"
         aria-labelledby="contentModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="contentModalLabel">
                        {:trans; Details :}
                    </h5>
                    <button type="button" class="btn-close"
                            data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    {:fetch; |{:;cmp_uuid->manifest->route:}/details/ajax/{:;LTOKEN:}|visible||{:;local::current->forms->class:}| >>
                        <div class="text-center p-3">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    :}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-light btn-sm"
                            data-bs-dismiss="modal">{:trans; Close :}</button>
                </div>
            </div>
        </div>
    </div>
:}
```

**2. Move modals to end of `<body>`** (in `index-snippets.ntpl`):

```ntpl
{:moveto; </body >>
    {:snip; cmp_uuid:modals :}
:}
```

**3. Add the trigger button** (in any page template):

```ntpl
<button type="button" class="btn btn-primary"
        data-bs-toggle="modal" data-bs-target="#contentModal">
    {:trans; View Details :}
</button>
```

**Flow:** User clicks trigger → modal opens → `visible` event fires → GET request loads content → spinner is replaced with response.

#### **4.5 Backend Route for Non-Form AJAX**

For simple content loading (no form processing), the backend route is straightforward:

```python
from flask import Response, g
from core.request_handler_form import FormRequestHandler
from . import bp

@bp.route("/details/ajax/<ltoken>", defaults={"route": "details/ajax"}, methods=["GET"])
def details_ajax(route, ltoken) -> Response:
    """AJAX route — load details content"""
    handler = FormRequestHandler(g.pr, route, bp.neutral_route, ltoken, "_unused_form")
    handler.schema_data["ajax_result"] = True
    return handler.render_route()
```

The `route` parameter value (`"details/ajax"`) maps directly to the template directory `root/details/ajax/` where `content-snippets.ntpl` lives.

---

### **5. AJAX Form Implementation**

Forms in Neutral TS follow a structured pattern that combines the `{:fetch;}` BIF with server-side validation, a coalesce-based lifecycle, and a handler class.

#### **5.1 Form Schema (`route/schema.json`)**

Every form needs validation rules defined in the route's `schema.json` under `data.current_forms`:

```json
{
    "data": {
        "current_forms": {
            "contact_form": {
                "check_fields": ["name", "email", "message"],
                "validation": {
                    "minfields": 3,
                    "maxfields": 4,
                    "allow_fields": ["name", "email", "message", "send"]
                },
                "rules": {
                    "name": {
                        "required": true,
                        "minlength": 2,
                        "maxlength": 100
                    },
                    "email": {
                        "required": true,
                        "pattern": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+",
                        "regex": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"
                    },
                    "message": {
                        "required": true,
                        "minlength": 10,
                        "maxlength": 1000
                    }
                }
            }
        }
    }
}
```

| Field | Description |
|-------|-------------|
| `check_fields` | Array of field names to validate on POST |
| `validation.minfields` / `maxfields` | Expected range of POST field count |
| `validation.allow_fields` | Whitelist of allowed field names (use `ftoken.*` for anti-bot token fields) |
| `rules.<field>.required` | Field must have a value |
| `rules.<field>.minlength` / `maxlength` | String length constraints |
| `rules.<field>.pattern` | HTML5 pattern attribute (client-side) |
| `rules.<field>.regex` | Server-side regex validation |
| `rules.<field>.value` | Exact value match required |
| `rules.<field>.set` | If `false`, field must NOT be present (honeypot anti-bot) |

> **Note:** `pattern` and `regex` can both be defined for the same field. `pattern` drives the browser's built-in validation; `regex` is checked server-side in the handler.

#### **5.2 Form Template Snippets**

Form snippets are defined in `form-snippets.ntpl` and follow a layered structure. All user-facing text must be wrapped in `{:trans; ... :}`.

**Required include at the top:**

```ntpl
{:include; {:flg; require :} >> {:;forms_0yt2sa->path:}/neutral/snippets.ntpl :}
```

**Error snippet generation** — for each form, iterate over validation errors and generate per-field error snippets:

```ntpl
{:+each; contact_form->error->field field msg >>
    {:+code;
        {:param; field >> {:;field:} :}
        {:param; msg >> {:;msg:} :}
        {:param; help-item >> contact_form-{:;field:} :}
        {:snip; forms:set-form-field-error :}
    :}
:}
```

This generates two snippets per errored field:
- `{:snip; is-invalid:fieldname :}` → outputs the CSS class `is-invalid`
- `{:snip; error-msg:fieldname :}` → outputs the error message HTML

If a field has no error, both snippets render as empty strings.

**The form snippet** — wraps form fields in `{:fetch;}` with `event=form`:

```ntpl
{:snip; cmp_uuid:contact_form-form >>
    {:fetch; |{:;cmp_uuid->manifest->route:}/contact/ajax/{:;LTOKEN:}|form||{:;local::current->forms->class:}| >>

        <div class="form-floating">
            <input type="text" id="contact_form-name" name="name"
                value="{:;CONTEXT->POST->name:}"
                class="form-control {:snip; is-invalid:name :}"
                placeholder="{:trans; Your name :}"
                minlength="{:;current_forms->contact_form->rules->name->minlength:}"
                maxlength="{:;current_forms->contact_form->rules->name->maxlength:}"
                {:bool; current_forms->contact_form->rules->name->required >> required :}
            >
            <label for="contact_form-name">{:trans; Your name :}</label>
        </div>
        {:snip; error-msg:name :}
        <div class="{:;local::current->forms->field-spacing:}"></div>

        {:* ... more fields ... *:}

        <button type="submit" name="send" value="1"
                class="w-100 btn btn-primary">{:trans; Send :}</button>

    :}
:}
```

Key patterns used in form fields:

| Pattern | Purpose |
|---------|---------|
| `value="{:;CONTEXT->POST->fieldname:}"` | Preserves user input after failed submission |
| `class="form-control {:snip; is-invalid:fieldname :}"` | Adds `is-invalid` class on validation error |
| `{:snip; error-msg:fieldname :}` | Shows per-field error message |
| `{:bool; ...->required >> required :}` | Conditionally adds `required` attribute from schema |
| `class="fetch-form-button-reset"` | Makes a button reload/reset the form via AJAX |
| `{:;local::current->forms->field-spacing:}` | Theme-provided spacing class |

#### **5.3 Coalesce Pattern (Form Lifecycle)**

The container snippet uses `{:coalesce;}` to control which state the user sees. `{:coalesce;}` evaluates each option in order and renders the **first** one that produces non-empty output:

```ntpl
{:snip; cmp_uuid:contact_form-form-container >>
    <div id="contact_form-container">
        {:coalesce;
            {:* Option 1: Success *:}
            {:same; /{:;form_result->status:}/success/ >>
                <div class="alert alert-success">
                    <h5>{:trans; Success! :}</h5>
                    <p>{:trans; Your message has been sent. :}</p>
                </div>
            :}

            {:* Option 2: General failure *:}
            {:same; /{:;form_result->status:}/fail/ >>
                <div class="alert alert-danger">
                    <h5>{:trans; ERROR :}</h5>
                    <p>{:;form_result->message:}</p>
                </div>
            :}

            {:* Option 3: Default — show the form *:}
            {:snip; cmp_uuid:contact_form-form :}
        :}
    </div>
:}
```

**Lifecycle states:**

| State | Condition | What renders |
|-------|-----------|-------------|
| Initial load | `form_result` not set | Option 3: empty form (no errors) |
| Field validation errors | `post()` returns `False`, field errors set | Option 3: form with inline errors |
| General failure | `form_result->status` = `"fail"` | Option 2: error alert |
| Success | `form_result->status` = `"success"` | Option 1: success message |

Alternative success actions include `{:snip; util:reload-page-self :}` to trigger a page reload (useful for login flows).

#### **5.4 Backend Routes**

Each form requires three Flask routes: the full-page GET, the AJAX GET, and the AJAX POST:

```python
from flask import Response, g
from .handler_module import FormRequestHandlerContact
from . import bp

# Full page (GET)
@bp.route("/contact", defaults={"route": "contact"}, methods=["GET"])
def contact_page(route) -> Response:
    handler = FormRequestHandlerContact(
        g.pr, route, bp.neutral_route,
        None,            # ltoken: None for page routes
        "contact_form"   # form_name: key in schema.json current_forms
    )
    handler.schema_data["dispatch_result"] = True
    return handler.render_route()

# AJAX GET (initial form load for modals / fetch)
@bp.route("/contact/ajax/<ltoken>", defaults={"route": "contact/ajax"}, methods=["GET"])
def contact_ajax_get(route, ltoken) -> Response:
    handler = FormRequestHandlerContact(
        g.pr, route, bp.neutral_route, ltoken, "contact_form"
    )
    handler.schema_data["dispatch_result"] = handler.get()
    return handler.render_route()

# AJAX POST (form submission)
@bp.route("/contact/ajax/<ltoken>", defaults={"route": "contact/ajax"}, methods=["POST"])
def contact_ajax_post(route, ltoken) -> Response:
    handler = FormRequestHandlerContact(
        g.pr, route, bp.neutral_route, ltoken, "contact_form"
    )
    handler.schema_data["dispatch_result"] = handler.post()
    return handler.render_route()
```

The `route` parameter maps to the template directory under `root/`. The `ltoken` parameter from the URL is passed to the handler for security validation.

#### **5.5 RequestHandler**

The handler subclasses `FormRequestHandler` and implements `get()` and `post()`:

```python
from core.request_handler_form import FormRequestHandler

class FormRequestHandlerContact(FormRequestHandler):
    """Handles contact_form processing."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None,
                 form_name="contact_form"):
        super().__init__(req, comp_route, neutral_route, ltoken, form_name)
        self.schema_data["dispatch_result"] = True

    def get(self) -> bool:
        if not self.valid_form_tokens_get():
            return False
        return True

    def post(self) -> bool:
        # 1. Validate tokens (CSRF / LTOKEN)
        if not self.valid_form_tokens_post():
            return False

        # 2. Validate fields against schema rules
        if not self.valid_form_validation():
            return False

        # 3. Check for field-level validation errors
        if self.any_error_form_fields("ref:contact_form_error"):
            return False

        # 4. Custom business logic
        email = self.schema_data["CONTEXT"]["POST"].get("email")

        if email and "@blocked.com" in email:
            self.error["form"]["email"] = "true"
            self.error["field"]["email"] = "ref:contact_form_error_invalid_domain"
            return False

        # 5. Set success
        self.schema_data["form_result"] = {
            "status": "success",
            "message": "Thank you!"
        }
        return True
```

**Inherited methods:**

| Method | Purpose |
|--------|---------|
| `valid_form_tokens_get()` | Validates LTOKEN for GET requests |
| `valid_form_tokens_post()` | Validates CSRF/LTOKEN for POST requests |
| `valid_form_validation()` | Validates POST fields against `schema.json` rules |
| `any_error_form_fields(prefix)` | Checks for field errors; generates translation keys by appending error type (e.g., `_required`, `_minlength`, `_regex`) |

**Error handling:**

| Property | Usage |
|----------|-------|
| `self.error["form"]["fieldname"] = "true"` | Marks a field as having an error |
| `self.error["field"]["fieldname"] = "ref:..."` | Sets the translation reference for the field's error message |
| `self.schema_data["form_result"]` | Dict with `status` (`"success"` / `"fail"`) and optional `message` |
| `self.schema_data["CONTEXT"]["POST"]` | Dict of submitted POST data |

#### **5.6 Complete Workflow Summary**

**Initial page load (GET):**
1. User visits `/component-route/contact`
2. RequestHandler created with `ltoken=None`, `dispatch_result=True`
3. Template chain: `data.json` → `content-snippets.ntpl` → content snippet → form-container → form
4. `{:fetch;}` generates a `<form>` with fields rendered server-side; no errors, empty fields

**Form submission (POST via AJAX):**
1. User submits → `{:fetch;}` intercepts and POSTs to `/contact/ajax/<ltoken>`
2. RequestHandler validates: tokens → schema → custom logic
3. On validation failure: `post()` returns `False`; errors populate `self.error`; template re-renders the form with inline error messages
4. On general failure: set `form_result = {"status": "fail", ...}`; coalesce shows error alert
5. On success: set `form_result = {"status": "success"}`; coalesce shows success message
6. AJAX response replaces the form area in the browser

**Modal flow:**
1. User opens modal → `visible` event fires → GET to `/contact/ajax/<ltoken>`
2. Spinner replaced with rendered form
3. Subsequent form submission follows the same POST flow above, updating within the modal

---

### **6. JavaScript Events and API**

Neutral TS dispatches custom events you can listen to:

```javascript
// Event: Fetch completed successfully
window.addEventListener('neutralFetchCompleted', function(evt) {
    console.log('Loaded URL:', evt.detail.url);
    console.log('Container element:', evt.detail.element);
});

// Event: Fetch error
window.addEventListener('neutralFetchError', function(evt) {
    console.error('Error loading:', evt.detail.url);
    // Show error message to user
});
```

---

### **7. JS Variables Configuration**

Before loading `neutral.min.js`, you can configure behavior:

```
<script nonce="{:;CSP_NONCE:}">
    // Spinner shown during load
    var neutral_submit_loading = '<span class="spinner-border spinner-border-sm"></span>';

    // Request timeout (ms)
    var neutral_submit_timeout = 30000;

    // Error message
    var neutral_submit_error = '{:trans; Connection error. Please try again. :}';

    // Time error message remains visible (ms)
    var neutral_submit_error_delay = 3500;

    // Delay to prevent double-click (ms)
    var neutral_submit_delay = 250;
</script>
```

---

### **8. Neutral JS Classes: Manual Control vs {:fetch;}**

Neutral TS provides two approaches for AJAX functionality: the `{:fetch;` BIF for automatic handling, or manual HTML with Neutral JS classes for full control.

#### **8.1 Automatic Approach: `{:fetch;` BIF**

The `{:fetch;` BIF automatically wraps content and adds necessary classes:

```ntpl
{:* Neutral TS automatically generates the appropriate wrapper *:}
{:fetch; |/url|form|form-wrapper|my-class|my-form-id|my-name| >>
    <input type="text" name="paramValue">
    <button type="submit">Send</button>
:}
```

**Generated HTML (form event):**
```html
<form id="my-id" name="my-name" class="neutral-fetch-form my-class"
      method="POST" action="/url" data-wrap="form-wrapper">
    <input type="text" name="paramValue">
    <button type="submit">Send</button>
</form>
```

#### **8.2 Manual Approach: Neutral JS Classes**

For cases requiring full control over the HTML structure, use Neutral JS classes directly:

| Class | Behavior | Use Case |
|-------|----------|----------|
| `neutral-fetch-form` | Submits form via AJAX on submit event | Forms needing custom structure |
| `neutral-fetch-auto` | Fetches content immediately on page load | Auto-loading content |
| `neutral-fetch-click` | Fetches content on click event | Buttons, links, clickable elements |
| `neutral-fetch-visible` | Fetches when element enters viewport | Lazy loading, infinite scroll |
| `neutral-fetch-none` | No automatic event, manual JS trigger | Custom JavaScript control |

**Required attributes for manual classes:**
- `data-url` - Endpoint URL to fetch
- `data-wrap` (optional) - ID of container to receive response

#### **8.3 Equivalent Examples**

**Form with `{:fetch;`:**
```ntpl
{:fetch; |/submit|form|wrapper|my-form| >>
    <input type="text" name="username">
    <button type="submit">Submit</button>
:}
```

**Same form with manual class (full control):**
```ntpl
<form class="neutral-fetch-form my-form"
      method="POST"
      action="/submit"
      data-wrap="wrapper">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

#### **8.4 When to Use Manual Classes**

Use manual Neutral JS classes when:

1. **Custom form structure needed** - You need specific form attributes (enctype, target, novalidate)
2. **Third-party library integration** - Libraries that modify form behavior
3. **Complex event handling** - Multiple triggers or custom JavaScript logic
4. **Progressive enhancement** - Form should work without JavaScript
5. **Accessibility requirements** - Specific ARIA attributes or focus management


#### **8.5 JavaScript API for Manual Control**

Access Neutral JS functions directly for custom behavior:

```javascript
// Re-initialize events after dynamic content loads
neutral_fev();

// Manual fetch trigger
neutral_fetch(element, url, wrapperId);

// Manual form submission
neutral_fetch_form(formElement, url, wrapperId);
```

---

### **9. AJAX Implementation Checklist**

| Step | Verification |
|------|--------------|
| 1 | Create reusable snippet in shared file |
| 2 | Container page uses `{:fetch; |url|auto|...` for initial load |
| 3 | `/ajax` route exists and responds to GET (or POST for forms) |
| 4 | AJAX template only defines `current:template:body-main-content` |
| 5 | No structural HTML (html, body, head) in AJAX response |
| 6 | Include `{:^;:}` at end of both templates |
| 7 | Configure `neutral_submit_*` variables if needed |
| 8 | Add event listeners for `neutralFetchCompleted` if post-load JS needed |
| 9 | Protect AJAX routes with `@require_header_set` if necessary |
| 10 | Verify `disable_js` is `false` in schema or include `neutral.min.js` manually |

---

### **10. Common Patterns and Troubleshooting**

#### **10.1 Common Patterns**

**Reset / reload button inside a form:**

Add a button with the class `fetch-form-button-reset`. Neutral JS automatically handles it by re-fetching the form via GET, restoring it to its initial state:

```ntpl
<button type="button" title="{:trans; Reload form :}"
        class="fetch-form-button-reset btn btn-light">
    <span class="{:;local::x-icon-reload:}"></span>
</button>
```

**Multiple modals sharing a single snippet:**

Define all modals inside one snippet and move them together:

```ntpl
{:snip; cmp_uuid:modals >>
    <div class="modal fade" id="formOneModal" ...>
        <div class="modal-body">
            {:fetch; |{:;cmp_uuid->manifest->route:}/form-one/ajax/{:;LTOKEN:}|visible||{:;local::current->forms->class:}| >>
                <div class="spinner-border" role="status"></div>
            :}
        </div>
    </div>
    <div class="modal fade" id="formTwoModal" ...>
        ...
    </div>
:}
```

**Setting cookies from the handler:**

```python
self.view.add_cookie({
    "session-name": {
        "key": "session-name",
        "value": "session-value",
        "path": "/"
    }
})
```

**Page reload on success** (e.g., after login):

Replace the success message in the coalesce with:

```ntpl
{:same; /{:;form_result->status:}/success/ >>
    {:snip; util:reload-page-self :}
:}
```

#### **10.2 FToken (Anti-Bot Protection)**

FToken is an optional client-side anti-bot mechanism. When enabled:

1. Add honeypot and checkbox fields to the schema with `"set": false` and `"value"` rules.
2. Add `ftoken-field-key`, `ftoken-field-value`, `data-ftokenid`, and related attributes to tracked input fields.
3. Give the `{:fetch;}` tag explicit `wrapperId` and `id` parameters.
4. Validate with `ftoken_check()` in the handler after standard validation.

See the `cmp_6000_examplesign` component for a complete working example.

#### **10.3 Troubleshooting**

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Full page returned instead of fragment | `Requested-With-Ajax` header missing | If using manual `fetch()`, add `"Requested-With-Ajax": "true"` header |
| AJAX response is empty | Missing `{:^;:}` at end of template | Add `{:^;:}` as the last line of `content-snippets.ntpl` |
| Form shows no validation errors | Error snippet generation block missing or misnamed | Verify `{:+each; form_name->error->field ...}` block exists and uses the correct form name |
| Form fields lose values after error | Missing `value="{:;CONTEXT->POST->fieldname:}"` | Add the value attribute referencing POST context |
| Snippet not found / empty | Snippet defined in a file that isn't included | Ensure `form-snippets.ntpl` is included from `index-snippets.ntpl` |
| Modal appears behind backdrop | Modal HTML not at end of `<body>` | Use `{:moveto; </body >> ... :}` in `index-snippets.ntpl` |
| `{:data; ... :}` has no effect in AJAX template | Data files are only loaded for page-level templates | Remove `{:data;}` from AJAX templates; data comes from the handler |
| Route returns 404 | `route` default doesn't match directory structure | Verify `defaults={"route": "..."}` matches `root/<path>/` |

---

### **11. Manual AJAX Requests with `Requested-With-Ajax` Header**

When Neutral TS initiates AJAX requests via `{:fetch;` or its JavaScript classes, it **automatically sets** the `Requested-With-Ajax` header to `fetch`. This header is essential for the backend to detect AJAX mode and respond appropriately (rendering `template-ajax.ntpl` instead of the full layout).

However, if you need to make manual AJAX requests using vanilla JavaScript (outside of Neutral's automatic handling), **you must explicitly set this header**:

```javascript
fetch("/component/route", {
  method: "POST",
  headers: {
    "Requested-With-Ajax": "true",
    "Content-Type": "application/x-www-form-urlencoded"
  },
  body: new URLSearchParams({ key: "value" })
});
```

**Important notes:**
- The header name is case-insensitive on the server side
- The exact value is less important than the header's presence (Neutral checks for existence, not specific value)
- This applies to any manual AJAX: `fetch()`, `XMLHttpRequest`, or third-party libraries like Axios
- Without this header, the server will render the full page layout instead of the AJAX fragment

This convention is specific to routes handled through the Neutral + RequestHandler flow and is not required for independent API endpoints outside that rendering pipeline.

---

### **12. Template Syntax Quick Reference**

| Syntax | Purpose |
|--------|---------|
| `{:;variable->path:}` | Output variable value |
| `{:;local::variable:}` | Output local/theme variable |
| `{:;LTOKEN:}` | Current page security token |
| `{:;CONTEXT->POST->field:}` | Submitted POST field value |
| `{:;cmp_uuid->manifest->route:}` | Component base route from manifest |
| `{:;current_forms->form->rules->field->prop:}` | Schema validation rule value |
| `{:trans; text :}` | Translation wrapper |
| `{:snip; namespace:name >> content :}` | Define a snippet |
| `{:snip; namespace:name :}` | Render a snippet |
| `{:fetch; \|url\|event\|wrap\|class\|id\| >> content :}` | AJAX fetch wrapper |
| `{:include; {:flg; require :} >> path :}` | Include a file (required) |
| `{:data; #/data.json :}` | Load data file (relative path with `#/`) |
| `{:coalesce; opt1 opt2 opt3 :}` | Render first non-empty option |
| `{:bool; variable >> content :}` | Render content if variable is truthy |
| `{:!bool; variable >> content :}` | Render content if variable is falsy |
| `{:bool; var >> if_true :}{:else; if_false :}` | Conditional with else |
| `{:same; /val1/val2/ >> content :}` | Render content if values are equal |
| `{:eval; expression >> content :}` | Render content if expression is truthy |
| `{:moveto; </body >> content :}` | Move content to end of body |
| `{:+each; collection key val >> template :}` | Iterate over collection |
| `{:+code; ... :}` | Code block with parameters |
| `{:param; name >> value :}` | Set parameter (inside `{:+code;:}`) |
| `{:* comment *:}` | Template comment (not rendered) |
| `{:^;:}` | Render trigger (required at end of `content-snippets.ntpl`) |

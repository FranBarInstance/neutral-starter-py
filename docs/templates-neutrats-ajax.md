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

It then only renders the content of the snippet `current:template:body-main-content`. This behavior is automatic and transparent for the developer.

---

### **2. Recommended File Structure**

```
src/component/cmp_XXXX_name/
└── neutral/
    └── route/
        └── root/
            ├── content-snippets.ntpl          # Container page (normal)
            ├── data.json                      # Shared data
            ├── ajax/                          # AJAX route
            │   └── content-snippets.ntpl      # AJAX response (content only)
            └── form/                          # Example subroute
                └── content-snippets.ntpl      # Form loaded via AJAX
```

---

### **3. Implementation Pattern Step by Step**

#### **Step 1: Create the Reusable Snippet**

Create a shared snippets file (e.g., `snippets.ntpl` or in `index-snippets.ntpl`):

```ntpl
{:*
    ======================================
    SNIPPET: my-form
    Reusable content for normal loading
    and AJAX loading
    ======================================
*:}

{:snip; my-form >>
    <div class="card border-light mb-3">
        <div class="card-body">
            <h4>{:trans; Example Form :}</h4>

            <form id="my-form" class="neutral-fetch-form"
                  action="{:;form_route:}/form/{:;LTOKEN:}"
                  method="POST">

                <div class="input-group mb-3">
                    <span class="input-group-text">@</span>
                    <input type="email"
                           name="email"
                           class="form-control"
                           placeholder="{:trans; Email :}"
                           required>
                </div>

                <div class="input-group mb-3">
                    <span class="input-group-text">🔒</span>
                    <input type="password"
                           name="password"
                           class="form-control"
                           placeholder="{:trans; Password :}"
                           required>
                </div>

                <button type="submit" class="btn btn-primary w-100">
                    {:trans; Submit :}
                </button>
            </form>
        </div>
    </div>
:}

{:* Success message snippet *:}
{:snip; form-success >>
    <div class="alert alert-success">
        <h5>{:trans; Success! :}</h5>
        <p>{:;message:}</p>
    </div>
:}

{:* Error message snippet *:}
{:snip; form-error >>
    <div class="alert alert-danger">
        <h5>{:trans; Error :}</h5>
        <p>{:;error_msg:}</p>
    </div>
:}
```

#### **Step 2: Container Page (Normal Route)**

`neutral/route/root/content-snippets.ntpl`:

```ntpl
{:*
    ========================================
    ROUTE: /my-component/
    Container page with full layout
    ========================================
*:}

{:* 1. Load data *:}
{:data; {:flg; require :} >> #/data.json :}

{:* 2. Include shared snippets *:}
{:!include; {:flg; require :} >> #/snippets.ntpl :}

{:* 3. Load form via AJAX on page load *:}
{:snip; current:template:body-main-content >>
    <div class="{:;local::current->theme->class->container:} mb-5">
        <h1 class="border-bottom p-2">{:trans; {:;local::current->route->h1:} :}</h1>

        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">

                {:* Container where form will be loaded *:}
                <div id="form-wrapper">
                    {:fetch; |{:;my_component->manifest->route:}/ajax|auto|form-wrapper| >>
                        <div class="text-center p-5">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">{:trans; Loading... :}</span>
                            </div>
                        </div>
                    :}
                </div>

            </div>
        </div>
    </div>
:}

{:* 4. Force output *:}
{:^;:}
```

#### **Step 3: AJAX Response (Content Only)**

`neutral/route/root/ajax/content-snippets.ntpl`:

```ntpl
{:*
    ========================================
    ROUTE: /my-component/ajax
    AJAX Response - ONLY content, no layout
    ========================================
*:}

{:* 1. Load data (same as container page) *:}
{:data; {:flg; require :} >> #/data.json :}

{:* 2. Include shared snippets *:}
{:!include; {:flg; require :} >> #/../snippets.ntpl :}

{:* 3. Render ONLY the form content *:}
{:* NOTE: Do not include container, layout, or complete HTML structure *:}

{:snip; current:template:body-main-content >>
    {:snip; my-form :}
:}

{:* 4. Force output *:}
{:^;:}
```

---

### **4. Implementation Variants**

#### **Variant A: Modal Content (Sign Component Example)**

```ntpl
{:*
    ========================================
    MODAL WITH AJAX CONTENT
    ========================================
*:}

{:* Button that opens modal *:}
<button type="button"
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#loginModal">
    {:trans; Sign in :}
</button>

{:* Modal definition *:}
{:snip; current:template:modals >>
    <div class="modal fade" id="loginModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{:trans; Sign in :}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    {:* AJAX load form inside modal *:}
                    {:fetch; |{:;sign_0yt2sa->manifest->route:}/in/form/{:;LTOKEN:}|visible| >>
                        <div class="text-center p-3">
                            <span class="spinner-border"></span>
                        </div>
                    :}
                </div>
            </div>
        </div>
    </div>
:}
```

#### **Variant B: Click-Triggered Load**

```ntpl
{:*
    ========================================
    CLICK-TRIGGERED LOAD
    ========================================
*:}

{:snip; current:template:body-main-content >>
    <div class="container">

        {:* Button that triggers load *:}
        {:fetch; |{:;my_component->manifest->route:}/ajax/data|click|data-container| >>
            <button type="button" class="btn btn-info">
                {:trans; Load data :}
            </button>
        :}

        {:* Target container (note it's EMPTY initially) *:}
        <div id="data-container" class="mt-3"></div>

    </div>
:}
```

#### **Variant C: Visible Load (Lazy Loading)**

```ntpl
{:*
    ========================================
    LOAD WHEN VISIBLE (Lazy Loading)
    ========================================
*:}

{:snip; current:template:body-main-content >>
    <div class="container">
        <p>Scroll down to load content...</p>

        {:* Will load when element enters viewport *:}
        <div class="lazy-content mt-5">
            {:fetch; |{:;my_component->manifest->route:}/ajax/lazy|visible|lazy-wrapper| >>
                <div class="placeholder" style="height: 200px;">
                    {:trans; Scroll to view content... :}
                </div>
            :}
            <div id="lazy-wrapper"></div>
        </div>
    </div>
:}
```

#### **Variant D: AJAX Form with Dynamic Response**

```ntpl
{:*
    ========================================
    FORM THAT UPDATES VIA AJAX
    ========================================
*:}

{:* In snippets.ntpl *:}
{:snip; dynamic-form >>

    {:* Show result if exists *:}
    {:filled; form_result >>
        {:same; /{:;form_result->status:}/success/ >>
            {:snip; form-success :}
        :}{:else;
            {:snip; form-error :}
        :}

        <button type="button"
                class="btn btn-secondary mt-3 neutral-fetch-click"
                data-url="{:;my_component->manifest->route:}/ajax/form">
            {:trans; Back to form :}
        </button>

    :}{:else;
        {:* Show form *:}
        {:fetch; |{:;my_component->manifest->route:}/ajax/form|form|form-wrapper|my-form-class| >>
            <form id="my-dynamic-form" class="neutral-fetch-form">
                <input type="text" name="name" placeholder="Name" required>
                <button type="submit">{:trans; Submit :}</button>
            </form>
        :}
    :}

    <div id="form-wrapper"></div>
:}
```

---

### **5. Backend Configuration (Python/Flask)**

#### **5.1 Routes in `routes.py`**

```python
# src/component/cmp_XXXX_name/route/routes.py

from flask import Response, request
from core.dispatcher import Dispatcher
from . import bp

# Container route (full page)
@bp.route("/", defaults={"route": ""}, methods=["GET"])
def index(route) -> Response:
    """Container page with full layout."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.view.render()

# AJAX route (content only)
@bp.route("/ajax", defaults={"route": "ajax"}, methods=["GET"])
def ajax_content(route) -> Response:
    """AJAX response - only content without layout."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    # Template engine detects AJAX via header and renders template-ajax.ntpl
    return dispatch.view.render()

# AJAX route for forms (POST)
@bp.route("/ajax/form", defaults={"route": "ajax/form"}, methods=["GET", "POST"])
def ajax_form(route) -> Response:
    """Form via AJAX."""
    from core.dispatcher_form import DispatcherForm

    if request.method == "GET":
        # Show empty form
        dispatch = Dispatcher(request, route, bp.neutral_route)
        dispatch.schema_data["dispatch_result"] = True
        return dispatch.view.render()

    # POST: Process form
    # ... validation logic ...
    dispatch.schema_data["form_result"] = {"status": "success", "message": "OK"}
    return dispatch.view.render()
```

#### **5.2 AJAX Route Protection**

```python
from app.extensions import require_header_set

@bp.route("/ajax/protected", methods=["GET"])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def protected_ajax() -> Response:
    """Only accessible via AJAX."""
    dispatch = Dispatcher(request, "ajax/protected", bp.neutral_route)
    return dispatch.view.render()
```

---

### **6. JavaScript Events and API**

Neutral TS dispatches custom events you can listen to:

```javascript
// Event: Fetch completed successfully
window.addEventListener('neutralFetchCompleted', function(evt) {
    console.log('Loaded URL:', evt.detail.url);
    console.log('Container element:', evt.detail.element);

    // Execute scripts from loaded content
    if (!evt.detail.url.includes('://')) {
        const scripts = evt.detail.element.querySelectorAll('script');
        scripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.text = script.textContent;
            document.body.appendChild(newScript);
        });
    }
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

```ntpl
{:moveto; <head >>
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
:}
```

---

### **8. Neutral JS Classes: Manual Control vs {:fetch;}**

Neutral TS provides two approaches for AJAX functionality: the `{:fetch;` BIF for automatic handling, or manual HTML with Neutral JS classes for full control.

#### **8.1 Automatic Approach: `{:fetch;` BIF**

The `{:fetch;` BIF automatically wraps content and adds necessary classes:

```ntpl
{:* Neutral TS automatically generates the appropriate wrapper *:}
{:fetch; |/url|form|form-wrapper|my-class|my-id|my-name| >>
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
{:fetch; |/api/submit|form|wrapper|my-form| >>
    <input type="text" name="username">
    <button type="submit">Submit</button>
:}
```

**Same form with manual class (full control):**
```ntpl
<form class="neutral-fetch-form my-form"
      method="POST"
      action="/api/submit"
      data-wrap="wrapper">
    <input type="text" name="username">
    <button type="submit">Submit</button>
</form>
```

**Auto-load with `{:fetch;`:**
```ntpl
{:fetch; |/api/data|auto|content-box| >>
    <div>Loading...</div>
:}
```

**Same with manual class:**
```ntpl
<div class="neutral-fetch-auto"
     data-url="/api/data"
     data-wrap="content-box">
    <div>Loading...</div>
</div>
```

**Click trigger with `{:fetch;`:**
```ntpl
{:fetch; |/api/action|click|result| >>
    <button>Load Data</button>
:}
```

**Same with manual class:**
```ntpl
<button class="neutral-fetch-click"
        data-url="/api/action"
        data-wrap="result">
    Load Data
</button>
```

**Visible trigger with `{:fetch;`:**
```ntpl
{:fetch; |/api/lazy|visible|lazy-content| >>
    <div>Scroll to load...</div>
:}
```

**Same with manual class:**
```ntpl
<div class="neutral-fetch-visible"
     data-url="/api/lazy"
     data-wrap="lazy-content">
    <div>Scroll to load...</div>
</div>
```

#### **8.4 When to Use Manual Classes**

Use manual Neutral JS classes when:

1. **Custom form structure needed** - You need specific form attributes (enctype, target, novalidate)
2. **Third-party library integration** - Libraries that modify form behavior
3. **Complex event handling** - Multiple triggers or custom JavaScript logic
4. **Progressive enhancement** - Form should work without JavaScript
5. **Accessibility requirements** - Specific ARIA attributes or focus management

**Example: Custom form with file upload progress:**
```ntpl
<form class="neutral-fetch-form"
      method="POST"
      action="/api/upload"
      data-wrap="upload-result"
      enctype="multipart/form-data"
      novalidate>

    <div class="upload-zone">
        <input type="file" name="document" accept=".pdf" required>
        <div class="progress-bar" style="display:none;">
            <div class="progress"></div>
        </div>
    </div>

    <button type="submit" class="btn btn-primary">
        {:trans; Upload :}
    </button>
</form>

<script nonce="{:;CSP_NONCE:}">
    document.querySelector('form').addEventListener('submit', function(e) {
        // Custom progress handling before Neutral JS takes over
        document.querySelector('.progress-bar').style.display = 'block';
    });
</script>
```

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

**Example: Custom trigger logic:**
```javascript
// Load content after user confirmation
document.querySelector('#confirm-btn').addEventListener('click', function() {
    if (confirm('Load content?')) {
        const container = document.getElementById('dynamic-content');
        neutral_fetch(container, '/api/content', 'dynamic-content');
    }
});
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

### **10. Complete Example: Comments Component**

**Structure:**
```
neutral/route/root/
├── content-snippets.ntpl          # Comments list + form
├── ajax/
│   └── content-snippets.ntpl      # Comments list only (refresh)
├── form/
│   └── content-snippets.ntpl      # New comment form
└── snippets/
    └── comments.ntpl              # Reusable snippets
```

**Comments list (refreshable via AJAX):**

```ntpl
{:* snippets/comments.ntpl *:}

{:snip; comments-list >>
    <div id="comments-list">
        {:each; comments id comment >>
            <div class="comment card mb-2">
                <div class="card-body">
                    <h6 class="card-subtitle mb-2 text-muted">
                        {:;comment->author:} - {:;comment->date:}
                    </h6>
                    <p class="card-text">{:;comment->text:}</p>
                </div>
            </div>
        :}{:else;
            <p class="text-muted">{:trans; No comments yet. :}</p>
        :}
    </div>
:}

{:snip; comment-form >>
    <div class="card mt-3">
        <div class="card-body">
            <h5>{:trans; Add comment :}</h5>
            {:fetch; |{:;comments->manifest->route:}/form/{:;LTOKEN:}|form|comment-form-wrapper| >>
                <textarea name="text" class="form-control mb-2" rows="3" required></textarea>
                <button type="submit" class="btn btn-primary">
                    {:trans; Post :}
                </button>
            :}
            <div id="comment-form-wrapper"></div>
        </div>
    </div>
:}
```

**Main page:**

```ntpl
{:* content-snippets.ntpl *:}

{:data; {:flg; require :} >> #/data.json :}
{:!include; {:flg; require :} >> #/snippets/comments.ntpl :}

{:snip; current:template:body-main-content >>
    <div class="container">
        <h2>{:trans; Comments :}</h2>

        {:* Refreshable list via AJAX *:}
        <div id="comments-wrapper">
            {:fetch; |{:;comments->manifest->route:}/ajax|auto|comments-wrapper| >>
                <div class="text-center">
                    <span class="spinner-border"></span>
                </div>
            :}
        </div>

        {:* Form *:}
        {:snip; comment-form :}
    </div>
:}

{:^;:}
```

**AJAX Response:**

```ntpl
{:* ajax/content-snippets.ntpl *:}

{:data; {:flg; require :} >> #/data.json :}
{:!include; {:flg; require :} >> #/../snippets/comments.ntpl :}

{:snip; current:template:body-main-content >>
    {:snip; comments-list :}
:}

{:^;:}
```

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

This convention is specific to routes handled through the Neutral + Dispatcher flow and is not required for independent API endpoints outside that rendering pipeline.

---

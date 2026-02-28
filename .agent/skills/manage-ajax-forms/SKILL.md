---
name: manage-ajax-forms
description: Create or modify forms using Neutral TS, AJAX logic wrapper ({:fetch;...:}) and Modal implementations.
---

# Manage AJAX Forms with Neutral TS

This skill guides you through the creation and management of forms using Neutral TS's built-in AJAX capabilities, as well as integrating them with Modals.

- **IMPORTANT**: If a form is submitted using `fetch()` without using Neutral TS automated classes, you must explicitly set the `Requested-With-Ajax: true` header.
- **IMPORTANT**: When creating a modal, use standard Bootstrap 5 modal structure. Let the content of `.modal-body` load via Neutral's `{:fetch;...:}`.
- If you need additional context, use `view_file` on `docs/templates-neutrats-ajax.md` or `docs/ajax-neutral-requests.md`.
- Look at `src/component/cmp_5100_sign` for real implementations if needed.

## 1. Directory Structure

A recommended directory structure for a component handling AJAX forms:

```text
src/component/cmp_NNNN_name/
└── neutral/
    ├── component-init.ntpl                    # Global snippets (app-wide)
    └── route/
        ├── index-snippets.ntpl                # Component snippets (included automatically by all component routes)
        ├── form-snippets.ntpl                 # Shared snippets (e.g., error formats, layouts) use include in index-snippets
        └── root/
            ├── content-snippets.ntpl
            ├── data.json                      # Shared data
            └── subroute_name/
                ├── ajax/
                │   └── content-snippets.ntpl  # AJAX response
                ├── content-snippets.ntpl      # Container page (normal layout, ajax wrapper)
                └── snippets.ntpl              # Snippets specifically for this subroute_name or form
```

The strategy is to create a snippet containing only the form and its fetch logic. Then, include it in the main route within a wrapper, and in the AJAX or modal routes as standalone content without the wrapper.

### Important: especial file snippets

The snippet files `component-init.ntpl` and `index-snippets.ntpl` are automatically loaded by the framework; it is not necessary to use `{:include; ... :}` to load them. These are the only cases where `{:include; ... :}` is not required.

`component-init.ntpl` contains everything intended to be available app-wide.

`index-snippets.ntpl` contains everything intended to be available component-wide.


## 2. Implementing the Form Snippets

- cmp_uuid: is the uuid of the component in manifest.json

fetch syntax

```
{:fetch; |url|event|wrapperId|class|id|name| >> code :}
```

- url: url to perform fetch, mandatory.
- event: can be; none, form, visible, click, auto, default auto.
- wrapperId: alternative container wrapper ID, default none
- class: add to container class, default none
- id: container ID, default none
- name: container name, default none

In form event the container is the form itself, so the class and id are added to the form.

`index-snippets.ntpl` is automatically loaded by all component routes, but it is a better idea to create a snippet exclusive to the form, e.g., `form-snippets.ntpl`, and load it in `index-snippets.ntpl` with `{:include; #/form-snippets.ntpl :}`. This way, `form-snippets.ntpl` can be included with everything necessary for the form outside of the component route.

in `index-snippets.ntpl`, simply include the form snippets file:
```ntpl
{:include; #/form-snippets.ntpl :}
```

in `form-snippets.ntpl`
```ntpl
{:* Form content snippet *:}
{:snip; cmp_uuid:my_form-form >>
    {:fetch; |{:;cmp_uuid->manifest->route:}/subroute_name/ajax/{:;LTOKEN:}|form|my-form-wrapper|{:;local::current->forms->class:}| >>
        <div class="mb-3">
            <label class="form-label">{:trans; Name :}</label>
            <input type="text" name="name" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-primary">{:trans; Submit :}</button>
    :}
:}

{:* Success snippets *:}
{:snip; cmp_uuid:my_form-success >>
    <div class="alert alert-success">
        <h5>{:trans; Success! :}</h5>
        <p>{:;message:}</p>
    </div>
:}

{:* Error snippets *:}
{:snip; cmp_uuid:my_form-error >>
    <div class="alert alert-danger">
        <h5>{:trans; Error :}</h5>
        <p>{:;error_msg:}</p>
    </div>
:}

{:* Wrapper snippet that resolves the result *:}
{:snip; cmp_uuid:my_form-wrapper >>
    <div id="my-form-wrapper">
        {:filled; form_result >>
            {:same; /{:;form_result->status:}/success/ >>
                {:snip; cmp_uuid:my_form-success :}
            :}{:else;
                {:snip; cmp_uuid:my_form-error :}
                {:snip; cmp_uuid:my_form-form :}
            :}
        :}{:else;
            {:snip; cmp_uuid:my_form-form :}
        :}
    </div>
:}

```

- {:;local::current->forms->class:} is a preconfigured class so that all forms have the same style.
- The prefix current:template:* are snippets that are loaded in the main layout.

## 3. Creating Response Routes

In `neutral/route/root/subroute_name/content-snippets.ntpl`:

```ntpl
{:snip; current:template:body-main-content >>
    {:snip; cmp_uuid:my_form-wrapper :}
:}

{:^;:}
```

In `neutral/route/root/subroute_name/ajax/content-snippets.ntpl` (renders the form, not the wrapper — the AJAX response replaces the *contents* of `#my-form-wrapper`, so returning the wrapper would nest it inside itself):

```ntpl
{:snip; current:template:body-main-content >>
    {:snip; cmp_uuid:my_form-form :}
:}

{:^;:}
```

## 4. Modal Implementation

Loading this form inside a Modal dynamically when opened ensures optimal load times.

in `form-snippets.ntpl`

```ntpl
{:* Placing the modal in the correct layout block *:}
{:snip;  cmp_uuid:modals >>
    <div class="modal fade" id="myModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">{:trans; My Form :}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    {:* Use Neutral TS fetch (visible triggers as soon as the element appears) *:}
                    {:fetch; |{:;cmp_uuid->manifest->route:}/subroute_name/ajax/{:;LTOKEN:}|visible| >>
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
In `neutral/route/root/anyroute_name/content-snippets.ntpl` (or another appropriate template):

```ntpl
{:* Move modals to body *:}
{:moveto; /body >>
    {:snip; cmp_uuid:modals :}
:}

{:* Content snippets *:}
{:snip; current:template:body-main-content >>
    <div class="container mt-5">
        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#myModal">
            {:trans; Open Form :}
        </button>
    </div>
:}
```

## 5. Fetch Forms vs Manual AJAX Requests

### Form approach
Using `{:fetch; |url|form|wrapper|class|id| >> ... :}` handles the submission and response placement seamlessly, rendering the backend response (which will automatically be the `template-ajax.ntpl` containing just the form wrapper replacement) back into the defined wrapper id (`my-form-wrapper`).

### Native HTML class fallback
If you can't use `{:fetch;...:}`, add `class="neutral-fetch-form"` to `<form>`, setting method to `POST`, `data-wrap="wrapper-id"` and `action="url"`. The JS handles it underneath.

### Pure JS fetch
If you write `fetch(...)` directly in Javascript instead of using Neutral's systems, you **must set the header**:

```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'Requested-With-Ajax': 'true'
    },
    body: formData
})
```

## 6. Backend Route Implementation

Ensure your corresponding python route in `routes.py` correctly handles both GET (rendering the form initially via ajax in the modal) and POST (handling the submission).

```python
from flask import request, Response
from core.dispatcher import Dispatcher
from . import bp

@bp.route("/subroute_name/ajax/<token>", defaults={"route": "subroute_name"}, methods=["GET"])
def ajax_form_get(route, token) -> Response:
    dispatch = Dispatcher(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.view.render()


@bp.route("/subroute_name/ajax/<token>", defaults={"route": "subroute_name"}, methods=["POST"])
def ajax_form_post(route, token) -> Response:
    dispatch = Dispatcher(request, route, bp.neutral_route)
    # Form validation and processing...
    dispatch.schema_data["form_result"] = {
        "status": "success",
        "message": "Form submitted successfully"
    }
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.view.render()
```

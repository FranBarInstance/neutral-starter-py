# Template Component

**UUID:** `template_0yt2sa`

Base layout provider for the application. This component registers the active Neutral layout, loads the shared template snippets, and decides whether a request renders as a full HTML document or as an AJAX fragment.

## Overview

This component is the UI shell for the whole application:

- registers the current template directory through `set_current_template()`
- exposes the main layout entrypoints under `neutral/layout/`
- loads shared utility, navigation, and rendering snippets
- provides the global `neutral.js` bootstrap expected by `{:fetch; ... :}` flows
- renders full pages, AJAX fragments, and error pages with the same extension model

## Registration and Runtime Integration

`__init__.py` calls `set_current_template(component, component_schema)`.

That registration populates:

- `current->template->dir`
- `CURRENT_NEUTRAL_ROUTE`
- `CURRENT_COMP_ROUTE`

Later, `src/core/schema.py` resolves:

- `TEMPLATE_LAYOUT` -> `neutral/layout/index.ntpl`
- `TEMPLATE_ERROR` -> `neutral/layout/error.ntpl`

At request time, the route handler and the template component collaborate like this:

1. `PreparedRequest` prepares schema, headers, session, and component context.
2. A route handler sets `CURRENT_COMP_ROUTE`.
3. The `Template` class renders the active template layout.
4. `index.ntpl` includes route snippets and then selects either `template.ntpl` or `template-ajax.ntpl`.

## Layout Files

```text
src/component/cmp_XXXX_template/
├── manifest.json
├── schema.json
├── __init__.py
└── neutral/
    └── layout/
        ├── cache.ntpl
        ├── cache-error.ntpl
        ├── error.ntpl
        ├── index.ntpl
        ├── template.ntpl
        ├── template-ajax.ntpl
        ├── template-error.ntpl
        ├── template-error-ajax.ntpl
        ├── template-snippets.ntpl
        ├── template-nav-snippets.ntpl
        ├── template-error-nav-snippets.ntpl
        └── util-snippets.ntpl
```

## Rendering Flow

### Normal page requests

`cache.ntpl` caches `index.ntpl` for `current->template->cache_seconds` unless the request is AJAX.

`index.ntpl` then:

1. loads utility snippets
2. loads layout snippets
3. loads navigation snippets
4. activates the configured spinner set via `current->theme->spin`
5. executes `core:include-components-register-ntpl`
6. includes route-level `index-snippets.ntpl`
7. includes `CURRENT_NEUTRAL_ROUTE/CURRENT_COMP_ROUTE/content-snippets.ntpl`
8. optionally includes route `custom-snippets.ntpl`
9. renders `template.ntpl`

### AJAX requests

If `CONTEXT->HEADERS->Requested-With-Ajax` is present, `index.ntpl` renders `template-ajax.ntpl` instead of `template.ntpl`.

`template-ajax.ntpl` returns only:

- `current:template:body-main-content`
- debug output when cache is disabled

This is the reason route templates must always define `current:template:body-main-content`.

### Error requests

`error.ntpl` mirrors the same structure for failures:

- loads utility snippets
- loads template snippets
- loads error navigation snippets
- renders `template-error.ntpl` or `template-error-ajax.ntpl`

`cache-error.ntpl` caches the full error page using a cache key that also includes the HTTP error payload.

## Template Route Flow

The most important contract in this template system is the route content snippet:

- `current:template:body-main-content`

In practice, every route template must provide that snippet so the template component knows what content to place in the page body.

The flow is:

1. the route handler resolves `CURRENT_COMP_ROUTE`
2. `index.ntpl` includes `CURRENT_NEUTRAL_ROUTE/CURRENT_COMP_ROUTE/content-snippets.ntpl`
3. that route template defines `current:template:body-main-content`
4. `template.ntpl` renders that snippet inside the full page shell
5. if the request is AJAX, `template-ajax.ntpl` renders only that same snippet

This means the route template does not render the complete HTML document. It only declares the fragment that belongs to the route, and the base template decides whether that fragment is wrapped in the full layout or returned as an AJAX response.

As a summary rule:

- every route `content-snippets.ntpl` must provide `current:template:body-main-content`

This is the same pattern used by the example component `hellocomp_0yt2sa`, where the root route, normal subroutes, and AJAX routes all define `current:template:body-main-content` in their own `content-snippets.ntpl`.

Typical route structure:

```ntpl
{:data; {:flg; require :} >> #/data.json :}

{:snip; current:template:body-main-content >>
    <div class="{:;current->theme->class->container:}">
        <h2>{:trans; Example route :}</h2>
        <p>{:trans; Route-specific content goes here. :}</p>
    </div>
:}

{:^;:}
```

Notes:

- `data.json` loads route-local metadata such as `title`, `description`, and `h1`
- `{:^;:}` is required so the route does not fall back to the framework 404 behavior
- if a route wants different shell behavior, it should override template snippets such as `current:template:page-h1` or `current:template:body-lateral-bar`, but it must still provide `current:template:body-main-content`

## Route Data and Snippet Overrides

`data.json` is the standard place to define Neutral TS variables needed by the route in a generic way for each request. In practice, route metadata is often placed under `current->route`, because several template snippets depend on that structure.

Example:

```json
{
    "data": {
        "current": {
            "route": {
                "title": "Hello Component",
                "description": "Visual showcase component with snippets, AJAX and modals",
                "h1": "Hello Component"
            }
        }
    }
}
```

This matters because some template snippets expect those variables to exist. For example:

- `current:template:page-h1` uses `local::current->route->h1`
- the default `<title>` and description fallback use `local::current->route->title` and `local::current->route->description`

So, in the default template behavior:

- `current->route->title` is used for the HTML `<title>`
- `current->route->description` is used for the HTML meta description

Any of these snippets can be overridden by the route when needed. They can also be disabled completely by redefining them as empty snippets.

Example:

```ntpl
{:snip; current:template:page-h1 >> :}
```

That leaves the snippet intentionally empty, so the base template will render nothing in that slot.

For more control over the `<head>` metadata, a route can override `current:template:meta-title-description` directly:

```ntpl
{:snip; current:template:meta-title-description >>
    <title>{:trans; Title :}</title>
    <meta name="description" content="{:trans; Description :}" />
    <meta name="..." content="..." />
:}
```

When this snippet is defined, the default fallback is bypassed, so `current->route->title` and `current->route->description` are ignored for title/description rendering.

## Public Snippet Contract

These snippets form the practical extension surface used by route templates and other components.

### Required route snippet

- `current:template:body-main-content`
  - Required in every route `content-snippets.ntpl`.
  - Full-page and AJAX rendering both depend on it.

### Common page extension points

- `current:template:meta-title-description`
  - Optional override for `<title>` and description meta.
  - Default fallback uses `local::current->route->title` and `description`.
- `current:template:page-h1`
  - Default `<h1>` renderer using `local::current->route->h1`.
- `current:template:body-hero`
  - Empty by default.
- `current:template:body-carousel`
  - Renders `local::current->carousel` when present.
- `current:template:body-lateral-bar`
  - Default right-column informational sidebar.
- `current:template:body-footer`
  - Default footer.
- `current:template:modals`
  - Global modal container with `#templateHelp`.

### Navigation snippets

- `current:template:main-navbar`
- `current:template:main-navbar-right-content`
- `current:template:main-navbar-bottom-content`
- `current:template:main-navbar-notices-content`
- `current:template:main-drawer`
- `current:template:main-drawer-button`
- `current:template:main-drawer-items-icons`
- `current:template:main-drawer-items-menu`

These snippets consume data merged into schema, especially:

- `current->drawer`
- `current->menu`
- `navbar->menu`
- `current->site`
- `current->theme`

### Error-page navigation snippets

- `current:template:main-navbar-error`
- `current:template:main-drawer-error`

### Spinner snippets

The configured set (`current->theme->spin`) defines:

- `spin-1x`
- `spin-lg`
- `spin-2x`
- `spin-3x`
- `spin-4x`
- `spin-5x`

Available sets:

- `current:template:spin-set-spin1`
- `current:template:spin-set-spin2`
- `current:template:spin-set-spin3`
- `current:template:spin-set-spin4`
- `current:template:spin-set-spin5`
- `current:template:spin-set-spin6`

### Utility snippets

Provided by `util-snippets.ntpl`:

- `util:modal-back-button`
- `util:reload-page-self`
- `util:reload-page-home`
- `util:redirection`
- `util:error-utoken`
- `util:requires-utoken`

These snippets also install utility JavaScript that reacts on `DOMContentLoaded` and `neutralFetchCompleted`.

### Client bootstrap snippet

- `neutral.js`
  - injects the Neutral runtime configuration
  - loads `js/neutral.min.js`
  - rebinds post-AJAX behaviors such as popovers and form reset buttons
  - manages temporary loading states for `.click-load-spin`

## Cache Behavior

`schema.json` exposes:

- `current->template->cache_seconds`
- `current->template->error_cache_seconds`
- `current->template->nav_cache_seconds`

Cache keys include:

- active theme
- theme color
- session presence
- AJAX header presence
- for error pages, HTTP error code/text/param

Navbar and drawer rendering are separately cached inside `template.ntpl`.

## Theme and CSP Behavior

The template is CSP-aware:

- inline `<style>` and `<script>` blocks include `{:;CSP_NONCE:}`
- `neutral.min.js` is loaded explicitly because automatic Neutral JS injection is disabled globally

Theme-specific CSS workarounds currently exist for:

- `litera`
- `journal`
- `sketchy`

## Route Authoring Rules

When a component renders inside this template:

1. define `current:template:body-main-content`
2. end `content-snippets.ntpl` with `{:^;:}`
3. use `Requested-With-Ajax` for manual AJAX requests that expect fragment rendering
4. override snippets only when the route needs to change the default shell behavior

Minimal example:

```ntpl
{:data; {:flg; require :} >> #/data.json :}

{:snip; current:template:body-main-content >>
    <div class="{:;current->theme->class->container:}">
        <h2>{:trans; Example :}</h2>
    </div>
:}

{:^;:}
```

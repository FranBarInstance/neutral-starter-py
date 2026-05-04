# Component: template_0yt2sa

## Executive Summary

This component is the default application layout provider. It registers the active Neutral template directory, supplies the shell used by all route-driven pages, and owns the switch between full-document rendering and AJAX fragment rendering.

The component is intentionally foundational:

- it is initialized very early in the component load order
- `src/core/schema.py` depends on its registration to resolve `TEMPLATE_LAYOUT` and `TEMPLATE_ERROR`
- every route rendered through the standard `RequestHandler` pipeline ultimately passes through this component's layout contract

Its behavior is not limited to HTML framing. It also provides:

- navigation and drawer snippets
- spinner sets
- utility snippets for redirection, cookie/token recovery, and modal controls
- the shared `neutral.js` bootstrap required by the project's AJAX model
- theme-specific CSS workarounds
- cache boundaries for normal pages, error pages, and navigation

## Identity

- **UUID**: `template_0yt2sa`
- **Base Route**: `` (no direct route ownership)
- **Version**: `0.0.0`

## Runtime Registration Contract

The component registers itself in `__init__.py` via:

```python
from app.components import set_current_template

def init_component(component, component_schema, _schema):
    set_current_template(component, component_schema)
```

That call populates the schema with:

- `current->template->dir`
- `CURRENT_NEUTRAL_ROUTE`
- `CURRENT_COMP_ROUTE`

At schema bootstrap time, `src/core/schema.py` uses that registration to derive:

- `TEMPLATE_LAYOUT = <template dir>/layout/<Config.TEMPLATE_NAME>`
- `TEMPLATE_ERROR = <template dir>/layout/<Config.TEMPLATE_NAME_ERROR>`

This means the component is the effective source of truth for application page layout selection.

## Normative References

- `docs/development.md`
- `docs/templates-neutrats.md`
- `docs/templates-neutrats-ajax.md`
- `docs/ajax-neutral-requests.md`
- `.specify/specs/002-neutral-templates-standard/provider-spec.md`
- `src/app/components.py`
- `src/core/schema.py`
- `src/core/prepared_request.py`

## Directory Structure

```text
src/component/cmp_0200_template/
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

## Functional Responsibilities

### 1. Application layout selection

`index.ntpl` is the main dispatcher for successful route rendering.

It performs these steps in order:

1. load utility snippets from `util-snippets.ntpl`
2. load general layout snippets from `template-snippets.ntpl`
3. load navigation snippets from `template-nav-snippets.ntpl`
4. activate the configured spinner family by calling `{:snip; {:;current->theme->spin:} :}`
5. execute `core:include-components-register-ntpl`
6. include route-level `index-snippets.ntpl` if present
7. include the route `content-snippets.ntpl`
8. include route `custom-snippets.ntpl` if present
9. choose `template.ntpl` or `template-ajax.ntpl`

If the route content include fails, `index.ntpl` exits with `404`.

### 2. AJAX/full-page mode switching

The rendering mode is selected using `CONTEXT->HEADERS->Requested-With-Ajax`.

- If the header is absent: render `template.ntpl`
- If the header is present: render `template-ajax.ntpl`

`template-ajax.ntpl` intentionally emits only:

- `current:template:body-main-content`
- debug output when cache is disabled

Therefore, the snippet `current:template:body-main-content` is mandatory for every route that uses this template.

### 3. Error-page rendering

`error.ntpl` mirrors the normal rendering flow but swaps route navigation for error navigation:

- utility snippets
- general template snippets
- error navigation snippets
- configured spinner family
- `core:include-components-register-ntpl`
- `template-error.ntpl` or `template-error-ajax.ntpl`

`template-error.ntpl` renders:

- a full HTML document
- a theme-aware navbar with a home action
- translated error title and fallback message
- debug buttons when cache is disabled
- footer, modals, and Neutral JS bootstrap

`template-error-ajax.ntpl` renders only the compact error fragment.

### 4. Shared shell and structure

`template.ntpl` owns the page skeleton:

- `<!DOCTYPE html>`
- `<html lang=... dir=...>`
- `<head>` metadata
- `<body>` shell
- main navbar and drawer
- optional carousel
- optional hero
- page heading
- main content container
- optional lateral bar
- footer
- modal container
- global scripts

The lateral bar is conditional:

- if `current:template:body-lateral-bar` evaluates to non-empty, it becomes a right column
- otherwise the main content spans the full width

## Snippet Contract

This component exposes the following practical extension points.

### Required snippet

- `current:template:body-main-content`

This is the required injection point for every route `content-snippets.ntpl`.

### Common optional overrides

- `current:template:meta-title-description`
- `current:template:page-h1`
- `current:template:body-hero`
- `current:template:body-carousel`
- `current:template:body-lateral-bar`
- `current:template:body-footer`
- `current:template:modals`

Default behavior:

- `page-h1` renders `local::current->route->h1` when present
- `body-hero` is empty
- `body-carousel` renders `local::current->carousel`
- `body-footer` renders the Neutral TS footer
- `modals` provides the `#templateHelp` bootstrap modal

### Navigation snippets

- `current:template:main-navbar`
- `current:template:main-navbar-right-content`
- `current:template:main-navbar-bottom-content`
- `current:template:main-navbar-notices-content`
- `current:template:main-drawer`
- `current:template:main-drawer-button`
- `current:template:main-drawer-items-icons`
- `current:template:main-drawer-items-menu`
- `current:template:main-drawer-opt`

These snippets render from merged schema data, especially:

- `current->drawer`
- `current->menu`
- `navbar->menu`
- `current->site`
- `current->theme`
- `HAS_SESSION`

### Error navigation snippets

- `current:template:main-navbar-error`
- `current:template:main-drawer-error`

### Cache-key snippets

- `current:template:cache-key`
- `current:template:error-cache-key`

These key builders include theme, theme color, session state, and AJAX mode. The error key also includes the HTTP error payload.

### Typography snippets

- `current:template:heading-small`
- `current:template:heading-medium`

These inject CSP-safe inline CSS with `{:;CSP_NONCE:}`.

### Spinner snippets

The component exposes six spinner families:

- `current:template:spin-set-spin1`
- `current:template:spin-set-spin2`
- `current:template:spin-set-spin3`
- `current:template:spin-set-spin4`
- `current:template:spin-set-spin5`
- `current:template:spin-set-spin6`

Each family defines:

- `spin-1x`
- `spin-lg`
- `spin-2x`
- `spin-3x`
- `spin-4x`
- `spin-5x`

The active family is selected by `current->theme->spin`.

### Utility snippets

`util-snippets.ntpl` provides:

- `util:modal-back-button`
- `util:reload-page-self`
- `util:reload-page-home`
- `util:redirection`
- `util:error-utoken`
- `util:requires-utoken`

These snippets are not purely markup helpers. They also rely on a script block moved to the body that dispatches:

- self-reload flows
- home redirection flows
- generic timed redirection
- UTOKEN recovery behavior for cookie-dependent pages

### Client bootstrap snippet

- `neutral.js`

This snippet is part of the template contract because the project disables automatic Neutral JS injection globally.

It configures:

- `neutral_submit_loading`
- `neutral_submit_timeout`
- `neutral_submit_error`
- `neutral_submit_error_delay`
- `neutral_submit_delay`

It also:

- loads `js/neutral.min.js`
- rebinds `.fetch-form-button-reset` behavior after AJAX replacements
- reinitializes Bootstrap popovers after AJAX replacements
- manages temporary loading states for `.click-load-spin`
- restores loading-button content on `pagehide`

## Data and Configuration Dependencies

### Schema-driven data

The component depends on shared schema fields such as:

- `current->site`
- `current->theme`
- `current->drawer`
- `current->menu`
- `navbar->menu`
- `local::current->route`
- `local::current->carousel`
- `HAS_SESSION`
- `HTTP_ERROR`

### Component-local configuration

`schema.json` contributes:

- translations for core layout/error text in `en`, `es`, `de`, `fr`, `ar`, `zh`
- cache durations under `current->template`

Current cache-related values:

- `cache_seconds = 300`
- `error_cache_seconds = 300`
- `nav_cache_seconds = 30`

## Cache Semantics

`cache.ntpl` applies page caching only to non-AJAX requests.

Behavior:

- AJAX requests bypass outer page cache
- normal requests cache `index.ntpl`
- error pages use `cache-error.ntpl`
- navigation is separately cached inside `template.ntpl`

This split is intentional:

- full pages benefit from coarse caching
- AJAX fragments remain request-specific
- nav content can refresh more frequently than the page shell

## Theme and CSP Behavior

The component is explicitly CSP-aware:

- all inline styles use `nonce="{:;CSP_NONCE:}"`
- all inline scripts use `nonce="{:;CSP_NONCE:}"`

It also ships theme-specific CSS workarounds for:

- `litera`
- `journal`
- `sketchy`

These are runtime template concerns, not static asset concerns, because they depend on the active theme selection in schema.

## AJAX Contract with the Rest of the Application

This component is central to the project-wide AJAX convention.

The effective contract is:

1. clients performing in-app AJAX must send `Requested-With-Ajax`
2. route templates must define `current:template:body-main-content`
3. AJAX responses should render fragments, not whole HTML documents
4. post-AJAX client behavior must rebind through `neutralFetchCompleted`

Neutral-driven requests using `{:fetch; ... :}` satisfy the header requirement automatically once `neutral.js` is loaded.

Manual JavaScript requests must add the header explicitly when they expect fragment semantics.

## Error Handling and Fail-Closed Behavior

The component follows a fail-closed posture:

- missing route content resolves to `404`
- error responses use dedicated layouts rather than returning partial broken page shells
- cookie/token-dependent utility flows surface a translated error state when automatic recovery is not possible

This makes the component part of the platform's resilience layer, not just its visual layer.

## Acceptance Criteria

### Functional

- [x] Registers the active application template through `set_current_template()`
- [x] Provides a normal-page dispatcher (`index.ntpl`)
- [x] Provides full-page, AJAX, error-page, and AJAX-error renderers
- [x] Exposes route-level extension points through `current:template:*` snippets
- [x] Provides shared navbar, drawer, footer, modal, spinner, and utility snippets
- [x] Supplies the global Neutral JS bootstrap used by AJAX flows

### Technical

- [x] Uses CSP nonces for inline styles and scripts
- [x] Supports request-mode branching via `Requested-With-Ajax`
- [x] Separates normal-page cache, error-page cache, and nav cache
- [x] Resolves error views without depending on route-level content

### Integration

- [x] Compatible with the standard `PreparedRequest` + `RequestHandler` pipeline
- [x] Compatible with Neutral `{:fetch; ... :}` AJAX flows
- [x] Provides the mandatory layout contract expected by route `content-snippets.ntpl`
- [x] Uses schema-driven theme and navigation data without owning route business logic

## Notes for Component Authors

Any component rendered inside this layout should assume:

1. `current:template:body-main-content` is mandatory
2. AJAX-specific routes should still reuse the same inner content contract
3. manual AJAX code must send `Requested-With-Ajax`
4. shell-level overrides should be implemented as snippet overrides, not by bypassing the template

This component is therefore both infrastructure and API surface for the rest of the UI layer.

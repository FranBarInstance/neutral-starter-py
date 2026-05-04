# 002-neutral-templates-standard - Layout Provider Requirements

## Executive Summary

This document defines the **interface contract** between the application
rendering runtime and any component that wants to provide the base page layout.

It is not a full NTPL specification and not a visual design guide. It only
defines what the core expects from the component acting as the layout
provider.

The provider is free to choose:

- the exact internal structure of its snippets and layouts;
- the visual strategy for navbar, drawer, footer, or modals;
- theme, branding, and styling;
- the composition details of helper snippets.

But it must satisfy the minimum contract so that `Template`,
`PreparedRequest`, and component `content-snippets.ntpl` files work
consistently.

## 1. Mandatory Requirements

### 1.1 Registration in the schema

The provider must call `set_current_template()` in its `init_component()`:

```python
from app.components import set_current_template

def init_component(component, component_schema, _schema):
    set_current_template(component, component_schema)
```

This registers at least:

- `data.current.template.dir`
- `data.CURRENT_NEUTRAL_ROUTE`
- `data.CURRENT_COMP_ROUTE`

### 1.2 Multiple providers: last one wins

`set_current_template()` may be called by multiple active components. The last
loaded component that calls it becomes the effective provider.

This allows:

- overriding the base template without modifying the default provider;
- customizing the global application shell through load order;
- replacing the provider by enabling or disabling components.

Important:

- provider selection happens at startup;
- the active provider remains static during the process lifetime;
- consumers (`Template`) do not know the concrete component and only use
  `TEMPLATE_LAYOUT` and `TEMPLATE_ERROR` as resolved in the schema.

### 1.3 Entry layouts must exist

At minimum, the following files must exist under the directory registered in
`current->template->dir`:

```text
layout/index.ntpl
layout/error.ntpl
```

In addition, `src/core/schema.py` resolves:

- `TEMPLATE_LAYOUT = <template_dir>/layout/<Config.TEMPLATE_NAME>`
- `TEMPLATE_ERROR = <template_dir>/layout/<Config.TEMPLATE_NAME_ERROR>`

The provider must therefore respect the naming convention configured by the
core.

### 1.4 Route orchestration contract

The base layout must include the current route content using:

- `CURRENT_NEUTRAL_ROUTE`
- `CURRENT_COMP_ROUTE`

The expected contract is that the provider includes the current route
`content-snippets.ntpl` and renders the snippet:

- `current:template:body-main-content`

The runtime expects every route to define that snippet. The layout provider
must consume it as the main content insertion point.

### 1.5 Full-page / AJAX compatibility

The provider must distinguish between a full request and an AJAX request using
the header:

- `Requested-With-Ajax`

Minimum expected behavior:

- normal request: render a full HTML document;
- AJAX request: render only the main content fragment.

The simplest recommended pattern is:

```ntpl
{:bool; CONTEXT->HEADERS->Requested-With-Ajax >>
    {:include; {:flg; require :} >> #/template-ajax.ntpl :}
:}{:else;
    {:include; {:flg; require :} >> #/template.ntpl :}
:}
```

### 1.6 Main snippet contract

The provider must reserve and consume the snippet:

- `current:template:body-main-content`

This snippet:

- must be defined by every route `content-snippets.ntpl`;
- is placed inside `<main>` in full-page mode;
- is returned directly in AJAX mode.

Without this contract, route components cannot integrate correctly with the
layout.

## 2. Data Available to the Provider

The layout provider may assume the schema already contains at least:

| Variable | Source | Description |
|---|---|---|
| `CURRENT_NEUTRAL_ROUTE` | `PreparedRequest` / `set_current_template()` | Neutral directory of the current route. |
| `CURRENT_COMP_ROUTE` | `RequestHandler` | Current relative route within the component. |
| `CONTEXT` | `PreparedRequest` | Full HTTP context. |
| `CSP_NONCE` | `PreparedRequest` | CSP nonce. |
| `HTTP_ERROR` | View | Error object during error rendering. |
| `current->theme` | global schema | Theme, colors, and visual classes. |
| `current->site` | global schema | Site metadata. |
| `local::current->route` | route `data.json` | Current route metadata. |

The provider may also define and consume its own snippets under the
`current:template:*` namespace.

## 3. Layout Responsibilities

### 3.1 Orchestrate common files

The provider must act as the orchestration layer between:

- global layout snippets;
- `component-init.ntpl` files accumulated by the core;
- the route component `index-snippets.ntpl`;
- the route `content-snippets.ntpl`;
- full-page layout;
- AJAX layout;
- error layout.

### 3.2 Reserve stable extension points

At minimum, the following extension snippets are recommended:

- `current:template:meta-title-description`
- `current:template:page-h1`
- `current:template:body-main-content`
- `current:template:body-lateral-bar`
- `current:template:body-footer`
- `current:template:modals`

Only `current:template:body-main-content` is mandatory, but the others provide
useful stable integration points.

### 3.3 Handle default metadata

The provider should support default route metadata based on:

- `local::current->route->title`
- `local::current->route->description`
- `local::current->route->h1`

It should also allow a route to override the metadata block completely through
a snippet such as:

- `current:template:meta-title-description`

### 3.4 Render errors independently

The provider must expose an error rendering flow separate from the normal page
flow, so that an error response does not depend on successful route content
rendering.

At minimum, `layout/error.ntpl` must exist and resolve either a full-page or
AJAX error view.

## 4. Recommended Optional Requirements

### 4.1 Navigation snippets

It is recommended to expose separate snippets for:

- navbar;
- drawer;
- footer;
- modals;
- theme workarounds;
- JS runtime bootstrap.

This lets routes override behavior without reimplementing the entire layout.

### 4.2 Separate cache handling

It is recommended to differentiate:

- full-page cache;
- error-page cache;
- navigation fragment cache.

### 4.3 Strict CSP

Any inline `<script>` or `<style>` should include:

```html
nonce="{:;CSP_NONCE:}"
```

### 4.4 Explicit Neutral JS loading

If the application does not inject `neutral.min.js` automatically, the
provider must ensure it is loaded manually so the `{:fetch; ... :}` flow
remains operational.

## 5. Minimal Implementation Example

### 5.1 Registration

```python
from app.components import set_current_template

def init_component(component, component_schema, _schema):
    set_current_template(component, component_schema)
```

### 5.2 Minimal orchestrator

```ntpl
{:include; {:;CURRENT_NEUTRAL_ROUTE:}/index-snippets.ntpl :}
{:include; {:;CURRENT_NEUTRAL_ROUTE:}/{:;CURRENT_COMP_ROUTE:}/content-snippets.ntpl :}

{:bool; CONTEXT->HEADERS->Requested-With-Ajax >>
    {:include; {:flg; require :} >> #/template-ajax.ntpl :}
:}{:else;
    {:include; {:flg; require :} >> #/template.ntpl :}
:}
```

### 5.3 Minimal AJAX layout

```ntpl
{:snip; current:template:body-main-content :}
```

### 5.4 Minimal full-page layout

```ntpl
<!DOCTYPE html>
<html lang="{:lang;:}">
<head>
    <title>{:;local::current->route->title:}</title>
</head>
<body>
    <main>
        {:snip; current:template:body-main-content :}
    </main>
</body>
</html>
```

## 6. Normative References

- `spec.md` (`002-neutral-templates-standard`) - general NTPL standard
- `spec.md` (`000-core-system`) - runtime, schema, and request pipeline
- `spec.md` (`001-component-standard`) - component contract
- `docs/templates-neutrats.md`
- `docs/templates-neutrats-ajax.md`

---

This is an interface-contract specification. The provider decides how to
implement it, but it must respect the runtime's observable contract.

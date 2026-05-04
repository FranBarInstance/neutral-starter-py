# Specification 002 - Neutral TS Template Standard (NTPL)

## Summary

Neutral TS is the project's logical, declarative, language-independent
template engine. In this repository, NTPL files bridge Python-prepared runtime
data and the final HTML returned to the client.

NTPL in this project is based on strict separation of responsibilities:

- backend code prepares state and data;
- templates present that data;
- route-specific content is composed through reusable snippets instead of
  monolithic pages.

This specification defines the normative contract for writing, reviewing, and
maintaining `.ntpl` files in the project. It must be read together with:

- `.specify/memory/constitution.md`
- `.specify/OVERVIEW.md`
- `.specify/specs/000-core-system/spec.md`
- `.specify/specs/001-component-standard/spec.md`
- `.specify/specs/003-forms-standard/spec.md`
- `.specify/specs/004-static-assets-delivery/spec.md`
- `.specify/specs/002-neutral-templates-standard/provider-spec.md`
- `.agents/skills/manage-neutral-templates/SKILL.md`
- `docs/templates-neutrats.md`
- `docs/templates-neutrats-ajax.md`
- `docs/security-csp.md`

## Goals

- define the anatomy of valid project `.ntpl` files;
- document immutable data (`schema.data`), mutable local data
  (`schema.inherit.data` / `local::`), and `CONTEXT`;
- establish the rendering architecture of global layout, full-page template,
  AJAX template, and route content;
- define template security rules: CSP, escaping, safe inclusion, and nonce use;
- document translation usage through `{:trans; ... :}`;
- normalize AJAX rendering through `{:fetch; ... :}` and full-page/fragment
  duality.

## Non-goals

- no attempt to replace the full upstream Neutral TS documentation;
- no backend contract definition here;
- no component loader contract here;
- no deep form-processing contract here;
- no static-delivery contract here.

## Definitions

| Term | Definition |
|---|---|
| BIF | Built-in Function from the NTPL engine. |
| Snippet | Reusable fragment defined and later consumed by name. |
| `schema.data` | Immutable data exposed as `{:;...:}`. |
| `schema.inherit.data` | Mutable local data, commonly read as `local::...`. |
| `CONTEXT` | Reserved node with user input and request context. |
| `content-snippets.ntpl` | Route file that defines the route's snippet output. |
| `index-snippets.ntpl` | Per-component route-wide shared snippet loader. |
| `component-init.ntpl` | Optional component-global initialization snippet. |
| Layout provider | The active component that provides the base web layout contract. |

## Normative Principles

### Separation of responsibilities

Templates must not implement business logic. If a template needs data shaping,
that shaping belongs in Python or in a declarative JSON model upstream.

### Composition over monolith

Route `content-snippets.ntpl` files must not act as complete standalone HTML
documents. Route content is inserted into the active layout through snippets.

### Security by default

User input in `CONTEXT` is treated as untrusted. Inline `<script>` or
`<style>` tags require `nonce="{:;CSP_NONCE:}"`. Raw output for untrusted data
is forbidden.

### Transparent localization

User-visible strings should be wrapped in `{:trans; ... :}` or expressed
through reference keys.

## Rendering Architecture

The runtime renders a request through a deterministic chain of files and
snippets.

### Rendering layers

| Order | File | Responsibility |
|---|---|---|
| 1 | provider `layout/index.ntpl` | Orchestrator: load helpers, route snippets, and choose full-page vs AJAX. |
| 2 | provider `layout/template-snippets.ntpl` | Default global snippets. |
| 3 | provider `layout/template.ntpl` | Full HTML page shell. |
| 4 | provider `layout/template-ajax.ntpl` | AJAX fragment shell. |
| 5 | route `content-snippets.ntpl` | Route-specific snippet definitions. |
| 6 | component `index-snippets.ntpl` | Component-wide route snippet/data/locale loader. |

### Orchestrator (`index.ntpl`)

The active provider's `layout/index.ntpl` is the single entry point for normal
rendering. It is expected to:

1. load helper snippets;
2. load provider default snippets;
3. load any provider navigation snippets;
4. execute global component init snippets;
5. include the current component `index-snippets.ntpl`;
6. include the current route `content-snippets.ntpl`;
7. optionally include route-local custom overrides;
8. decide between `template.ntpl` and `template-ajax.ntpl` using
   `Requested-With-Ajax`.

Minimal pattern:

```ntpl
{:bool; CONTEXT->HEADERS->Requested-With-Ajax >>
    {:include; {:flg; require :} >> #/template-ajax.ntpl :}
:}{:else;
    {:include; {:flg; require :} >> #/template.ntpl :}
:}
```

### Full-page template (`template.ntpl`)

The full-page layout is responsible for:

- valid HTML structure;
- `<html lang="{:lang;:}">` or equivalent language propagation;
- metadata, title, description, viewport, and CSP-sensitive assets;
- placing `current:template:body-main-content` inside the main content area;
- rendering stable optional areas such as header, navigation, footer, drawer,
  modals, and route H1 snippets.

### AJAX template (`template-ajax.ntpl`)

The AJAX layout must render only the fragment intended for replacement, usually:

```ntpl
{:snip; current:template:body-main-content :}
```

It must not emit a second `<html>`, `<head>`, or full-page wrapper.

### Default snippets (`template-snippets.ntpl`)

The provider should define stable defaults for snippets such as:

- `current:template:meta-title-description`
- `current:template:page-h1`
- `current:template:body-main-content`
- `current:template:body-lateral-bar`
- `current:template:body-footer`
- `current:template:modals`

Only `current:template:body-main-content` is mandatory for route integration,
but the rest provide useful extension points.

### Route content (`content-snippets.ntpl`)

Every route `content-snippets.ntpl` must:

1. load route-local data when needed, usually through `data.json`;
2. load route-local locale files when needed;
3. optionally override provider snippets;
4. define `current:template:body-main-content`;
5. optionally null out snippets by redefining them empty.

A route may blank a snippet explicitly:

```ntpl
{:snip; current:template:page-h1 >> :}
```

### Auto-loaded files

| File | Scope | Auto-loaded |
|---|---|---|
| `component-init.ntpl` | Application-global | Yes, once per active component |
| `neutral/route/index-snippets.ntpl` | Whole component | Yes, before each route render |
| `neutral/route/form-snippets.ntpl` | Whole component | No, include explicitly |
| route `content-snippets.ntpl` | Specific route | Yes, via the layout orchestrator |
| `snippets.ntpl` | Arbitrary route/subroute | No, include explicitly |

## Data System and Variables

### Immutable data: `schema.data`

Injected by the backend or defined in `schema.json`. Templates access it as:

```ntpl
{:;current->theme->color:}
{:;user->email:}
```

### Mutable local data: `local::...`

Route `data.json` and related mutable route-level data are accessed as local
data:

```ntpl
{:;local::current->route->title:}
{:;local::current->route->description:}
{:;local::current->route->h1:}
```

If the same conceptual value must be overrideable dynamically, the default
should be placed in `inherit.data` upstream so route-local data can replace it.

### Request context: `CONTEXT`

User-controlled request data lives under `CONTEXT`, including:

- `GET`
- `POST`
- `COOKIES`
- `HEADERS`
- `ENV`
- session-derived runtime branches exposed by the core

This data is untrusted and must not be rendered raw.

### Core-injected automatic variables

The core and request pipeline typically inject:

- `CURRENT_NEUTRAL_ROUTE`
- `CURRENT_COMP_ROUTE`
- `CSP_NONCE`
- current theme/site data
- locale/current language data
- request/session/user data

## Route Metadata Conventions

The default layout should support route metadata through:

- `local::current->route->title`
- `local::current->route->description`
- `local::current->route->h1`

`title` and `description` are the fallback sources for the HTML `<title>` and
the standard description meta tag.

If a route defines:

```ntpl
{:snip; current:template:meta-title-description >>
    <title>{:trans;Title :}</title>
    <meta name="description" content="{:trans; Description :}" />
:}
```

then that snippet fully replaces the fallback mechanism and
`current.route.title` / `current.route.description` are ignored for that block.

## Security Rules

- never render untrusted request data through raw output;
- do not build dynamic include paths from unvalidated user input;
- include CSP nonces on inline script/style blocks;
- avoid inline event handlers and unsafe inline JS unless the repository's CSP
  strategy explicitly permits it;
- prefer external assets and declarative DOM hooks.

## AJAX and `{:fetch; ... :}`

AJAX interactions must remain compatible with the shared form and fragment
rendering model:

- full pages and AJAX fragments must share the same route content contract;
- AJAX requests should typically receive only the snippet-backed fragment;
- form flows and fragment replacement belong to specification 003.

## Internationalization

- user-visible text should use `{:trans; ... :}`;
- component locale files live under `neutral/route/locale-*.json`;
- reference keys may be used for reusable text;
- locale behavior must remain consistent with specification 009.

## Static Assets

Static asset URLs in templates must use the dynamic prefix contract defined by
specification 004, typically through `{:;current->site->static:}`.

## Acceptance Criteria

- [x] route content is composed through snippets, not standalone monoliths;
- [x] every route provides `current:template:body-main-content`;
- [x] route-local `data.json` values are consumed through `local::...`;
- [x] fallback title/description behavior is documented and overrideable;
- [x] CSP nonce rules are enforced for inline-sensitive markup;
- [x] full-page and AJAX rendering remain compatible with the same route
  content contract.

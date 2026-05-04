# Specification 001 - Component Standard

## Summary

In Neutral Starter Py, a **component** is the atomic extension unit of the
application. A component may encapsulate identity, configuration, route
security, Flask routes, handlers, NTPL templates, static assets, translations,
data models, tests, and its own SDD documentation.

The application must grow by adding, replacing, or disabling components under
`src/component/`, not by moving business logic into the core.

This specification defines the contract every active component must satisfy. It
must be read together with:

- `.specify/memory/constitution.md`
- `.specify/specs/000-core-system/spec.md`
- `.specify/specs/002-neutral-templates-standard/spec.md`
- `.specify/specs/003-forms-standard/spec.md`
- `.agents/skills/manage-component/SKILL.md`
- `.agents/skills/manage-neutral-templates/SKILL.md`
- `.agents/skills/manage-ajax-forms/SKILL.md`
- `.agents/skills/translate-component/SKILL.md`

## Goals

- make each feature localizable, auditable, and replaceable as a unit;
- keep structure predictable for humans, tests, and AI agents;
- guarantee declarative per-component security through `manifest.json`;
- prevent tests, docs, or examples from depending on volatile folder names;
- preserve compatibility with CSP, i18n, AJAX-first forms, and deterministic
  load order.

## Non-goals

- no full NTPL syntax definition here;
- no detailed AJAX-form contract here;
- no business logic in the core to avoid creating a component;
- no treating the `cmp_*` folder name as stable component identity.

## Definitions

| Term | Definition |
|---|---|
| Active component | A directory under `src/component/` whose name starts with `cmp_` and has a valid `manifest.json`. |
| Disabled/example component | Any directory not starting with `cmp_`, usually `_cmp_*`. The runtime must ignore it completely. |
| Local development component | A component with suffix `_local` (e.g., `cmp_9999_mylocal_local`). Ignored by git, loaded by runtime. |
| Component UUID | The `uuid` value from `manifest.json`. This is the stable identity. |
| Base route | The `route` value from `manifest.json`, documented as `<manifest.route>`. |
| Subroute | A path relative to the component base route, such as `/`, `/admin`, or `/form`. |
| Component schema | The effective `schema.json` after applying overrides. |
| Route schema | `route/schema.json`, primarily used by forms and validation handlers. |

## Discovery and Lifecycle

### Discovery

The loader scans `src/component/` alphabetically and only loads directories that
start with `cmp_`.

Rules:

- `cmp_*` loads;
- `_cmp_*` is ignored and may serve as an example or disabled component;
- loose files in `src/component/` are ignored;
- an active component without a valid `manifest.json` must block startup.

### Disabled components

Disabled components must remain completely outside the active runtime:

- no manifest activation;
- no blueprints, routes, hooks, snippets, schemas, assets, or models;
- no participation in global component maps;
- no execution in the normal test suite.

Rehabilitating a disabled component is an explicit task: either rename it back
to `cmp_*` or load it through isolated, documented test configuration.

### Local development pattern (`*_local`)

Components with the `_local` suffix (e.g., `cmp_9999_test_local`) are a special
category for local development only:

**Purpose:**
- Develop components without committing them to the repository
- Test component ideas before formal integration
- Maintain personal/local components that shouldn't be shared

**Behavior:**
- **Git**: Ignored via `.gitignore` (`/src/component/*_local/`). Never committed.
- **Runtime**: Loaded normally like any other `cmp_*` component
- **Naming**: Follows the same `cmp_NNNN_name_local` pattern
- **Promotion**: Rename by removing `_local` suffix to integrate into repository

**Difference from `_cmp_*`:**
- `_cmp_*` prefixes (disabled/example): Runtime **ignores** completely
- `*_local` suffix (local dev): Runtime **loads** normally, git ignores

These patterns are complementary:
- Use `_cmp_*` for disabled/example components that should not run
- Use `*_local` for active development components that should run but not commit

**Example workflow:**
1. Create `src/component/cmp_0900_experiment_local/` for testing
2. Develop and test the component locally
3. When ready: rename to `cmp_0900_experiment/` and commit

**Caution:**
- `_local` components are not backed up by git
- They may break if dependencies change (since they're not tracked)
- Use only for temporary/experimental work

**See also:** `.gitignore` configuration and local development workflow in project documentation.

### Load order

Alphabetical folder order controls precedence and composition:

- lower prefixes usually provide base/shared behavior;
- later components may extend or override data, snippets, or routes;
- `cmp_9*` components are late fallbacks.

Folder order is a load-order decision, not the stable identity. Docs, tests,
and specs must use the component UUID or `<manifest.route>`.

### Effective startup lifecycle

The effective component contract is built in this order:

1. discover active `cmp_*` directories;
2. read and validate `manifest.json`;
3. read local `custom.json`, if present;
4. read centralized overrides from `config/config.db`, if present;
5. apply manifest overrides;
6. register the component in the global schema by UUID and folder metadata;
7. register `neutral/component-init.ntpl`, if present;
8. read `schema.json`, if present;
9. apply schema overrides;
10. merge the component schema into the global schema;
11. resolve schema dynamic references such as `[:;...:]`;
12. execute `init_component(...)`, if present;
13. register the blueprint via `init_blueprint(...)`, if present;
14. expose `route/schema.json` as route handler schema when present;
15. accumulate `component-init.ntpl` into the shared registration snippet.

## Directory Structure

### Full structure

```text
src/component/cmp_NNNN_name/
├── manifest.json
├── schema.json
├── custom.json
├── requirements.txt
├── requirements-dev.txt
├── __init__.py
├── README.md
├── .specify/
│   ├── spec.md
│   └── data-model.md
├── route/
│   ├── __init__.py
│   ├── routes.py
│   ├── schema.json
│   └── *_handler.py
├── neutral/
│   ├── component-init.ntpl
│   ├── snippets.ntpl
│   ├── obj/
│   │   └── object.json
│   └── route/
│       ├── index-snippets.ntpl
│       ├── form-snippets.ntpl
│       ├── locale-en.json
│       ├── locale-es.json
│       ├── data.json
│       └── root/
│           ├── data.json
│           ├── content-snippets.ntpl
│           └── subroute/
│               ├── data.json
│               ├── content-snippets.ntpl
│               └── ajax/
│                   └── content-snippets.ntpl
├── model/
│   └── *.json
├── static/
│   ├── *.css
│   ├── *.js
│   └── images/
├── src/
│   └── *.py
├── lib/
│   └── <uuid_or_namespace>/
└── tests/
    ├── conftest.py
    └── test_*.py
```

### Minimal structure

```text
src/component/cmp_NNNN_name/
├── manifest.json
├── schema.json
├── route/
│   ├── __init__.py
│   └── routes.py
└── neutral/
    └── route/
        └── root/
            ├── data.json
            └── content-snippets.ntpl
```

A support-only component may omit `route/` and `neutral/route/root/` if its
spec clearly justifies that it only provides schema, shared snippets, assets,
models, or initialization hooks.

## Identity Contract: `manifest.json`

`manifest.json` is mandatory. It defines identity, version, base route, and
security policy.

### Required fields

| Field | Type | Contract |
|---|---|---|
| `uuid` | string | Stable identity. Lowercase, digits, and `_`. Must contain `_`. |
| `name` | string | Human-readable component name. |
| `description` | string | Short auditable purpose. |
| `version` | string | Semantic or project-compatible version. |
| `route` | string | Blueprint base route. Empty string is reserved for justified base/template components. |
| `security` | object | Declarative fail-closed security policy. |

### Optional fields

- `config`
- `repository` (reserved/planned, not an active loader contract)
- `required` (reserved/planned, not an active loader contract)
- domain-specific metadata documented by the component spec

### Security

`security` must contain:

- `routes_auth`: object mapping route prefixes to booleans;
- `routes_role`: object mapping route prefixes to non-empty role lists.

Prefix resolution uses "most specific wins".

Examples:

```json
{
  "security": {
    "routes_auth": {
      "/": false,
      "/admin": true
    },
    "routes_role": {
      "/": ["*"],
      "/admin": ["admin"]
    }
  }
}
```

Rules:

- `*` means any authenticated role set accepted by the route contract;
- `*` must not be mixed with explicit roles in the same list;
- route prefixes are relative to `<manifest.route>`.

## Configuration: `schema.json`

### General shape

Component schemas may contribute to:

- immutable `data`;
- mutable `inherit.data`;
- locale-related data;
- menus, theme metadata, or component-specific configuration.

### Menus

Menu structures belong in schema data so they remain declarative and visible to
templates without hardcoded HTML duplication.

### Dynamic schema references

Schema values may reference other schema values using the project's dynamic
reference syntax. These references must resolve after schema merge, not by
manual string duplication.

### Dynamic references in templates

Templates must read derived runtime values from schema paths instead of
hardcoding component folder names or static route strings.

### Global translations

Global component translation data should be exposed through locale JSON files in
`neutral/route/`.

## Overrides: `custom.json` and `config/config.db`

- `custom.json` is a local override file for non-secret mutable configuration;
- `config/config.db` may provide centralized enabled overrides by component
  UUID;
- secrets must still live in environment configuration, not JSON.

## Backend: Routes and Handlers

### `route/__init__.py`

Owns blueprint creation and route registration helpers.

### `route/routes.py`

Owns fine-grained Flask route declarations. Business logic should stay in
handlers, not inline route functions.

### `RequestHandler`

Use for ordinary request flows that need prepared schema data, route metadata,
session/user access, and rendering helpers.

### `FormRequestHandler`

Use for form flows that require the AJAX-first validation and token contract
defined by specification 003.

### Rate limiting and AJAX headers

Sensitive routes must apply the relevant rate limits. AJAX endpoints must be
consistent with the `Requested-With-Ajax` rendering contract.

## Frontend: `neutral/`

### Route-to-directory mapping

Route templates must map to `neutral/route/...` using `root/` for the base
route and nested directories for subroutes.

### `data.json`

Route-level `data.json` defines local NTPL data. Values defined there are read
via `local::...`. Defaults that must remain dynamically overridable by route
data should be copied into `inherit.data`.

### `content-snippets.ntpl`

Every route must define `current:template:body-main-content`. This is the
provider-facing contract that inserts route content into the active layout.

### `index-snippets.ntpl`

Component-wide per-route shared snippet loader. Common route snippets, shared
translations, and shared data belong here.

### `component-init.ntpl`

Optional global registration snippet accumulated at app startup.

### CSP

Components must remain CSP-compatible. Avoid inline JS/CSS unless required and
always include `nonce="{:;CSP_NONCE:}"` on CSP-sensitive inline tags.

## Static Assets

Component assets live in the component `static/` directory. Public publication
into `public/` or a CDN is an optimization documented by the component and
governed by specification 004.

## Per-Component Python Dependencies

If a component requires extra runtime or development dependencies, they belong
in `requirements.txt` and `requirements-dev.txt` inside that component.

## Forms

Forms must follow specification 003. In practice this means AJAX-first design,
declarative route validation in `route/schema.json`, and handler inheritance
from `FormRequestHandler`.

## Translations

Translation files belong under `neutral/route/locale-*.json`. User-visible text
in templates should be wrapped in `{:trans; ... :}`.

## Models and Persistence

Component SQL definitions belong in `model/*.json`. Components must call them
explicitly through `model.exec(..., model_dir=component_path)` and must not
embed SQL strings in Python business logic.

## Private Libraries and Helper Code

Private component-only libraries may live under `lib/` or `src/` when justified
by the component scope.

## Naming in Component Specifications

### Specific rules

- do not treat the folder name as stable identity;
- use the UUID in prose when naming the component;
- use component-relative file paths like `/schema.json` or `/route/routes.py`
  when the purpose is to describe files inside the component;
- document routes as `<manifest.route>/...`, not as hardcoded concrete routes,
  unless the exact repository state is the explicit subject.

## Per-Component SDD Specification

Each active component should have:

- `.specify/spec.md`
- `.specify/data-model.md` when persistence deserves its own contract

`plan.md` is optional and should exist only for active staged work.

## Testing

### Process

Each active component should ship tests under `tests/`.

### Stability rules

Tests must derive:

- the component UUID from `manifest.json`;
- the effective route from `manifest.json`;
- file-system paths relative to the test file or component root.

Tests must not assume the folder name is a stable identifier.

### Minimal coverage

At minimum, tests should cover:

- manifest validity;
- route registration;
- security policy expectations;
- main handler behavior;
- template rendering expectations when relevant;
- schema/model integration when relevant.

## Compatibility with Example Components

Example or disabled components may be useful references, but they are not
runtime contracts and must not override this specification.

## Universal Acceptance Criteria

- [x] every active component has a valid `manifest.json`;
- [x] UUID, not folder name, is the stable identity;
- [x] route base comes from `manifest.json`;
- [x] security is declarative and fail-closed;
- [x] templates follow the route content contract;
- [x] forms follow the shared form standard;
- [x] tests and docs avoid depending on unstable folder names.

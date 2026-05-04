# Specification 000 - Core System: Neutral Starter Py

## Summary

Neutral Starter Py is a base platform for Progressive Web Applications built on
Flask for the backend and Neutral TS for presentation. The core is not a
business application. It is the runtime responsible for:

- discovering and loading active components;
- composing the effective global schema;
- preparing request context before component code runs;
- enforcing cross-cutting security controls;
- rendering Neutral TS templates;
- exposing declarative persistence through JSON SQL models.

Real features belong in components. The core exists so those components can be
installed, replaced, overridden, tested, and executed deterministically without
rewriting the shared runtime.

This specification must be read together with:

- `.specify/memory/constitution.md`
- `.specify/OVERVIEW.md`
- `.specify/specs/001-component-standard/spec.md`
- `.specify/specs/004-static-assets-delivery/spec.md`
- `docs/component.md`
- `docs/component-security.md`
- `docs/development.md`
- `docs/dispatcher.md`
- `docs/model.md`
- `docs/security-csp.md`
- `docs/session.md`
- `docs/session_dev.md`
- `.agents/skills/manage-component/SKILL.md`

## Goals

- provide a stable Flask application factory and extensible blueprint runtime;
- load active components automatically, deterministically, and with validation;
- maintain a composed effective schema from core defaults, components, and
  overrides;
- prepare a complete request context before any component handler executes;
- enforce fail-closed security for host validation, proxy handling, CSP,
  sessions, route policies, roles, and user states;
- keep data access decoupled from Python business logic through declarative SQL
  models in JSON;
- provide a clear structure for specs, tests, and local AI skills.

## Non-goals

- no business features belong directly in the core;
- no component internals are defined here when covered by specification 001;
- no detailed NTPL syntax belongs here when covered by specification 002;
- no detailed AJAX-form flow belongs here when covered by specification 003;
- disabled example components do not define runtime contracts.

## Normative Principles

### Component-first

New routes, pages, feature models, and feature assets must live in
`src/component/`. Core changes are justified only when they affect shared
runtime behavior, base configuration, security, request preparation, shared
rendering, or shared persistence.

### Spec-first

Expected behavior must be documented in `.specify/` before implementation. Core
changes must update this specification first. `plan.md` is optional and should
exist only when staged work, migration sequencing, or explicit follow-up is
required.

### Tests as contract protection

Core changes must be covered by tests against observable contracts: startup,
hook order, fail-closed denial, configuration merge, route resolution,
rendering, and persistence behavior.

### Cross-cutting security

Security is a runtime concern, not a per-route afterthought. If policy,
component resolution, host validation, or user role checks fail, the request
must be denied.

### Simplicity

Use Flask, SQLAlchemy, and Neutral TS directly unless an additional abstraction
clearly improves an explicit local contract.

## High-Level Architecture

| Layer | Responsibility |
|---|---|
| Configuration | Read `config/.env`, build `Config`, resolve internal paths, databases, CSP, limits, and security settings. |
| Flask factory | Create the app, initialize extensions, install middleware, register hooks, and load components. |
| Middleware and hooks | Validate host, normalize trusted proxy data, prepare `g.pr`, and add security headers. |
| Component loader | Discover active components, validate manifests, apply overrides, compose schema, execute hooks, and register blueprints. |
| Runtime schema | Clone the composed schema per request and inject HTTP context, locale, theme, route, user, and token data. |
| Route security | Resolve `routes_auth` and `routes_role` with "most specific wins" semantics. |
| Handlers | Provide `RequestHandler` and `FormRequestHandler` as the public adapter layer for components. |
| Rendering | Delegate page, error, and AJAX fragment rendering to Neutral TS. |
| Persistence | Execute declarative JSON SQL operations through configured SQLAlchemy engines. |
| Public assets | Delegate static delivery to `public/`, the HTTP server, or a CDN according to specification 004. |

## Startup Contract

### Application factory

The application must be created through a factory that:

1. creates the Flask app;
2. loads `Config`;
3. determines debug mode through explicit guard conditions;
4. disables `strict_slashes`;
5. initializes cache and rate limiting;
6. bootstraps databases if `AUTO_BOOTSTRAP_DB=true`;
7. applies `ProxyFix`;
8. installs forwarded-header safeguards for untrusted proxies;
9. refuses startup if `SECRET_KEY` is missing;
10. registers `before_request` hooks in a safe order;
11. ensures host validation runs before request context preparation;
12. registers security headers in `after_request`;
13. registers required URL converters;
14. loads components;
15. serializes the effective schema for cheap per-request cloning.

### Debug mode

Debug mode must be gated. Enabling `FLASK_DEBUG` alone is not sufficient.
Typical conditions include:

- `FLASK_DEBUG=true`;
- `DEBUG_FILE` exists;
- `DEBUG_EXPIRE > 0`;
- `DEBUG_FILE` mtime is still inside the allowed window;
- in WSGI entries, `WSGI_DEBUG_ALLOWED=true` acts as an additional gate.

If any condition fails, debug must stay disabled.

### Database bootstrap

When `AUTO_BOOTSTRAP_DB=true`, the core must initialize shared structures for:

- the PWA database: distributed UIDs, users, profiles, emails, PINs, disabled
  states, and RBAC;
- the Safe database: normal user sessions;
- the Image database: image storage, when the image subsystem is installed.

Bootstrap must fail explicitly if any declarative setup operation fails.

## Component Loader Contract

The loader owns activation, validation, overrides, and registration. Component
internals are defined by specification 001.

### Discovery

- inspect `src/component/`;
- only directories starting with `cmp_` are active;
- `_cmp_*` and any non-`cmp_` directory are ignored completely;
- an active component without a valid `manifest.json` must block startup;
- base discovery order is alphabetical.

### Manifest validation

Every active component must declare:

- `uuid`
- `name`
- `description`
- `version`
- `route`
- `security`

UUID rules:

- string type;
- project-defined min/max length;
- must contain `_`;
- only lowercase ASCII, digits, and `_`.

Security rules:

- `routes_auth` is a non-empty object mapping route prefixes to booleans;
- `routes_role` is a non-empty object mapping route prefixes to non-empty lists
  of strings;
- `*` must not be mixed with explicit role codes in the same list.

### Component override order

The effective component contract is composed in this order:

1. versioned `manifest.json`;
2. local `custom.json`, if present;
3. `config/config.db` `custom` table entry for the component UUID, if enabled;
4. versioned `schema.json`, if present;
5. schema overrides derived from `custom.json` and configuration DB state.

### Schema composition

The loader must:

- register the component both by UUID and by folder metadata in the global
  schema;
- merge component schema into the global runtime schema;
- resolve dynamic schema references such as `[:;...:]` after merging;
- preserve component-local isolation while exposing runtime data in predictable
  branches.

### Component hooks

If present, the loader must execute:

- `init_component(component, component_schema, _schema)`
- `init_blueprint(component, component_schema, _schema)`

`init_component` may mutate the component schema or register provider roles such
as the active layout or mail-template provider. `init_blueprint` owns blueprint
construction, not business logic.

### Blueprint order

Blueprint registration must remain deterministic. Components whose folder names
begin with `cmp_9` are late fallbacks and must be registered after ordinary
feature components.

## Request Contract

### Mandatory order

Each request must follow this broad order:

1. validate host and proxy assumptions;
2. prepare request context and clone runtime schema;
3. load session and user runtime data;
4. resolve the active component and route security policy;
5. execute the component handler;
6. render or return the response;
7. append security headers.

### Host and proxies

Host validation must run before the application trusts request-derived routing
or context. Forwarded headers may only be accepted when the deployment is
configured to trust the proxy chain.

### `PreparedRequest`

`PreparedRequest` is the per-request core data assembler. It is responsible for
injecting:

- `CONTEXT` (GET, POST, cookies, headers, environment, session);
- current locale and theme data;
- route-relative template paths;
- CSP nonce and other security-related runtime variables;
- request-derived information used by handlers and NTPL rendering.

### Request schema

The runtime must work on a per-request schema clone derived from the serialized
global schema, then enriched with request-local values such as user state,
route metadata, tokens, AJAX headers, and current template paths.

### AJAX

The runtime must support fragment rendering by detecting the
`Requested-With-Ajax` header and allowing the active layout provider to return
only the required content fragment.

### Public handler API for components

Components must interact with the core through:

- `RequestHandler` for general request flows;
- `FormRequestHandler` for form flows.

The core must not require components to bypass these abstractions to access
schema, route context, session state, or tokens.

## Route Security Contract

### Policy resolution

The route policy for `routes_auth` and `routes_role` must be resolved by
prefix, with the most specific matching prefix winning.

### Evaluation

If a route requires authentication, unauthenticated users must be denied. If a
route requires roles, authenticated users lacking the required roles must also
be denied. Missing or malformed policy data must default to denial.

### Roles

Role checks must rely on runtime user data derived from the user subsystem and
must support both user-level and profile-level role information when the route
contract requires it.

## Sessions, User, and Tokens

### Normal session

The standard user session is persisted in the Safe database and exposed through
cookies configured as `HttpOnly`, `Secure`, and `SameSite=Lax` unless the
deployment explicitly justifies another policy.

### Runtime user

Authenticated requests must expose a normalized runtime user object containing
authentication state, user identifiers, profile data, roles, and disabled
states.

### `SessionDev`

Development admin access is a separate mechanism using environment-managed
credentials, signed cookies, IP allowlisting, and in-memory failed-attempt
tracking. It does not replace the normal user/session system.

### Tokens

The core must provide the token primitives required by the form system,
including LTOKEN, CSRF-related state, FTOKEN support, and any session-backed
token validation required by specification 003.

## Security Headers and CSP

The core must:

- generate a per-request CSP nonce;
- expose that nonce to templates as `CSP_NONCE`;
- append CSP and related security headers after request processing;
- forbid template patterns that bypass CSP without explicit and documented
  justification.

## Neutral TS Rendering

The core must resolve:

- the active layout provider directory;
- the current component-relative route path;
- the full-page or AJAX rendering entry point;
- the error rendering entry point.

The exact NTPL file contracts belong to specification 002 and its
`provider-spec.md`.

## Configuration

### Sources

Effective runtime configuration is composed from:

- environment variables and `.env`;
- versioned component manifests and schemas;
- local `custom.json` overrides;
- centralized overrides in `config/config.db`.

### Configurable areas

Typical areas include:

- databases and storage;
- security and CSP;
- static delivery and CDN prefixes;
- mail and template provider selection;
- locale and theme defaults;
- debug and bootstrap guards.

### Internal paths

Paths must remain configurable through `Config` and must not be hardcoded
inside features when a runtime-derived or manifest-derived path already exists.

## Persistence

Shared persistence contracts belong to `core.model.Model` and the JSON SQL
definition system. The core may expose shared models such as `app.json`,
`session.json`, and `user.json`, while components may provide isolated model
directories.

## Rate Limiting and Cache

The core initializes rate limiting and cache extensions, but usage policies are
defined by shared and component-specific specs. Sensitive routes must opt into
the relevant limits and cache invalidation flows where required.

## Static Assets

Static delivery must follow specification 004. The application server is not
the preferred delivery path for public static assets in production.

## AI Agents and Skills

The repository is designed so local skills and SDD documentation guide changes.
`AGENTS.md` points to `.specify/OVERVIEW.md` as the entry point. Specs should
be treated as normative in their applicable scope.

## Observability and Errors

The core must expose explicit failures for:

- invalid component manifests;
- missing secrets such as `SECRET_KEY`;
- bootstrap errors;
- invalid host or proxy assumptions;
- malformed or missing provider contracts.

User-facing error rendering must remain stable and safe even when the normal
route rendering pipeline fails.

## Invariants

- business features belong in components, not the core;
- only `cmp_*` components are active;
- component UUID is the stable identity, not the folder name;
- route base comes from `manifest.json`, not hardcoded strings;
- request context must be prepared before component business logic runs;
- missing or malformed security policy must deny access;
- NTPL rendering depends on provider contracts, not hardcoded component names.

## Usage Scenarios

### Application startup

The runtime validates configuration, bootstraps shared data if enabled, loads
active components, composes the effective schema, and registers blueprints in a
deterministic order.

### New feature development

A new feature should usually add a component, not modify the core, unless the
change truly affects shared runtime behavior.

### Public request

The request passes host validation, context preparation, route resolution, and
policy evaluation before the target handler is allowed to run.

### Authenticated request

The runtime loads the session, builds runtime user data, resolves route policy,
and then allows the component handler to continue.

### Local admin development

`SessionDev` provides a guarded development-only access flow without depending
on the normal user database.

### Centralized override

An operator may override component configuration through `config/config.db`
without editing the component package itself.

## Global Acceptance Criteria

- [x] startup is factory-based and deterministic;
- [x] only active `cmp_*` components participate in the runtime;
- [x] manifest and schema composition remains validated and ordered;
- [x] request context is prepared before component logic;
- [x] route policies are evaluated fail-closed;
- [x] the core exposes stable handler abstractions to components;
- [x] NTPL rendering relies on provider contracts and prepared schema data;
- [x] shared persistence uses declarative JSON SQL models.

## Known Risks and Debt

- some provider and example contracts evolved after the initial codebase and
  must keep being documented retrospectively;
- bootstrap and migration flows remain intentionally explicit rather than fully
  automated;
- any future change that weakens fail-closed behavior is a core regression.

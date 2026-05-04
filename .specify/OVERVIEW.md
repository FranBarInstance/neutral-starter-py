# Neutral TS Starter Py — Specification Overview

> This document is the entry point to the project's specification system.
> Read it before navigating any spec or template.

---

## 1. Application Abstract

**Neutral TS Starter Py** is a modular, opinionated starter kit for building
**Progressive Web Applications (PWA)** with **Python (Flask)** on the backend and
**[Neutral TS](https://github.com/FranBarInstance/neutralts)** as the universal
template engine.

The fundamental unit of extension is the **component**: a self-contained capsule
that encapsulates routes, NTPL templates, static assets, configuration
(`schema`), data models, and tests. The base application is an empty platform;
all real functionality lives in its components.

### Defining Traits

- **Plug-and-play architecture.** Components are loaded automatically by
  alphabetical prefix order (`cmp_NNNN_`). Adding or removing a component does
  not require changing the core.
- **Strict modularity.** Each component has its own manifest, schema, routes,
  templates, and tests. Isolation is the norm; cross-component dependencies are
  the documented exception.
- **Layered configuration.** A component's base contract lives in
  `manifest.json` and `schema.json`, but it may receive local overrides through
  `custom.json` or centralized overrides through `config/config.db`; specs must
  not assume that the effective route always matches the versioned manifest.
- **AI-agent-oriented design.** The structure is explicit, patterns are
  documented in skills (`.agents/skills/`), and specifications are verifiable
  contracts rather than informal documentation. Agents can create full
  components by following the skills instead of inferring conventions.
- **Security by default.** Strict CSP, host validation, form tokens, role-based
  access control, and fail-closed behavior are system invariants, not options.
- **TDD as contract.** No implementation starts without failing tests first.

---

## 2. How These Specifications Work

This project follows **Spec-Driven Development (SDD)**: the specification is
the source of truth. Code serves the spec; if code changes without the spec
changing first, something went wrong.

### Documents in the Spec System

| Document | Purpose |
|---|---|
| `.specify/OVERVIEW.md` | **This file.** Entry point to the spec system. |
| `.specify/memory/constitution.md` | Immutable principles governing the entire project. It prevails over any other source. |
| `.specify/specs/README.md` | SDD methodology: how to create, update, and use specs. |
| `.specify/templates/README.md` | Guide to choosing the correct template (`component` / `feature` / `system`). |

### Document Types Inside Each Spec

| File | Purpose |
|---|---|
| `spec.md` | **What** is built and **why**: contracts, boundaries, acceptance criteria. |
| `plan.md` | **How** it is built: implementation sequence, red-phase tests, evidence. It only exists when there is open or planned work. |
| `data-model.md` | Schemas and persistence. It only exists when the spec introduces or changes data. |

### Where Each Spec Lives

```text
.specify/specs/NNN-name/                    <- System and cross-component feature specs
src/component/<component-folder>/.specify/ <- Per-component spec
```

### Identity Rules

- Components are identified by their **UUID** in `manifest.json`, not by the
  `cmp_*` folder name.
- Component base routes are expressed as `<manifest.route>` in documentation.
- Absolute system paths must not be used in any spec or plan.

---

## 3. Specification Index

### 3.1 Global System Specifications

| Spec | Description |
|---|---|
| [000 — Core System](specs/000-core-system/spec.md) | Base architecture, cross-cutting security, component loading, and framework contracts. |
| [001 — Component Standard](specs/001-component-standard/spec.md) | Structure, conventions, manifests, schemas, and component lifecycle. |
| [002 — NTPL Template Standard](specs/002-neutral-templates-standard/spec.md) | Syntax, snippets, route data, and Neutral TS template patterns. |
| [003 — Forms Standard](specs/003-forms-standard/spec.md) | AJAX-first forms, tokens, validation, and modal flows. |

### 3.2 Extended Global Index

Use this section as the practical navigation map. Read only the specs needed for
the current task.

| Area | Read First | Read Also | Use When |
|---|---|---|---|
| Core runtime | [000 — Core System](specs/000-core-system/spec.md) | [000 — Core Data Model](specs/000-core-system/data-model.md) | Working on app bootstrap, request lifecycle, security pipeline, schema composition, or shared runtime behavior. |
| Component architecture | [001 — Component Standard](specs/001-component-standard/spec.md) | [001 — Component Data Model](specs/001-component-standard/data-model.md) | Creating, restructuring, documenting, testing, enabling, or disabling components. |
| Neutral TS templates | [002 — NTPL Template Standard](specs/002-neutral-templates-standard/spec.md) | [002 — Layout Provider Contract](specs/002-neutral-templates-standard/provider-spec.md) | Editing `.ntpl`, route `data.json`, snippets, layout integration, AJAX rendering, or template contracts. |
| Forms | [003 — Forms Standard](specs/003-forms-standard/spec.md) | — | Building or modifying forms, validation, modal forms, tokens, and AJAX-first form flows. |
| Static assets | [004 — Static Assets Delivery](specs/004-static-assets-delivery/spec.md) | — | Working on `public/`, component `static/`, CDN/server delivery, or CSP-sensitive asset loading. |
| Images and files | [005 — Image System](specs/005-image-system/spec.md) | — | Working on uploaded images, albums, variants, visibility, or file lifecycle. |
| Users, auth, roles | [006 — User and RBAC](specs/006-user-and-rbac/spec.md) | — | Working on users, profiles, auth flows, roles, disabled states, or account security. |
| Persistence | [007 — Data Modeling](specs/007-data-modeling/spec.md) | [000 — Core Data Model](specs/000-core-system/data-model.md) | Working on JSON models, SQL contracts, transactions, or component persistence. |
| Rate limiting and devices | [008 — Rate Limiting and Devices](specs/008-rate-limiting-and-devices/spec.md) | — | Working on brute-force protection, `SessionDev`, limiter rules, or device-related controls. |
| Internationalization | [009 — i18n Standard](specs/009-i18n-standard/spec.md) | — | Working on `{:trans; :}`, locale files, translation extraction, or language negotiation. |
| Mail | [010 — Mail System](specs/010-mail-system/spec.md) | [010 — Mail Template Provider Contract](specs/010-mail-system/provider-spec.md) | Working on email sending, transport, template providers, or mail rendering. |
| Component configuration | [011 — Component Configuration](specs/011-component-configuration/spec.md) | — | Working on config boundaries, secrets, manifest config, inherit rules, or overrides. |
| SDD methodology | [Specs README](specs/README.md) | [Templates README](templates/README.md) | Working on the spec system itself, authoring new specs, or reviewing spec quality. |

### 3.3 Component Specifications

Each active component has its documentation in
`<component-folder>/.specify/`. The stable identity of each component is its
**UUID** in `manifest.json`.

The minimum required file is `spec.md`. Components with open or planned
implementation work add `plan.md`. Components that introduce or change
persistence add `data-model.md`. More complex components may require additional
files depending on their domain, for example `security.md`, `api.md`, or
`integration.md`.

To navigate a component spec, go directly to the component directory under
`src/component/` and open its `.specify/` folder.

### 3.4 Recommended Reading Paths

For common tasks, start here:

- New or modified component:
  Read `001-component-standard/spec.md`, then the relevant component spec under `src/component/.../.specify/`, then any supporting area spec such as templates, forms, or persistence.
- Template or snippet work:
  Read `002-neutral-templates-standard/spec.md`, then `002-neutral-templates-standard/provider-spec.md` if the work touches the base layout contract.
- Forms or AJAX form flows:
  Read `003-forms-standard/spec.md`, then the relevant component spec.
- Security-sensitive work:
  Start with `000-core-system/spec.md`, then read the task-specific area spec such as `006-user-and-rbac/spec.md`, `008-rate-limiting-and-devices/spec.md`, or `010-mail-system/spec.md`.
- Documentation or spec authoring:
  Read `specs/README.md`, then `templates/README.md`, then the specific system or component spec you are editing.

### 3.5 Example Components (Disabled)

Components prefixed with `_cmp_*` are reference examples.
They do not have their own active spec; they are documented as patterns in the
skills under `.agents/skills/`.

---

*Current constitution: v1.1.1 — Ratified 2026-04-30*  
*This document should be updated when new global specs or active components are added.*

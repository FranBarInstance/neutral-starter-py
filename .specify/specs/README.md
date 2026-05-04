# SDD Methodology Specification

## Executive Summary

This document defines the **Spec-Driven Development (SDD)** methodology that
governs development in Neutral Starter Py. In SDD, the **specification is the
source of truth**: code serves the spec, not the other way around. If code must
change, the specification must change first.

This specification is **normative**. Every developer and AI agent must follow
it when creating, updating, and using specifications in the project.

## Normative References

- `.specify/memory/constitution.md` — Immutable project principles.
- `.specify/OVERVIEW.md` — Specification system overview and navigation entry point.
- `.specify/templates/README.md` — Guide for choosing and using specification templates.

---

## 1. Core Principles of SDD

### 1.1 The Specification Is the Source of Truth

- Code implements the specification; it does not replace it.
- If code contradicts the spec, code is wrong.
- If reality changes, update the spec first, then the code.
- A feature without a specification does **not exist** as a project contract.

### 1.2 Specification Before Implementation

No implementation code is written before:

1. There is an approved specification covering the scope.
2. There are failing tests (Red phase of TDD).
3. The user has validated the design.

### 1.3 Specs as Verifiable Contracts

A specification is not informal documentation. It is a **contract** defining:

- **What** is built and **why**
- Explicit boundaries: what is out of scope
- Technical contracts: interfaces, data schemas, APIs, routes
- Verifiable acceptance criteria
- Testing strategy with concrete cases
- Documented impact and risks

---

## 2. Structure of the Specification System

### 2.1 Locations and Types

```text
.specify/
├── memory/
│   └── constitution.md
├── OVERVIEW.md
├── templates/
│   ├── README.md
│   ├── system/
│   ├── feature/
│   └── component/
└── specs/
    ├── README.md
    ├── 000-core-system/
    ├── 001-component-standard/
    ├── 002-neutral-templates-standard/
    ├── 003-forms-standard/
    └── ...
```

### 2.2 Specification Types

| Type | Location | Use | Examples |
|---|---|---|---|
| **System** | `.specify/specs/NNN-name/` | Cross-cutting framework contracts | Core, Component Standard, Templates, Forms |
| **Feature** | `.specify/specs/NNN-name/` | Functionality spanning multiple components | OAuth authentication, external API integration |
| **Component** | `src/component/<component-folder>/.specify/` | Contract of a specific component | Album, Sign, User |

### 2.3 Documents Inside a Spec

| File | Purpose | Requirement |
|---|---|---|
| `spec.md` | What, why, contracts, boundaries, acceptance criteria | Always |
| `plan.md` | How, implementation order, red-phase tests, evidence | When there is open work |
| `data-model.md` | Schemas, persistence, migrations | When data is introduced or changed |
| `security.md` | Security analysis, CSP, tokens, vulnerabilities | Recommended for auth-sensitive components |
| `api.md` | External API contracts | If public API is exposed |
| `integration.md` | Dependencies on other systems | If external integrations exist |

---

## 3. SDD Workflow

### 3.1 Phase 1: Specification

1. Identify the spec type (`system`, `feature`, or `component`) using `.specify/templates/README.md`.
2. Copy the appropriate template into the correct location.
3. Fill in identity and scope:
   - component UUID from `manifest.json` if applicable
   - the problem being solved and for whom
   - explicit non-objectives
4. Define technical contracts:
   - routes and handlers
   - NTPL snippets and templates
   - static assets
   - data schemas
   - required configuration
5. Specify security:
   - CSP, tokens, host validation
   - complete `routes_auth` and `routes_role` contracts
6. Define verifiable acceptance criteria.
7. Document the testing strategy.
8. Review against the constitution.

### 3.2 Phase 2: Planning (`plan.md`)

When a change requires phased work, tracking, or separate validation evidence,
create `plan.md` with:

1. Sources of truth for review
2. Quality gates
   - security gates
   - architecture gates
   - SDD gates
3. Mandatory testing areas
4. Validation evidence to be completed during implementation

### 3.3 Phase 3: Tests First

1. Write failing unit or integration tests (Red phase).
2. Validate with the user that the tests represent the expected behavior.
3. Confirm that the tests **fail** before implementation.

### 3.4 Phase 4: Implementation

1. Write the minimum code necessary to make tests pass (Green phase).
2. Refactor while preserving the contracts in the spec (Blue phase).
3. Do not modify the spec during implementation without documented justification.

### 3.5 Phase 5: Validation and Closeout

1. Run all relevant tests; they must pass.
2. If `plan.md` exists, update it with validation evidence.
3. Update the spec so it reflects the validated real system state.

---

## 4. Spec Quality Criteria

A specification is fit to be used as a contract when it answers these
questions:

| Question | Typical Section |
|---|---|
| What problem does it solve and for whom? | Executive Summary, Objectives |
| What is explicitly out of scope? | Non-Objectives |
| What contracts does it create or modify? | Technical Contract sections |
| What routes, handlers, snippets, assets, and data are involved? | Architecture, Structure |
| What must happen when everything works? | Acceptance Criteria, Happy Path |
| What must happen when something fails? | Error Handling, Edge Cases |
| What security controls are required? | Security |
| What tests will prove the contract? | Testing Strategy |
| What components or layers may break if it changes? | Impact, Dependencies |
| What decisions or risks are documented? | Decisions, Risks |

### 4.1 Identity Rules

- Identify components by UUID, not by folder name.
- Use `<manifest.route>` when referring to component base routes.
- Derive real routes from `manifest.json`, `route/routes.py`, and `neutral/route/root/`.
- Never use absolute system paths in specs, plans, or examples.
- Do not use `cmp_*` names as stable identity except when documenting current load order or folder pattern.

### 4.2 Security Rules

Every relevant spec must document:

- CSP when JavaScript, CSS, DOM events, templates, or client assets are involved
- tokens and validation when forms or AJAX are involved
- complete `routes_auth` and `routes_role` contracts for routed components
- rate limiting on routes that mutate state or expose sensitive data

---

## 5. Lifecycle of a Spec

### 5.1 Validity Criterion

A spec can be used as a contract when:

- it describes the real behavior or a validated target behavior
- it does not contradict code or the constitution
- its contracts are sufficiently verifiable for implementation or review

If a spec becomes outdated or inconsistent, it must be corrected before being
used again as normative guidance.

### 5.2 Versioning

- Use **dates** (`YYYY-MM-DD`) instead of semantic versions for specs.
- Record change history at the end of each `spec.md`, and in `plan.md` if it exists.
- Global system specs (`000-NNN`) and the constitution are the most stable contracts.

---

## 6. Retrospective Specifications

When documenting an already existing system or component:

1. If needed, state inside the spec that it is retrospective and still under review.
2. Extract identity from `manifest.json`.
3. Extract routes from `route/routes.py` and `neutral/route/root/`.
4. Extract configuration from `schema.json` and `route/schema.json`.
5. Extract snippets and assets from `neutral/` and `static/`.
6. Record as a risk any discovered behavior that lacks tests.

### Retrospective Validation

- Create tests for current behavior first.
- If tests pass without changes, document that behavior in the spec.
- If tests reveal inconsistencies, fix code or document the risk explicitly.

---

## 7. Integration with AI-Agent Skills

### 7.1 Skills as Imperative Guidance

- The project is optimized for collaboration with AI.
- Skills under `.agents/skills/` are imperative guidance for agents.
- Conventions must come from skills and official documentation, not guesswork.

### 7.2 Available Skills

| Skill | Use | Location |
|---|---|---|
| `manage-component` | Create/modify component structure | `.agents/skills/manage-component/SKILL.md` |
| `manage-neutral-templates` | Create/modify NTPL templates | `.agents/skills/manage-neutral-templates/SKILL.md` |
| `manage-ajax-forms` | Create/modify AJAX forms | `.agents/skills/manage-ajax-forms/SKILL.md` |
| `translate-component` | Extract/maintain translations | `.agents/skills/translate-component/SKILL.md` |

### 7.3 Source Priority

1. **Constitution** (`.specify/memory/constitution.md`)
2. **This specification** (SDD methodology)
3. **OVERVIEW.md**
4. **System specs** (`000-NNN`)
5. **Agent skills**
6. **Real code** as implementation reference, not as the contract itself

---

## 8. Anti-Patterns and Common Errors

| Symptom | Problem | Remedy |
|---|---|---|
| "It will be implemented..." without criteria | Intention, not contract | Add verifiable acceptance criteria |
| Missing Non-Objectives section | Undefined scope | Explicitly define what is out of scope |
| No testing strategy | Not verifiable | Add concrete test cases |
| Security-sensitive feature without security section | Incomplete contract | Document CSP, tokens, auth, roles, limits |
| References based on folder name instead of UUID | Unstable identity | Switch to UUID and `<manifest.route>` |

---

## 9. Glossary

| Term | Definition |
|---|---|
| **Spec** | A technical contract defining what is built and why. |
| **SDD** | Spec-Driven Development. |
| **TDD** | Test-Driven Development. |
| **Component** | The isolated, modular unit of functionality in the project. |
| **Source of truth** | The document that prevails as the contract for implementation and review. |

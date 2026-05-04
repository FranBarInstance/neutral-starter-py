# SDD Specification Templates

This directory contains the master templates used to write rigorous,
verifiable specifications. A spec must not be an informal description; it must
function as a contract between product, architecture, security, testing, and
implementation.

## Which Template to Use

### `system/`

Use for application, core, platform, or cross-cutting framework contracts.

Examples:
- component loading
- cross-cutting security
- template engine
- base data model
- agent/skill system
- local operation rules

Recommended location: `.specify/specs/NNN-system-name/`.

### `feature/`

Use for features or changes that cross multiple components, change product
behavior, or integrate multiple layers.

Examples:
- a new user flow touching authentication and profile
- a change in form policy
- an external integration
- a cross-cutting functional regression

Recommended location: `.specify/specs/NNN-feature-name/`.

### `component/`

Use inside each component to document its own contract.

Recommended location: `.specify/` inside the component.

Each active component should have at least:
- `.specify/spec.md`
- `.specify/plan.md` only when there is open or planned implementation work.

## Difference Between `spec.md` and `plan.md`

- `spec.md` defines the **what**, the **why**, the contracts, the boundaries,
  the acceptance criteria, and the expected tests.
- `plan.md` defines the **how**, the implementation sequence, the impact map,
  the red-phase tests, and the validation evidence.
- `data-model.md` should exist when a spec introduces or changes persistence.

## Mandatory Rules

- Identify components by UUID, not by folder name.
- Use `<manifest.route>` when talking about component base routes.
- Derive real routes from `manifest.json`, `route/routes.py`, and
  `neutral/route/root/`.
- Document complete `routes_auth` and `routes_role` contracts for any component
  with routes.
- Document CSP whenever there is JavaScript, CSS, DOM events, templates, or
  client assets.
- Document tokens and validation whenever there are forms or AJAX flows.
- Include verifiable acceptance criteria, not generic intentions.
- Include a testing strategy and Python commands with `.venv` activated.
- Do not use absolute system paths in specs, plans, or examples.
- Do not use `cmp_*` names as the stable identity of a component; they are only
  acceptable when documenting the current load state or the directory pattern.

## Spec Quality Checklist

A spec is considered sufficiently complete when it answers these questions:

- What problem does it solve, and for whom?
- What is explicitly out of scope?
- What contracts does it create or modify?
- What routes, handlers, snippets, assets, data, and configuration participate?
- What must happen when everything goes well?
- What must happen when something fails?
- What security controls are mandatory?
- What tests will prove that the contract is satisfied?
- What components or layers could break if it changes?
- What decisions or risks are documented?

## Recommended Flow

1. Copy the appropriate template.
2. Fill in identity, scope, and contracts before planning implementation.
3. Review security, data, and tests.
4. Create or update `plan.md` only if phased work or separate evidence is needed.
5. Write tests that fail before implementation.
6. If a plan exists, store validation evidence there.

## Retrospective Use

When documenting components or systems that already exist:

- If needed, state inside the spec itself that it is retrospective
  documentation under review until contrasted with real code.
- Extract identity from `manifest.json`.
- Extract routes from `route/routes.py` and `neutral/route/root/`.
- Extract configuration from `schema.json` and `route/schema.json`.
- Extract snippets and assets from `neutral/` and `static/`.
- Record as a risk any discovered behavior that has no tests.

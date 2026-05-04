# Neutral Starter Py Constitution

This constitution defines the immutable principles governing development in this
project. All specifications, plans, and implementations must adhere to these
articles.

## Universal Articles (SDD and Methodology)

### Article I: Component-First Priority
The fundamental unit of extension and functionality is the **component**
(`src/component/`). Every new feature, route, view, or data model must be
implemented as a self-contained, isolated component. Business logic must not be
added directly to the application core.

### Article II: Spec-Driven Development (SDD)
The specification is the only source of truth. Code serves the specification.
If code needs to change, the specification under `.specify/` must change first.
No functionality is implemented without a validated prior design.

### Article III: Test-First Development — NON-NEGOTIABLE
All development must follow a strict TDD process. No implementation code may be
written before:
1. Unit tests have been written.
2. The user has validated and approved the tests.
3. The tests have been confirmed to FAIL (Red phase).

### Article IV: Integration and Behavioral Testing
Integration tests take priority in critical areas: new component contracts,
core changes, inter-component communication, and shared models. Tests must be
resolved dynamically from the component manifest and must not depend on the
folder name on disk.

### Article V: Simplicity (YAGNI) and Anti-Abstraction
Start from the simplest possible implementation. Future-proofing and "just in
case" development are not allowed. Prefer using Flask and Neutral TS directly
instead of introducing unnecessary abstraction layers or wrappers.

### Article VI: Realistic Environments and Integration
Tests should use realistic environments whenever possible. Real in-memory
databases (SQLite) are preferred over mocks, and real template rendering is
preferred over abstract assertions on stubs.

## Platform-Specific Articles

### Article VII: Strict Isolation and Modularity
Each component must maintain its own manifest, schema, routes, templates, and
static assets. Isolation is the norm; cross-component dependencies are the
documented exception and require justification in the spec.

### Article VIII: Security by Default (Fail Closed)
Security is a non-negotiable cross-cutting responsibility. Every component must
declare its security policy in `manifest.json`. The base system guarantees CSP
validation, form tokens, host validation, and trusted proxy handling. Every
component operates under a fail-closed principle.

### Article IX: AI-Agent-Oriented Development
The project is optimized for collaboration with AI. The architecture is
explicit and predictable. Skills under `.agents/skills/` are the imperative
guide for AI agents; conventions must be taken from skills and official
documentation, not inferred heuristically.

### Article X: Request Context Invariants
The system must guarantee in code that critical controls and the request
context are prepared before component logic executes. Access control through
the centralized global schema cannot be bypassed.

### Article XI: Component Lifecycle and Ordering
Components are discovered and loaded strictly by their prefix (`cmp_NNNN_`).
Orchestration, resource override precedence, asset loading, and route priority
are governed by this deterministic lifecycle.

### Article XII: Stable Identity and Portable Documentation
The stable identity of a component is its UUID in `manifest.json`, not its
folder or effective base route. Specs, tests, and documentation must avoid
absolute system paths, folder names as functional identity, and manually fixed
routes when they can be derived from the manifest.

## Governance

This constitution prevails over any other development practice. Changes to the
constitution require technical justification, review, and corresponding updates
across the linked documentation ecosystem.

**Version**: 1.1.1 | **Ratified**: 2026-04-30

# PreparedRequest Core Bootstrap Refactor

## Objective
Define a single, mandatory core bootstrap object for every HTTP request.

`PreparedRequest` is not only a security helper. It is the request-level core orchestrator that initializes shared framework capabilities before component logic runs.

It must be clear that absolutely no route executes without `PreparedRequest` granting permission, without exceptions. This is the ultimate goal of this refactor.

## Core Design Decision
`PreparedRequest` is the first and mandatory step of request processing.

- It runs in the first global `app.before_request`.
- It builds and centralizes core context for the request.
- Component routes and dispatchers consume `g.pr` and do not rebuild core context.
- Access control is enforced by core before route logic runs.

## Naming Convention (Dispatcher replacement)
`Dispatcher` naming is replaced by `RequestHandler` naming.

### Base rename
- `Dispatcher` -> `RequestHandler`

### Specialized rename rule
Use `Domain + RequestHandler` (not `RequestHandler + Domain`).

Examples:
- `DispatcherFormSign` -> `SignRequestHandler`
- `DispatcherAdmin` -> `AdminRequestHandler`

Rationale:
1. Domain-first naming is more natural and readable.
2. Class lists group by functional prefix (`Admin`, `Sign`, `Profile`), improving navigation.
3. Consistent with common Python naming style for role-based classes.

## Framework Stance (Opinionated, Final)
1. No migration mode (framework in development stage).
2. Strong framework coupling is intentional.
3. Core checks are centralized and mandatory.
4. Components should focus on their own behavior, not core plumbing.
5. Fail closed by default.
6. Current redesign scope is limited to `cmp_5100_home` and `cmp_5150_testing`.

## PreparedRequest Mission
`PreparedRequest` handles all declared core functionalities for one request.

### Core bootstrap responsibilities
1. Initialize core objects (`Schema`, `Session`, `User`, `Template/View`, tokens).
2. Build shared request data (`schema_data`, `schema_local_data`, `CURRENT_USER`).
3. Resolve route metadata (component, normalized path, policy).
4. Execute core policies (authentication, status restrictions, role access).
5. Expose final request context + access decision for downstream execution.

### Security is one stage, not the whole class
Security is a mandatory stage inside `PreparedRequest`, together with other core bootstrap tasks.

## Class Contract
File:
- `src/core/prepared_request.py`

Suggested minimal shape:

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class PreparedRequest:
    req: Any

    # initialized by build()
    schema: Any | None = None
    session: Any | None = None
    user: Any | None = None
    view: Any | None = None
    schema_data: dict | None = None
    schema_local_data: dict | None = None
    ajax_request: bool = False

    # routing/policy
    route_path: str = "/"
    policy: dict | None = None
    allowed_roles: list[str] | None = None

    # access decision
    allowed: bool = False
    deny_status: int | None = None
    deny_reason: str | None = None

    def build(self, component_bp=None, route="") -> "PreparedRequest":
        # stage 1: core bootstrap
        # stage 2: current user + context materialization
        # stage 3: route/policy resolution
        # stage 4: core policy evaluation
        return self
```

If access is not allowed, it renders with a generic 401 directly.


## `flask.g` Contract
Use short request-scope naming:

- `g.pr`

`g.pr` is the only canonical request bootstrap object used by component handlers and dispatchers.

## Access Permission Ownership (Core-only)
Access permissions are a core responsibility, not a component responsibility.

1. `PreparedRequest` evaluates `security` policy in core (`auth`, status restrictions, roles).
2. If policy check fails, core returns generic `401` immediately from global `before_request` (temporary design stage behavior).
3. Request execution stops there; component route logic is not executed.
4. `RequestHandler` must not decide access control and must not implement fallback permission checks.

## Mandatory Execution Order
In request processing order:
1. Host validation guard runs first (`reject_disallowed_host`).
2. `PreparedRequest` runs next (`prepare_request_context`).
3. Component route logic runs only if access is allowed.

If this order is not guaranteed, app startup must fail.

## Component Manifest Contract (route auth + roles)
Manifest defines authentication and role access by route.

Routes inherit from the path; to allow everything, using `"/": true` or `"/": ["*"]` is sufficient.

```json
{
  "security": {
    "routes_auth": {
      "/": true,
      "/public": false
    },
    "routes_role": {
      "/": ["*"],
      "/user": ["admin", "dev", "moderator"],
      "/profile": ["admin", "dev"],
      "/profile/any": ["admin", "dev"],
      "/post": ["admin"]
    }
  }
}
```

### Semantics
1. Keys are absolute component-relative paths.
2. `routes_auth` controls whether session-authenticated user is required for each route prefix.
3. `routes_role` controls role access for each route prefix.
4. `*` means role wildcard (any role).
5. Role list uses OR semantics.
6. Prefix matching is used (not exact only): `/x` applies to `/x` and `/x/...`.
7. Most specific prefix wins.
8. Missing role route key -> deny.
9. Missing `security` or `routes_role` -> deny.
10. Missing auth route key -> deny.
11. `require_auth` is invalid in the new design and must not be used.

## Authentication vs Authorization
Two separated core checks:
1. Authentication group (`routes_auth`): has session started.
2. Role group (`routes_role`): role access per route.

Mandatory evaluation order in `PreparedRequest`:
1. `routes_auth`
2. status restrictions (core)
3. `routes_role`

## Path Resolution Rules
Before route lookup:
1. Empty path -> `/`
2. Ensure leading slash.
3. Remove trailing slash except root.
4. Prefix policy matching (segment-aware).

Examples:
- `""` -> `/`
- `/profile/` -> `/profile`
- `/profile/any` -> `/profile/any`
- Policy key `/profile` matches `/profile` and `/profile/any`.

## Blueprint Usage Pattern

```python
from flask import g

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET", "POST"])
def index(route):
    # If security fails, core already rendered generic 401 in before_request.
    dispatch = RequestHandler(g.pr, route, bp.neutral_route)
    return dispatch.render_route()
```

## Performance and Caching (Core-owned)
Performance optimizations are framework responsibility:
1. Cache route-role policy by normalized path.
2. Cache parsed/validated manifest security blocks at startup.
3. Reuse request-scoped context via `g.pr`.
4. Add short-lived role/status cache by session with explicit invalidation.

## Validation Rules (Mandatory)
At startup/registration:
1. `security.routes_role` exists and is dict.
2. `security.routes_auth` exists and is dict.
3. Route keys are normalized absolute paths.
4. Role lists are non-empty string arrays.
5. `*` is not mixed with explicit roles in same entry.
6. Any validation error fails app startup.

## Observability (Mandatory)
1. Structured deny logs with normalized route, component id, deny reason.
2. Metrics counters:
   - denied by auth
   - denied by user/profile status
   - denied by role
   - denied by missing/invalid policy
3. Debug trace for route normalization/policy resolution.

## Refactor Plan

### Phase 1
1. Add `src/core/prepared_request.py`.
2. Implement full core bootstrap pipeline.
3. Register first global `before_request` to set `g.pr`.

### Phase 2
1. Refactor `Dispatcher` to consume `g.pr`.
2. Migrate component routes to standard pattern.
3. Remove duplicated core/bootstrap logic from dispatchers.

### Phase 3
1. Enforce strict startup validation and fail-closed runtime behavior.
2. Add comprehensive core security integration tests.

## Testing Strategy

### Unit tests
1. Core bootstrap fields initialized correctly.
2. Path normalization and policy resolution.
3. Auth/status/role decision flow.
4. Deny behavior for missing security mapping.

### Integration tests
1. Deny occurs before component logic on failed checks.
2. Allowed requests reach dispatcher logic.
3. Startup fails for invalid/missing `routes_role` contract.

## Acceptance Criteria
1. Every component request goes through `PreparedRequest` first.
2. Components cannot bypass core auth/status/role checks.
3. Dispatcher receives prepared context and does not rebuild core bootstrap.
4. Missing policy mapping denies access by default.

## Work Completed So Far

**IMPORTANT**: At this point there are NO tests. Existing tests are neither executed nor verified because they will fail. Once the new design is implemented, the corresponding tests will be performed.

1. `PreparedRequest` was introduced as the mandatory core object per request and exposed as `g.pr`.
2. `PreparedRequest` now fully replaces `Dispatcher` functionality:
   - Initializes Schema, Session, User, Template (same as Dispatcher)
   - Sets up component context using blueprint directly (not path parsing)
   - Merges blueprint schema (fail closed - errors propagate)
   - Builds CURRENT_USER with roles/status (bug fixed: db_roles `is not None` check)
   - Handles UTOKEN/LTOKEN and cookies
3. `RequestHandler` simplified to thin adapter - does NOT re-evaluate security policies.
4. Security evaluation centralized in core using `security.routes_auth` and `security.routes_role`.
5. Policy resolution uses route-prefix matching (most specific wins).
6. Fail closed: No bypass for non-component requests - denied with `missing_component_policy`.
7. `require_auth` compatibility removed; invalid in new contract.
8. Design stage: deny responses return generic `401`.
9. `before_request` order: Host validation → PreparedRequest → component route.
10. Components adapted: `cmp_5100_home`, `cmp_5150_testing`, `cmp_9100_catch_all`.

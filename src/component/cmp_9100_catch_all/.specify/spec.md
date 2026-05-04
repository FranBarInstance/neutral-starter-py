# Component: catch_all_0yt2sa

> **Note**: The UUID is the stable component identifier. The folder name
> (`cmp_9100_catch_all`) is dynamic and may change; never use it as the functional
> reference in specs, tests, or documentation.

## Executive Summary

This component provides fallback routing for the application. It serves static
files from the `public/` directory when they exist, and renders a 404 error page
for all other unmatched routes. It acts as the lowest-priority catch-all,
loaded last by its `cmp_9xxx` prefix.

## Identity

- **UUID**: `catch_all_0yt2sa` — Stable identifier, never changes.
- **Version**: `0.0.0`
- **Base Route**: `<manifest.route>` (empty string `""`, registered at root level)
- **Status**: Active
- **Current Folder** (reference only): `cmp_9100_catch_all` — subject to change, do not use as identity in specs

## Normative References

- `.specify/memory/constitution.md` — Immutable principles.
- `.specify/specs/000-core-system/spec.md` — Core system and request handling.
- `.specify/specs/001-component-standard/spec.md` — Component structure and conventions.
- `.specify/specs/004-static-assets-delivery/spec.md` — Static asset delivery.

---

## 1. Objectives and Scope

### 1.1 Component Responsibility

This component acts as the application's route fallback layer. It intercepts
requests that no other component has matched and either serves a static file
from the configured static folder or renders a 404 error page.

### 1.2 Objectives

- Serve existing static files from `Config.STATIC_FOLDER` with proper cache headers.
- Return a rendered 404 error page for any unmatched route.
- Apply rate limiting to prevent abuse of the catch-all endpoint.
- Load last in component order (`cmp_9xxx`) so all other components take priority.

### 1.3 Non-Objectives (Explicit Boundaries)

- Does not handle authentication or authorization (all routes are public).
- Does not serve dynamic content — only static files and 404 pages.
- Does not implement its own template rendering; delegates to `RequestHandler`
  and the `http_errors` component's 404 handler.
- Does not manage file uploads or mutations — read-only static serving.

---

## 2. Architecture

### 2.1 Directory Structure

```text
src/component/cmp_9100_catch_all/
├── manifest.json                         # Identity and metadata (required)
├── .specify/
│   └── spec.md                           # Component SDD contract
└── route/
    ├── __init__.py                       # Blueprint init
    └── routes.py                         # Flask route definitions
```

This is a minimal component: no `schema.json`, no templates, no static assets,
no models, no tests. It only provides fallback routes.

### 2.2 Component Diagram

```text
[Browser Request]
    ↓
[No other component matched]
    ↓
[catch_all Blueprint: root-level routes]
    ↓
[Route 1: /<anyext:asset_path>]
    ├── File exists in STATIC_FOLDER? → send_from_directory() + Cache-Control
    └── Not found? → RequestHandler → 404 error page
    ↓
[Route 2: /<path:_path_value>]
    └── Always → RequestHandler → 404 error page
```

### 2.3 Dependencies

| Type | Dependency | UUID | Notes |
|------|-------------|------|-------|
| Requires | `Config.STATIC_FOLDER` | — | Path to public static files |
| Requires | `Config.STATIC_LIMITS` | — | Rate limit for static file serving |
| Requires | `Config.STATIC_CACHE_CONTROL` | — | Cache-Control header value |
| Requires | `RequestHandler` | — | Core request handler for 404 rendering |
| Requires | `http_errors` component | `http_errors_0yt2sa` | Provides the 404 error page rendering |

---

## 3. Routes and Handlers

### 3.1 Route Table

| Route | Method | Handler | Auth | Role | Description |
|-------|--------|---------|------|------|-------------|
| `/<anyext:asset_path>` | GET | `serve_static_file` | No | `*` | Serve static files from `public/` |
| `/` (and all subpaths) | GET | `serve_dynamic_content` | No | `*` | Fallback 404 for unmatched routes |

### 3.2 Route Details

#### `serve_static_file(asset_path)`

- **URL Pattern**: `/<anyext:asset_path>` — matches paths with a file extension.
- **Rate Limit**: `@limiter.limit(Config.STATIC_LIMITS)`
- **Logic**:
  1. Build the full file path from `Config.STATIC_FOLDER` + `asset_path`.
  2. If the file exists and is not a directory, serve it with
     `Cache-Control: Config.STATIC_CACHE_CONTROL`.
  3. Otherwise, delegate to `RequestHandler` for a 404 error page.

#### `serve_dynamic_content(_path_value)`

- **URL Pattern**: `/` and `/<path:_path_value>` — matches all remaining paths.
- **Logic**: Always delegates to `RequestHandler(g.pr, "404", ...)` which renders
  the 404 error page via the `http_errors` component.

### 3.3 Security Configuration (`manifest.json`)

```json
{
  "security": {
    "routes_auth": {
      "/": false
    },
    "routes_role": {
      "/": ["*"]
    }
  }
}
```

All routes are public (no authentication required). The `["*"]` role means
anyone can access.

---

## 4. Data and Models

This component has no data models, no schema, no forms, and no translations.
It is purely a routing fallback.

---

## 5. NTPL Templates

This component does not define any NTPL templates. Error page rendering is
delegated to the `http_errors` component via `RequestHandler`.

---

## 6. Static Assets

This component does not ship its own static assets. It serves files from the
global `Config.STATIC_FOLDER` (typically `public/`).

---

## 7. Security

### 7.1 Security Matrix

| Aspect | Implementation | Verified |
|--------|----------------|----------|
| Authentication | `routes_auth: {"/": false}` — public | [x] |
| Authorization | `routes_role: {"/": ["*"]}` — open | [x] |
| Rate Limit | `@limiter.limit(Config.STATIC_LIMITS)` on static route | [x] |
| Directory Traversal | `send_from_directory()` prevents path traversal | [x] |
| File Type Restriction | `anyext` route filter requires file extension for static serving | [x] |
| Directory Listing | Explicitly blocked (`not os.path.isdir(file_path)`) | [x] |

### 7.2 Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Path traversal | Low | High | Flask's `send_from_directory()` is safe by design |
| DoS via catch-all | Medium | Medium | Rate limiting via `@limiter.limit()` |
| Information disclosure | Low | Medium | 404 page does not leak path or stack info |

---

## 8. Testing

### 8.1 Testing Strategy

| Type | Location | Coverage |
|------|----------|----------|
| Integration | `tests/` (not yet created) | Route registration, static file serving, 404 fallback |

### 8.2 Critical Test Cases

- [ ] **TC1**: Static file that exists is served with correct `Cache-Control` header.
- [ ] **TC2**: Static file that does not exist returns a 404 error page.
- [ ] **TC3**: Directory path is not served (returns 404).
- [ ] **TC4**: Path without extension falls through to `serve_dynamic_content` and returns 404.
- [ ] **TC5**: Root path `/` returns 404 when no other component handles it.
- [ ] **TC6**: Rate limiting is applied to the static file route.

### 8.3 Execution Commands

```bash
source .venv/bin/activate

# Component tests (when they exist)
pytest src/component/cmp_9100_catch_all/tests -v
```

---

## 9. Acceptance Criteria

### 9.1 Functional

- [x] Static files from `public/` are served when they exist.
- [x] Non-existent paths return a rendered 404 error page.
- [x] Directory paths are not served as files.
- [x] Component loads last due to `cmp_9xxx` prefix.

### 9.2 Technical

- [x] Correct blueprint registration at root level (empty route).
- [x] Stable identity by UUID (`catch_all_0yt2sa`).
- [x] No absolute system paths in code.
- [x] Uses `Config.STATIC_FOLDER` for file resolution.

### 9.3 Security

- [x] Complete `routes_auth` and `routes_role` in `manifest.json`.
- [x] Rate limiting on the static file route.
- [x] `send_from_directory()` prevents directory traversal.
- [x] Directory listing explicitly blocked.

### 9.4 Quality

- [ ] Test coverage — no tests exist yet (risk documented).
- [x] No inline scripts or styles (no templates).
- [x] Documentation complete.

---

## 10. Operations

### 10.1 Deployment

| Action | Command/Procedure |
|--------|-------------------|
| Install | The active component loads automatically (folder starts with `cmp_`) |
| Enable | Use a `cmp_NNNN_name` folder |
| Disable | Rename the folder out of the `cmp_*` pattern, usually `_cmp_NNNN_name` |

### 10.2 Troubleshooting

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| Static files not served | `Config.STATIC_FOLDER` misconfigured | Verify the path in config |
| 404 for all requests | Another component may not be loading | Check component load order and prefixes |
| Rate limit errors | `Config.STATIC_LIMITS` too restrictive | Adjust rate limit in config |

---

## 11. Change History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-05-04 | 0.0.0 | Retrospective spec created from existing implementation | OWL |

---

*Template: component/spec.md*
*Last updated: 2026-05-04*

# Testing: Dynamic Component Routes

## Problem

Component routes are **not stable**: the URL prefix is defined in each component’s `manifest.json` under `route` and is applied when the component blueprint is registered (`url_prefix`).

Many component tests currently **hardcode** paths like:

- `/u/profile`
- `/sign/up`
- `/admin/user`

When a component’s `manifest.json` route changes (or a component is mounted differently), those tests start failing with `404 NOT FOUND` even though the application is correct.

This is a **generic issue** across component tests: tests are coupled to a value that is intentionally configurable.

## Goal

Make tests resilient to route changes by resolving the component base route **dynamically** at test runtime, from the registered Flask blueprint (or its manifest).

## Recommended Approach

### 1) Add a shared fixture to resolve routes

Centralize the logic in `src/component/conftest.py` (shared for component tests). The fixture should:

- Receive `flask_app`
- Locate the blueprint (e.g. `bp_cmp_5000_user`)
- Return `bp.url_prefix` (preferred) or `bp.manifest["route"]`

Example sketch:

```python
import pytest

@pytest.fixture
def component_route(flask_app):
    def _route(component_name: str) -> str:
        bp = flask_app.blueprints[f"bp_{component_name}"]
        return bp.url_prefix  # equals bp.manifest["route"]
    return _route
```

### 2) Use a small helper to join paths safely

Avoid double slashes and keep test code readable:

```python
def join_route(base: str, path: str) -> str:
    base = (base or "").rstrip("/")
    path = (path or "").lstrip("/")
    if not base:
        return f"/{path}" if path else "/"
    return f"{base}/{path}" if path else base
```

### 3) Refactor tests to use the dynamic base route

Instead of:

```python
client.get("/user/profile")
```

Do:

```python
base = component_route("cmp_5000_user")
client.get(join_route(base, "profile"))
```

## Notes / Tradeoffs

- Using `flask_app.blueprints[...]` validates that the component is actually registered in the app used by the test.
- If some test runs with a reduced app (component not loaded), the fixture will fail early with a clear error (missing blueprint) instead of silently producing incorrect URLs.
- This pattern can be applied consistently to **all** component route tests (`cmp_5100_sign`, `cmp_7040_admin`, etc.).


# Component Quickstart (0 to Working Component)

> [!NOTE]
> The `manage-component` skill is available in this project. You can ask the AI directly to create a new component using that skill workflow.

This guide is a practical, minimal path to build a working component in this project, aligned with the `manage-component` workflow.

## 1. Create the Component Folder

Use a `cmp_` prefix so the loader picks it up.
Use `cmp_NNNN_name` naming, where `NNNN` controls load order (commonly in the `5000-7000` range unless you have a reason to place it earlier/later).

```bash
cp -r src/component/cmp_7000_hellocomp src/component/cmp_8000_dashboard
```

Then update identifiers:

- `manifest.json`: set a new `uuid`, `name`, and `route`.
- `schema.json`: remove example-specific data you do not need.

`uuid` should follow `name_random` format (example: `dashboard_8x90s`) and be unique.

## 2. Keep the Required Structure

Minimum recommended structure:

```text
src/component/cmp_8000_dashboard/
├── manifest.json
├── schema.json
├── __init__.py
├── route/
│   ├── __init__.py
│   └── routes.py
└── neutral/
    ├── component-init.ntpl
    └── route/
        └── root/
            ├── data.json
            └── content-snippets.ntpl
```

`__init__.py` is optional if you do not need initialization logic.

## 3. Manifest and Schema Minimum

Minimal `manifest.json` example:

```json
{
  "uuid": "dashboard_8x90s",
  "name": "Dashboard",
  "description": "Dashboard component",
  "version": "1.0.0",
  "route": "/dashboard"
}
```

By default, define menu entries in `schema.json` (`inherit.data.drawer` and `inherit.data.menu`) so the component is reachable from navigation.

## 4. Register Blueprint and Routes

In `route/__init__.py`, create the blueprint via `create_blueprint(...)`:

```python
from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    bp = create_blueprint(component, component_schema)  # pylint: disable=unused-variable
    from . import routes  # pylint: disable=import-error,C0415,W0611
```

In `route/routes.py`, define a route that uses `Dispatcher`:

```python
from flask import request, Response
from core.dispatcher import Dispatcher
from . import bp

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def catch_all(route) -> Response:
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

## 5. Render Real Content in NTPL

Add route metadata in `neutral/route/root/data.json`:

```json
{
  "data": {
    "current": {
      "route": {
        "title": "Dashboard",
        "description": "Dashboard page",
        "h1": "Dashboard"
      }
    }
  }
}
```

Then in `neutral/route/root/content-snippets.ntpl`:

```ntpl
{:data; #/data.json :}

{:snip; current:template:body-main-content >>
    <h3>{:trans; {:;local::current->route->h1:} :}</h3>
    <p>It works.</p>
:}
{:^;:}
```

Without this snippet, your route may render the layout without meaningful page content.

## 6. Test the Component

Run targeted tests while iterating:

```bash
source .venv/bin/activate
pytest -q src/component/cmp_8000_dashboard/tests
```

Run full suite before merging:

```bash
source .venv/bin/activate
pytest -q
```

## 7. Code Quality Check

Run `pylint` for new Python files before merging.

```bash
source .venv/bin/activate
pylint src/component/cmp_8000_dashboard
```

## 8. Production Note

`cmp_7000_hellocomp` is an illustrative example component. In production, disable or remove it unless explicitly needed.

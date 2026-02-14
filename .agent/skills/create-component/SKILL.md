---
name: create-component
description: Create a new Neutral TS component following the standard directory structure and file templates.
---

# Create Neutral TS Component

This skill guides you through creating a completely new component in the Neutral TS framework.

Components are independent modules, and to create one component you don't need to modify others.

## 1. Directory Structure

Create a new directory in `src/component/` starting with `cmp_` followed by a number and name.
Example: `src/component/cmp_7000_hellocomp`

```bash
mkdir -p src/component/cmp_NNNN_name
```

## 2. Manifest and Configuration

### manifest.json
Create `manifest.json` with the component metadata.

```json
{
    "uuid": "name_uuid_suffix",
    "name": "Component Name",
    "description": "Component description",
    "version": "1.0.0",
    "route": "/route-prefix"
}
```

### schema.json
Create `schema.json` for configuration. To add a menu item, you **must** define both the `drawer` (the top-level tab) and the `menu` (the link items inside the tab). The menu may display different options depending on whether the user is logged in ("session:true") or not ("session:"). Always create a menu unless instructed otherwise.

```json
{
    "inherit": {
        "locale": {
            "trans": {
                "en": { "Component Name": "Component Name" },
                "es": { "Component Name": "Nombre Componente" }
            }
        },
        "data": {
            "drawer": {
                "menu": {
                    "session:": {
                        "component-tab": {
                            "name": "Component Name",
                            "tabs": "component-tab",
                            "icon": "x-icon-info"
                        }
                    },
                    "session:true": {
                        "component-tab": {
                            "name": "Component Name",
                            "tabs": "component-tab",
                            "icon": "x-icon-info"
                        }
                    }
                }
            },
            "menu": {
                "session:": {
                    "component-tab": {
                        "component": {
                            "text": "Component Name",
                            "link": "[:;data->name_uuid_suffix->manifest->route:]",
                            "icon": "x-icon-info"
                        }
                    }
                },
                "session:true": {
                    "component-tab": {
                        "component": {
                            "text": "Component Name",
                            "link": "[:;data->name_uuid_suffix->manifest->route:]",
                            "icon": "x-icon-info"
                        }
                    }
                }
            }
        }
    }
}
```

## 3. Python Initialization

### __init__.py
Initialize the component. This is optional, only if you need to do something on component initialization.

```python
def init_component(component, component_schema, _schema):
    pass
```

## 4. Backend Routes

### route/__init__.py
Initialize the Blueprint.

```python
from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    """Blueprint Init"""
    bp = create_blueprint(component, component_schema) # pylint: disable=unused-variable
    # Import routes after creating the blueprint
    from . import routes  # pylint: disable=import-error,C0415,W0611
```

### route/routes.py
Define the routes. The dispatcher connects Flask requests to the Neutral Templating system.

```python
from flask import request, Response
from core.dispatcher import Dispatcher
from . import bp

@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def index(route) -> Response:
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
```

## 5. Frontend Templates

### neutral/route/root/data.json
Define route configuration and metadata.

```json
{
    "data": {
        "current": {
            "route": {
                "title": "Page Title",
                "description": "Page Description",
                "h1": "Main Heading"
            }
        }
    }
}
```

### neutral/route/root/content-snippets.ntpl
Define the main content of the page using Neutral Templates (NTPL).

```html
{:*
    Data for this route
    -------------------
*:}
{:data; #/data.json :}

{:snip; current:template:body-main-content >>
    <div class="container">
        <h3>{:trans; {:;local::current->route->h1:} :}</h3>
        <p>{:trans; Example of a simple component :}</p>
    </div>
:}
{:^;:}
```

## 6. Implementation Checklist

1.  **Create Directory**: `src/component/cmp_NNNN_name`
2.  **Manifest**: `src/component/cmp_NNNN_name/manifest.json` (mandatory)
3.  **Schema**: `src/component/cmp_NNNN_name/schema.json` (if needed, eg. for menu items, etc)
4.  **Init**: `src/component/cmp_NNNN_name/__init__.py` (if needed)
5.  **Route Init**: `src/component/cmp_NNNN_name/route/__init__.py` (if needed routes)
6.  **Routes**: `src/component/cmp_NNNN_name/route/routes.py` (if needed routes)
7.  **Template Data**: `src/component/cmp_NNNN_name/neutral/route/root/data.json`
8.  **Template Content**: `src/component/cmp_NNNN_name/neutral/route/root/content-snippets.ntpl`
9.  **Static Files**: `src/component/cmp_NNNN_name/static/` (if needed)

Use `view_file` on `docs/component.md` for more advanced options.
Use `view_file` on `docs/templates-neutrats.md` for more template options.

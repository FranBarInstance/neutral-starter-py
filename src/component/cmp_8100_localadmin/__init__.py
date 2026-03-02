"""Local Admin component init."""

# from app.app import app

from flask import current_app

def init_component(component, component_schema, _schema):
    """Component - Init"""

    debug = component_schema.get('config', {}).get('app', {}).get('debug', False)
    if not debug:
        return

    route = component['manifest']['route']

    drawer = {
        'menu': {
            'session:': {
                'localadmin': {
                    "name": "Local Admin",
                    "tabs": "localadmin",
                    "icon": "x-icon-dev",
                }
            },
            'session:true': {
                'localadmin': {
                    "name": "Local Admin",
                    "tabs": "localadmin",
                    "icon": "x-icon-dev",
                }
            }
        }
    }

    component_schema['inherit']['data']['drawer'] = drawer

    menu = {
        "session:": {
            "localadmin": {
                "localadmin-home": {
                    "text": "Local Admin",
                    "link": route,
                    "icon": "x-icon-dev"
                },
                "custom": {
                    "text": "Custom json",
                    "link": f"{route}/custom",
                    "icon": "x-icon-setting"
                },
                "icons": {
                    "text": "Icons list",
                    "link": f"{route}/icons",
                    "icon": "x-icon-greeting"
                }
            }
        },
        "session:true": {
            "localadmin": {
                "localadmin-home": {
                    "text": "Local Admin",
                    "link": route,
                    "icon": "x-icon-dev"
                },
                "custom": {
                    "text": "Custom json",
                    "link": f"{route}/custom",
                    "icon": "x-icon-setting"
                },
                "icons": {
                    "text": "Icons list",
                    "link": f"{route}/icons",
                    "icon": "x-icon-greeting"
                }
            }
        }
    }

    component_schema['inherit']['data']['menu'] = menu

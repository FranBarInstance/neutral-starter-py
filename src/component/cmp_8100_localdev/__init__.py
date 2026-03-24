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
                'localdev': {
                    "name": "Local Admin",
                    "tabs": "localdev",
                    "icon": "x-icon-dev",
                }
            },
            'session:true': {
                'localdev': {
                    "name": "Local Admin",
                    "tabs": "localdev",
                    "icon": "x-icon-dev",
                }
            }
        }
    }

    component_schema['data']['current']['drawer'] = drawer

    menu = {
        "session:": {
            "localdev": {
                "localdev-home": {
                    "text": "Local Admin",
                    "link": route,
                    "icon": "x-icon-dev"
                },
                "login": {
                    "text": "Login",
                    "link": f"{route}/login",
                    "icon": "x-icon-sign-in"
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
            "localdev": {
                "localdev-home": {
                    "text": "Local Admin",
                    "link": route,
                    "icon": "x-icon-dev"
                },
                "login": {
                    "text": "Login",
                    "link": f"{route}/login",
                    "icon": "x-icon-sign-in"
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

    component_schema['data']['current']['menu'] = menu

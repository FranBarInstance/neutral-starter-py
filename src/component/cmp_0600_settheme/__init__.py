"""Component locale - Init"""

from app.config import Config


def init_component(component, component_schema, _schema):
    """Component - Init"""
    menu_drawer(component, component_schema)
    menu_navbar(component, component_schema)


def menu_drawer(component, component_schema):
    """Component - Menu Drawer"""
    themes = component_schema['data']['current']['theme']['allow_themes']
    colors = component_schema['data']['current']['theme']['allow_colors']

    if len(themes) < 2 or not component['manifest']['config']['menu-theme-drawer-enable']:
        component_schema['data']['current']['menu']['session:']['setting']['theme'] = None
        component_schema['data']['current']['menu']['session:true']['setting']['theme'] = None
    else:
        menu = build_drawer_menu('Theme', 'x-icon-theme', themes, Config.THEME_KEY)
        component_schema['data']['current']['menu']['session:']['setting']['theme'] = menu
        component_schema['data']['current']['menu']['session:true']['setting']['theme'] = menu

    if len(colors) < 2 or not component['manifest']['config']['menu-color-drawer-enable']:
        component_schema['data']['current']['menu']['session:']['setting']['color'] = None
        component_schema['data']['current']['menu']['session:true']['setting']['color'] = None
        return

    menu = build_drawer_menu('Color', 'x-icon-color', colors, Config.THEME_COLOR_KEY)
    component_schema['data']['current']['menu']['session:']['setting']['color'] = menu
    component_schema['data']['current']['menu']['session:true']['setting']['color'] = menu


def menu_navbar(component, component_schema):
    """Component - Menu Navbar"""
    themes = component_schema['data']['current']['theme']['allow_themes']
    colors = component_schema['data']['current']['theme']['allow_colors']

    if len(themes) < 2 or not component['manifest']['config']['menu-theme-navbar-enable']:
        component_schema['data']['navbar']['menu']['session:']['theme'] = None
        component_schema['data']['navbar']['menu']['session:true']['theme'] = None
    else:
        menu = build_navbar_menu('Theme', 'x-icon-theme', themes, Config.THEME_KEY)
        component_schema['data']['navbar']['menu']['session:']['theme'] = menu
        component_schema['data']['navbar']['menu']['session:true']['theme'] = menu

    if len(colors) < 2 or not component['manifest']['config']['menu-color-navbar-enable']:
        component_schema['data']['navbar']['menu']['session:']['color'] = None
        component_schema['data']['navbar']['menu']['session:true']['color'] = None
        return

    menu = build_navbar_menu('Color', 'x-icon-color', colors, Config.THEME_COLOR_KEY)
    component_schema['data']['navbar']['menu']['session:']['color'] = menu
    component_schema['data']['navbar']['menu']['session:true']['color'] = menu


def build_drawer_menu(name, icon, values, config_key):
    """Build drawer dropdown menu."""
    menu = {
        'name': name,
        'link': '',  # is a button, not a link
        'icon': icon,
        'prop': {},
        'dropdown': {}
    }

    for value in values:
        menu['dropdown'][value] = {
            'text': value,
            'link': f'?{config_key}={value}',
            'icon': 'x-icon-bullet',
            'prop': {}
        }

    return menu


def build_navbar_menu(name, icon, values, config_key):
    """Build navbar dropdown menu."""
    menu = {
        'name': name,
        'link': '',
        'icon': icon,
        'prop': {},
        'dropdown': {}
    }

    for value in values:
        menu['dropdown'][value] = {
            'name': value,
            'link': f'?{config_key}={value}',
            'icon': 'x-icon-none',
            'prop': {}
        }

    return menu

"""Component locale - Init"""

from app.config import Config


def init_component(component, component_schema, _schema):
    """Component - Init"""
    menu_drawer(component, component_schema)
    menu_navbar(component, component_schema)


def menu_drawer(component, component_schema):
    """Component - Menu Drawer"""
    themes = component_schema['inherit']['data']['current']['theme']['allow_themes']

    if len(themes) < 2 or not component['manifest']['config']['menu-drawer-enable']:
        component_schema['inherit']['data']['menu']['session:']['setting']['theme'] = None
        component_schema['inherit']['data']['menu']['session:true']['setting']['theme'] = None
        return

    # Language drawer menu for dropdown
    menu = {
        'name': 'Theme',
        'link': '', # is a button, not a link
        'icon': 'x-icon-theme',
        'prop': {},
        'dropdown': {}
    }

    # create menu dropdown items
    for theme in themes:
        menu['dropdown'][theme] = {
            'text': theme,
            'link': f'?{Config.THEME_KEY}={theme}',
            'icon': 'x-icon-bullet',
            'prop': {}
        }

    # set menu in local data
    component_schema['inherit']['data']['menu']['session:']['setting']['theme'] = menu
    component_schema['inherit']['data']['menu']['session:true']['setting']['theme'] = menu


def menu_navbar(component, component_schema):
    """Component - Menu Navbar"""
    themes = component_schema['inherit']['data']['current']['theme']['allow_themes']

    if len(themes) < 2 or not component['manifest']['config']['menu-navbar-enable']:
        component_schema['inherit']['data']['navbar']['menu']['session:']['theme'] = None
        component_schema['inherit']['data']['navbar']['menu']['session:true']['theme'] = None
        return

    # Language navbar menu for dropdown
    menu = {
        'name': 'Theme',
        'link': '',
        'icon': 'x-icon-theme',
        'prop': {},
        'dropdown': {}
    }

    # create menu dropdown items
    for theme in themes:
        menu['dropdown'][theme] = {
            'name': theme,
            'link': f'?{Config.THEME_KEY}={theme}',
            'icon': 'x-icon-none',
            'prop': {}
        }

    # set menu in local data
    component_schema['inherit']['data']['navbar']['menu']['session:']['theme'] = menu
    component_schema['inherit']['data']['navbar']['menu']['session:true']['theme'] = menu

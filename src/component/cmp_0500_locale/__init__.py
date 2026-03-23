"""Component locale - Init"""

from app.config import Config


def init_component(component, component_schema, _schema):
    """Component - Init"""
    menu_drawer(component, component_schema)
    menu_navbar(component, component_schema)


def menu_drawer(component, component_schema):
    """Component - Menu Drawer"""
    languages = component_schema['data']['current']['site']['languages']
    tab = component['manifest']['config']['menu-drawer-tab']

    if tab not in component_schema['inherit']['data']['menu']['session:']:
        component_schema['inherit']['data']['menu']['session:'][tab] = {}
    if tab not in component_schema['inherit']['data']['menu']['session:true']:
        component_schema['inherit']['data']['menu']['session:true'][tab] = {}

    if len(languages) < 2 or not component['manifest']['config']['menu-drawer-enable']:
        component_schema['inherit']['data']['menu']['session:'][tab]['language'] = None
        component_schema['inherit']['data']['menu']['session:true'][tab]['language'] = None
        return

    # Language drawer menu for dropdown
    menu = {
        'name': 'Language',
        'link': '', # is a button, not a link
        'icon': 'x-icon-locale',
        'prop': {},
        'dropdown': {}
    }

    # create menu dropdown items
    for lang in languages:
        menu['dropdown'][lang] = {
            'text': f'ref:locale:{lang}',
            'link': f'?{Config.LANG_KEY}={lang}',
            'icon': 'x-icon-bullet',
            'prop': {}
        }

    # set menu in local data
    component_schema['inherit']['data']['menu']['session:'][tab]['language'] = menu
    component_schema['inherit']['data']['menu']['session:true'][tab]['language'] = menu


def menu_navbar(component, component_schema):
    """Component - Menu Navbar"""
    languages = component_schema['data']['current']['site']['languages']

    if len(languages) < 2 or not component['manifest']['config']['menu-navbar-enable']:
        component_schema['inherit']['data']['navbar']['menu']['session:']['language'] = None
        component_schema['inherit']['data']['navbar']['menu']['session:true']['language'] = None
        return

    # Language navbar menu for dropdown
    menu = {
        'name': 'Language',
        'link': '',
        'icon': 'x-icon-locale',
        'prop': {},
        'dropdown': {}
    }

    # create menu dropdown items
    for lang in languages:
        menu['dropdown'][lang] = {
            'name': f'ref:locale:{lang}',
            'link': f'?{Config.LANG_KEY}={lang}',
            'icon': 'x-icon-bullet',
            'prop': {}
        }

    # set menu in local data
    component_schema['inherit']['data']['navbar']['menu']['session:']['language'] = menu
    component_schema['inherit']['data']['navbar']['menu']['session:true']['language'] = menu

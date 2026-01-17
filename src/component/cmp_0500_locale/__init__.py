"""Component locale - Init"""

from app.config import Config


def init_component(component, component_schema, _schema):
    """Component - Init"""

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

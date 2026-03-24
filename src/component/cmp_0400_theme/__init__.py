"""Component locale - Init"""

from app.config import Config


def init_component(component, component_schema, _schema):
    """Component - Init"""

    if not component['manifest']['config']['menu-drawer-enable']:
        component_schema['data']['current']['menu']['session:']['setting']['darkmode'] = None
        component_schema['data']['current']['menu']['session:true']['setting']['darkmode'] = None

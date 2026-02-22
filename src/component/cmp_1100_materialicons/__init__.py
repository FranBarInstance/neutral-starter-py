"""Dev Admin component init."""


def init_component(_component, component_schema, _schema):
    """Component init hook."""

    component_schema['inherit']['data']['list-x-icons'] = {}
    for key, value in component_schema['inherit']['data'].items():
        if key.startswith('x-icon-'):
            component_schema['inherit']['data']['list-x-icons'][key] = value

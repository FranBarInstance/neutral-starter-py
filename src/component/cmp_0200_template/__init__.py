"""Template Component - Inicialización"""

from app.components import set_current_template  # pylint: disable=import-error


def init_component(component, component_schema, _schema):
    """Component Initialization"""

    # Set this component for the current template for app, all components.
    _template_dir, _template_route = set_current_template(component, component_schema)

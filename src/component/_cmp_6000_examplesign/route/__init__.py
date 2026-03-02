"""Route init module for component examplesign"""

from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    """Blueprint Init"""

    # Create the blueprint and make it available in the component module
    bp = create_blueprint(component, component_schema)  # pylint: disable=unused-variable

    # Import routes after creating the blueprint to avoid circular imports
    from . import routes  # pylint: disable=import-error,C0415,W0611

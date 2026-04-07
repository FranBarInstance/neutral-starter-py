"""Image Zoom route initialization."""

from app.components import create_blueprint

def init_blueprint(component, component_schema, _schema):
    """Blueprint Init"""
    # pylint: disable=unused-variable
    bp = create_blueprint(component, component_schema)
    # Import routes after creating the blueprint
    from . import routes  # pylint: disable=import-error,C0415,W0611

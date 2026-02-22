"""Blueprint initialization for admin component."""

from app.components import create_blueprint


def init_blueprint(component, component_schema, _schema):
    """Blueprint init."""
    bp = create_blueprint(component, component_schema)  # pylint: disable=unused-variable
    from . import routes  # pylint: disable=import-error,C0415,W0611

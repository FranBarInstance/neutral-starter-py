
"""Hello Component Blueprint Module."""

from app.components import create_blueprint


def init_blueprint(component, component_schema, _schema):
    """Blueprint Init"""

    bp = create_blueprint(component, component_schema) # pylint: disable=unused-variable

    # Import routes after creating the blueprint
    from . import routes  # pylint: disable=import-error,C0415,W0611

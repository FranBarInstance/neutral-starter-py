"""
Mail template component
"""
from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    """
    Initialize the component by registering the mail templates in the system
    """
    set_current_mail_template(component, component_schema)

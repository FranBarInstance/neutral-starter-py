from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    """
    Inicializa el componente registrando las plantillas de correo en el sistema
    usando la infraestructura de 010-mail-system.
    """
    set_current_mail_template(component, component_schema)

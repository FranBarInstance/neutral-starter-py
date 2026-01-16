"""Component RRSS - Init"""

def init_component(component, component_schema, _schema):
    """Component - Init"""

    route = component['manifest']['route']
    set_local_data(component, component_schema)
    set_menu(route, component['manifest']['config']['rrss_urls'], component_schema)


def set_local_data(component, component_schema):
    """Component - Set Local Data"""
    rrss_urls = {}
    rrss_valid_names = ''

    for name, url in component['manifest']['config']['rrss_urls'].items():
        if not url:
            continue

        rrss_urls[name] = url
        rrss_valid_names += f"{name}\n"

    component_schema['inherit']['data']['rsss_default'] = component['manifest']['config']['rsss_default']
    component_schema['inherit']['data']['rrss_urls'] = rrss_urls
    component_schema['inherit']['data']['rrss_valid_names'] = rrss_valid_names


def set_menu(route, rrss_urls, component_schema):
    """Component - Set Menu"""

    menu = {
        'session:': {
            'rrss': {
                'root': component_schema['inherit']['data']['menu']['session:']['rrss']['root']
            }
        },
        'session:true': {
            'rrss': {
                'root': component_schema['inherit']['data']['menu']['session:true']['rrss']['root']
            }
        }
    }

    # create menu items
    for name, url in rrss_urls.items():
        if not url:
            continue
        menu['session:']['rrss'][name] = {
            'text': name,
            'link': f'{route}/rss/{name}',
            'icon': 'x-icon-rss',
            'class': 'click-load-spin'
        }
        menu['session:true']['rrss'][name] = {
            'text': name,
            'link': f'{route}/rss/{name}',
            'icon': 'x-icon-rss',
            'class': 'click-load-spin'
        }

    # set menu in local data
    component_schema['inherit']['data']['menu'] = menu

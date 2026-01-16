# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-pwa-py (See LICENCE)

"""Dispatcher for Read RSS."""

from core.dispatcher import Dispatcher  # pylint: disable=import-error


class DispatcherRrss(Dispatcher):
    """Dispatcher for Read RSS."""

    def set_rss_name(self, component_schema, rrss_name=None) -> bool:
        """Set RSS name."""

        if rrss_name is None:
            self.schema_data['rrss_name'] = component_schema['inherit']['data']['rsss_default']
            return True

        if rrss_name not in component_schema['inherit']['data']['rrss_urls']:
            self.schema_data['rrss_name'] = ''
            return False

        self.schema_data['rrss_name'] = rrss_name
        return True

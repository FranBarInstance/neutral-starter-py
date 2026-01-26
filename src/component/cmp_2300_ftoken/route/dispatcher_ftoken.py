"""FToken dispatcher module."""

from ftoken_0yt2sa import ftoken_create

from core.dispatcher import Dispatcher


class DispatcherFtoken(Dispatcher):
    """Dispatcher class specialized for ftoken operations."""

    def ftoken(self, key, fetch_id, form_id) -> bool:
        """Generate and store form token."""
        self.schema_data['ftoken'] = ftoken_create(
            key,
            fetch_id,
            form_id,
            self.schema_data['CONTEXT']['UTOKEN']
        )
        return True

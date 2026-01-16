# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Hello component dispatcher."""

from core.dispatcher import Dispatcher  # pylint: disable=import-error


class DispatcherHelloComp(Dispatcher):
    """Hello component dispatcher."""

    def __init__(self, request, comp_route, neutral_route=None):
        super().__init__(request, comp_route, neutral_route)
        self.schema_local_data['foo'] = "bar"

    def test1(self):
        """business logic for test1 requests."""
        return True

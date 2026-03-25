# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Hello component request handler."""

from core.request_handler import RequestHandler


class HelloCompRequestHandler(RequestHandler):
    """Hello component request handler."""

    def __init__(self, prepared_request, comp_route: str = "", neutral_route: str | None = None):
        super().__init__(prepared_request, comp_route, neutral_route)
        self.schema_local_data['foo'] = "bar"

    def test1(self):
        """Business logic for test1 requests."""
        return True

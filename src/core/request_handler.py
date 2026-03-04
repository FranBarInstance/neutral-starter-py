"""Request handler base that consumes PreparedRequest (`g.pr`)."""

from .prepared_request import PreparedRequest


class RequestHandler:  # pylint: disable=too-few-public-methods
    """Thin adapter around PreparedRequest for blueprint route handlers."""

    def __init__(self, prepared_request: PreparedRequest, comp_route="", neutral_route=None):
        self.pr = prepared_request
        self.pr.set_route_context(route=comp_route, neutral_route=neutral_route)

        self.req = self.pr.req
        self.schema = self.pr.schema
        self.schema_data = self.pr.schema_data
        self.schema_local_data = self.pr.schema_local_data
        self.ajax_request = self.pr.ajax_request
        self.session = self.pr.session
        self.user = self.pr.user
        self.view = self.pr.view

    def render_route(self):
        """Default route render behavior."""
        return self.view.render()

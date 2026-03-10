"""Request handler base that consumes PreparedRequest (`g.pr`)."""

from typing import TYPE_CHECKING
from app.config import Config

if TYPE_CHECKING:
    from .prepared_request import PreparedRequest


class RequestHandler:
    """Thin adapter around PreparedRequest for blueprint route handlers.

    Provides convenient access to PreparedRequest context and default
    route rendering behavior. Does NOT re-evaluate security policies
    (those are evaluated once in the global before_request).
    """

    def __init__(
        self,
        prepared_request: "PreparedRequest",
        comp_route: str = "",
        neutral_route: str | None = None
    ):
        """Initialize handler with PreparedRequest context.

        Args:
            prepared_request: The PreparedRequest built in before_request
            comp_route: Component-relative route path
            neutral_route: Neutral template route path
        """
        self.pr = prepared_request

        # Expose commonly used attributes for convenience
        self.req = self.pr.req
        self.schema = self.pr.schema
        self.schema_data = self.pr.schema_data
        self.schema_local_data = self.pr.schema_local_data
        self.ajax_request = self.pr.ajax_request
        self.session = self.pr.session
        self.user = self.pr.user
        self.view = self.pr.view

        # update from user profile
        if self.schema_data['USER']['profile'].get('properties'):
            user_prop = self.schema_data['USER']['profile']['properties']
            if user_prop.get('theme'):
               self.schema_local_data['current']['theme']['theme'] = user_prop['theme']
            if user_prop.get('color'):
                self.schema_local_data['current']['theme']['color'] = user_prop['color']
        if self.schema_data['USER']['profile'].get('locale'):
            self.schema.properties['inherit']['locale']['current'] = self.schema_data['USER']['profile']['locale']

        # Set CURRENT_COMP_ROUTE with actual component-relative route
        # This is the route value from the route handler (e.g., "users" from "/<path:route>")
        normalized_comp_route = f"{Config.COMP_ROUTE_ROOT}/{comp_route or ''}".strip("/")
        self.schema_data["CURRENT_COMP_ROUTE"] = normalized_comp_route
        self.schema_data["CURRENT_COMP_ROUTE_SANITIZED"] = normalized_comp_route.replace("/", ":")

        # Store route context for potential template/debug use
        self.comp_route = comp_route
        self.neutral_route = neutral_route

        # Expose security decision
        self.allowed = self.pr.allowed
        self.deny_status = self.pr.deny_status
        self.deny_reason = self.pr.deny_reason

    def render_route(self):
        """Default route render behavior.

        Returns the rendered template response from the view.
        Component handlers can extend this for custom behavior.
        """
        return self.view.render()

    def render_error(self, status: int = 404, message: str = "", param: str = ""):
        """Render error response.

        Args:
            status: HTTP status code
            message: Error message
            param: Additional error parameter
        """
        return self.view.render_error(status, message, param)

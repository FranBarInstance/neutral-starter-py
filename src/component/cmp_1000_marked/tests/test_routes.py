"""Tests for the marked component routes."""


class TestMarkedRoutes:
    """Integration tests for marked component routes."""

    def test_marked_esm_file(self, client):
        """Test GET /marked/marked.esm.js returns the JavaScript module."""
        response = client.get("/marked/marked.esm.js")
        assert response.status_code == 200
        assert "javascript" in response.content_type
        assert "Cache-Control" in response.headers

    def test_component_init_uses_local_asset(self):
        """The component should not depend on a CDN-hosted module."""
        with open(
            "src/component/cmp_1000_marked/neutral/component-init.ntpl",
            "r",
            encoding="utf-8",
        ) as file:
            template = file.read()

        assert "cdnjs.cloudflare.com" not in template
        assert "import { marked } from '{:;marked_0yt2sa->manifest->route:}/marked.esm.js';" in template

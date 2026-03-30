"""Tests for the materialicons component routes."""


class TestMaterialIconsRoutes:
    """Integration tests for materialicons component routes."""

    def test_materialicons_css_file(self, client):
        """Test GET /materialicons/materialdesignicons.min.css returns the CSS file."""
        response = client.get("/materialicons/materialdesignicons.min.css")
        assert response.status_code == 200
        assert "css" in response.content_type
        assert "Cache-Control" in response.headers

    def test_materialicons_font_file(self, client):
        """Test GET /materialicons/fonts/materialdesignicons-webfont.woff2 returns a font file."""
        response = client.get("/materialicons/fonts/materialdesignicons-webfont.woff2")
        assert response.status_code == 200
        assert "font" in response.content_type or "application/octet-stream" in response.content_type
        assert "Cache-Control" in response.headers

    def test_component_init_uses_local_asset(self):
        """The component should not depend on a CDN-hosted stylesheet."""
        with open(
            "src/component/cmp_1100_materialicons/neutral/component-init.ntpl",
            "r",
            encoding="utf-8",
        ) as file:
            template = file.read()

        assert "cdnjs.cloudflare.com" not in template
        assert 'href="{:;materialicons_0yt2sa->manifest->route:}/materialdesignicons.min.css"' in template

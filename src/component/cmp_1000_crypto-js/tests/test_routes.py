"""Tests for the crypto-js component routes."""


class TestCryptoJsRoutes:
    """Integration tests for crypto-js component routes."""

    def test_crypto_js_file(self, client):
        """Test GET /crypto-js.min.js returns the JavaScript file."""
        response = client.get("/crypto-js.min.js")
        assert response.status_code == 200
        assert "javascript" in response.content_type
        assert "Cache-Control" in response.headers

    def test_component_init_uses_local_asset(self):
        """The component should not depend on a CDN-hosted asset."""
        with open(
            "src/component/cmp_1000_crypto-js/neutral/component-init.ntpl",
            "r",
            encoding="utf-8",
        ) as file:
            template = file.read()

        assert "cdnjs.cloudflare.com" not in template
        assert 'src="/crypto-js.min.js"' in template

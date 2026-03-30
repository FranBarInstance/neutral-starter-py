"""Tests for the crypto-js component routes."""

import json
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
ASSET_ROUTE = f"{MANIFEST['route']}/crypto-js.min.js"


class TestCryptoJsRoutes:
    """Integration tests for crypto-js component routes."""

    def test_crypto_js_file(self, client):
        """Test GET /crypto-js.min.js returns the JavaScript file."""
        response = client.get(ASSET_ROUTE)
        assert response.status_code == 200
        assert "javascript" in response.content_type
        assert "Cache-Control" in response.headers

    def test_component_init_uses_local_asset(self):
        """The component should not depend on a CDN-hosted asset."""
        template = (COMPONENT_ROOT / "neutral" / "component-init.ntpl").read_text(
            encoding="utf-8"
        )

        assert "cdnjs.cloudflare.com" not in template
        assert "cryptojs_0yt2sa->manifest->route" in template
        assert 'src="{:;cryptojs_0yt2sa->manifest->route:}/crypto-js.min.js"' in template

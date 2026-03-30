"""Tests for the marked component routes."""

import json
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestMarkedRoutes:
    """Integration tests for marked component routes."""

    def test_marked_esm_file(self, client):
        """Test GET /marked/marked.esm.js returns the JavaScript module."""
        response = client.get(f"{BASE_ROUTE}/marked.esm.js")
        assert response.status_code == 200
        assert "javascript" in response.content_type
        assert "Cache-Control" in response.headers

    def test_component_init_uses_local_asset(self):
        """The component should not depend on a CDN-hosted module."""
        template = (COMPONENT_ROOT / "neutral" / "component-init.ntpl").read_text(
            encoding="utf-8"
        )

        assert "cdnjs.cloudflare.com" not in template
        assert "import { marked } from '{:;marked_0yt2sa->manifest->route:}/marked.esm.js';" in template

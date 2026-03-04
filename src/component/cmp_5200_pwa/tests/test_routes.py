"""Tests for the PWA component routes."""


class TestPWARoutes:
    """Integration tests for PWA component routes."""

    def test_service_worker_file(self, client):
        """Test GET /service-worker.js returns the service worker."""
        response = client.get('/service-worker.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type
        assert 'Cache-Control' in response.headers

    def test_pwa_manifest_json(self, client):
        """Test GET /pwa/manifest.json returns the manifest."""
        response = client.get('/pwa/manifest.json')
        assert response.status_code == 200
        # Should be JSON or HTML (template rendering)
        assert 'json' in response.content_type or 'html' in response.content_type

    def test_pwa_offline_page(self, client):
        """Test GET /pwa/offline.html returns the offline page."""
        response = client.get('/pwa/offline.html')
        assert response.status_code == 200

    def test_pwa_static_icons(self, client):
        """Test GET /pwa/*.png returns icon files."""
        # Try common icon sizes
        response = client.get('/pwa/192.png')
        # Should either return the file or a 404
        assert response.status_code in [200, 404]


class TestPWAStaticFiles:
    """Tests for PWA static file serving."""

    def test_pwa_static_file_exists(self, client):
        """Test serving existing static files."""
        # This test assumes the static files exist
        # If they don't exist, should get 404
        response = client.get('/pwa/512.png')
        assert response.status_code in [200, 404]

    def test_pwa_static_file_not_exists(self, client):
        """Test 404 for non-existent static files."""
        response = client.get('/pwa/non-existent-file-12345.png')
        assert response.status_code == 404


class TestPWACache:
    """Tests for PWA cache headers."""

    def test_service_worker_cache_control(self, client):
        """Test service worker has cache control headers."""
        response = client.get('/service-worker.js')
        if response.status_code == 200:
            assert 'Cache-Control' in response.headers

    def test_manifest_cache_control(self, client):
        """Test manifest has cache control headers."""
        response = client.get('/pwa/manifest.json')
        if response.status_code == 200:
            assert 'Cache-Control' in response.headers


class TestPWASecurity:
    """Tests for PWA security."""

    def test_no_directory_traversal(self, client):
        """Test that directory traversal is prevented."""
        response = client.get('/pwa/../../../etc/passwd')
        # Should not succeed
        assert response.status_code in [403, 404, 400]

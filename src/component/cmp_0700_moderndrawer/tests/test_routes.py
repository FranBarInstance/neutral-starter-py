"""Tests for the moderndrawer component routes."""


class TestModernDrawerRoutes:
    """Integration tests for moderndrawer component routes."""

    def test_moderndrawer_css_file(self, client):
        """Test GET /css/moderndrawer.min.css returns the CSS file."""
        response = client.get('/css/moderndrawer.min.css')
        assert response.status_code == 200
        assert 'css' in response.content_type
        assert 'Cache-Control' in response.headers

    def test_moderndrawer_js_file(self, client):
        """Test GET /js/moderndrawer.min.js returns the JavaScript file."""
        response = client.get('/js/moderndrawer.min.js')
        assert response.status_code == 200
        assert 'javascript' in response.content_type
        assert 'Cache-Control' in response.headers


class TestModernDrawerAccess:
    """Tests for route access control."""

    def test_static_routes_accessible(self, client):
        """Test that static routes are publicly accessible."""
        css_response = client.get('/css/moderndrawer.min.css')
        js_response = client.get('/js/moderndrawer.min.js')

        assert css_response.status_code == 200
        assert js_response.status_code == 200


class TestModernDrawerSecurity:
    """Tests for security-related behaviors."""

    def test_css_cache_control(self, client):
        """Test CSS file has cache control headers."""
        response = client.get('/css/moderndrawer.min.css')
        assert response.status_code == 200
        assert 'Cache-Control' in response.headers

    def test_js_cache_control(self, client):
        """Test JS file has cache control headers."""
        response = client.get('/js/moderndrawer.min.js')
        assert response.status_code == 200
        assert 'Cache-Control' in response.headers

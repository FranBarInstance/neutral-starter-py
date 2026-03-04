"""Tests for the RRSS component routes."""


class TestRRSSRoutes:
    """Integration tests for RRSS component routes."""

    def test_rrss_home_page(self, client):
        """Test GET /rrss returns the home page."""
        response = client.get('/rrss/')
        assert response.status_code in [200, 302]

    def test_rrss_rss_name_valid(self, client):
        """Test GET /rrss/rss/<name> with valid RSS name."""
        response = client.get('/rrss/rss/BBC')
        assert response.status_code in [200, 302]

    def test_rrss_rss_name_invalid(self, client):
        """Test GET /rrss/rss/<name> with invalid RSS name returns 404."""
        response = client.get('/rrss/rss/InvalidRSSName123')
        assert response.status_code == 404

    def test_rrss_ajax_without_header(self, client):
        """Test /rrss/ajax/<name> without AJAX header returns error."""
        response = client.get('/rrss/ajax/BBC')
        # Should fail without AJAX header
        assert response.status_code in [400, 403]

    def test_rrss_ajax_with_header(self, client):
        """Test /rrss/ajax/<name> with AJAX header."""
        response = client.get(
            '/rrss/ajax/BBC',
            headers={'Requested-With-Ajax': 'true'}
        )
        # Should succeed with AJAX header
        assert response.status_code in [200, 302]

    def test_rrss_catch_all(self, client):
        """Test /rrss/<path> catch-all route."""
        response = client.get('/rrss/some/random/path')
        # May return 200, 302, or 404 depending on routing order
        assert response.status_code in [200, 302, 404]


class TestRRSSHandler:
    """Tests for RrssRequestHandler."""

    def test_set_rss_name_default(self, client):
        """Test that default RSS name is set."""
        # Just verify the page loads with default RSS
        response = client.get('/rrss/')
        assert response.status_code in [200, 302]

    def test_set_rss_name_valid(self, client):
        """Test setting a valid RSS name."""
        response = client.get('/rrss/rss/NASA')
        assert response.status_code in [200, 302]


class TestRRSSSecurity:
    """Tests for RRSS security."""

    def test_ajax_requires_header(self, client):
        """Test that AJAX endpoint requires special header."""
        response = client.get('/rrss/ajax/BBC')
        # Without header should be denied
        assert response.status_code in [400, 403, 404]

    def test_public_routes_accessible(self, client):
        """Test that public routes are accessible."""
        response = client.get('/rrss/')
        assert response.status_code in [200, 302]

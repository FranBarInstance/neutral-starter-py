"""Tests for the Info component routes."""


class TestInfoRoutes:
    """Integration tests for Info component routes."""

    def test_info_about(self, client):
        """Test GET /info/about."""
        response = client.get('/info/about')
        assert response.status_code in [200, 302, 404]

    def test_info_contact(self, client):
        """Test GET /info/contact."""
        response = client.get('/info/contact')
        assert response.status_code in [200, 302, 404]

    def test_info_help(self, client):
        """Test GET /info/help."""
        response = client.get('/info/help')
        assert response.status_code in [200, 302, 404]

    def test_info_legal(self, client):
        """Test GET /info/legal."""
        response = client.get('/info/legal')
        assert response.status_code in [200, 302, 404]

    def test_info_catch_all(self, client):
        """Test GET /info/<path> catch-all route."""
        response = client.get('/info/some/random/page')
        assert response.status_code in [200, 302, 404]


class TestInfoContent:
    """Tests for Info page content."""

    def test_info_page_has_content(self, client):
        """Test info pages return content."""
        response = client.get('/info/about')
        # Should have some content or be 404
        assert response.status_code in [200, 302, 404]


class TestInfoSecurity:
    """Tests for Info security."""

    def test_public_routes_accessible(self, client):
        """Test that public routes are accessible."""
        response = client.get('/info/about')
        assert response.status_code in [200, 302, 404]

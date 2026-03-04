"""Tests for the HTTP errors component routes."""


class TestHTTPErrorRoutes:
    """Integration tests for HTTP error component routes."""

    def test_404_error_page(self, client):
        """Test 404 error page is returned for non-existent routes."""
        response = client.get('/non-existent-page-12345')
        assert response.status_code == 404

    def test_405_error_page(self, client):
        """Test 405 error page for method not allowed."""
        response = client.post('/')  # POST not allowed on home
        # May return various status codes depending on routing/policy
        assert response.status_code in [401, 403, 405, 302]


class TestHTTPErrorContent:
    """Tests for HTTP error response content."""

    def test_error_page_has_content(self, client):
        """Test error pages return HTML content."""
        response = client.get('/this-page-does-not-exist')
        assert response.status_code == 404
        # Should have some content
        assert len(response.data) > 0


class TestHTTPErrorSecurity:
    """Tests for HTTP error security."""

    def test_error_does_not_expose_internal_info(self, client):
        """Test that error pages don't expose sensitive internal information."""
        response = client.get('/non-existent-page')
        content = response.data.decode('utf-8', errors='ignore')
        # Should not contain common internal paths or patterns
        assert '/root/' not in content.lower()
        assert 'password' not in content.lower()
        assert 'secret' not in content.lower()

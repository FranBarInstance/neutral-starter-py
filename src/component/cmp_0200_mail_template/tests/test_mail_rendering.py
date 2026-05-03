"""
Tests for mail template rendering.
Verifies that all mail templates in cmp_0200_mail_template render correctly
with namespaced snippets and proper data injection.
"""

import os
import pytest
from app.config import Config
from core.mail import Mail


def _get_test_mail_data(extra=None):
    """Base mail data with absolute URLs for visual check."""
    data = {
        'to': 'user@example.com',
        'subject': 'Neutral Test Email',
        'url_home': 'https://example.com/',
        'logo': 'https://placehold.co/60x60/375a7f/ffffff?text=NTS',
        'cover': 'https://placehold.co/680x300/375a7f/ffffff?text=Neutral+Cover',
        'brand_text': 'Neutral Starter Py',
        'cover_text': 'Welcome to Neutral',
        'expires': '24',
        'pin': '888999',
        'token': 'test-secure-token-123',
        'alias': 'John Doe'
    }
    if extra:
        data.update(extra)
    return data


def _render_mail_test(flask_app, content_template, test_filename):
    """Helper to render a mail template to a file and perform basic assertions."""
    test_mail_file = f"tmp/mail-html-test/{test_filename}"
    os.makedirs("tmp/mail-html-test", exist_ok=True)

    original_method = Config.MAIL_METHOD
    original_file = Config.MAIL_TO_FILE

    Config.MAIL_METHOD = 'file'
    Config.MAIL_TO_FILE = test_mail_file

    try:
        schema = flask_app.components.schema

        # Simulate dynamic schema population for mail layout
        if 'mail_template' in schema['data']['current']:
            mail_template_dir = schema['data']['current']['mail_template']['dir']
            schema['data']['MAIL_TEMPLATE_LAYOUT'] = os.path.join(
                mail_template_dir, 'layout', Config.MAIL_TEMPLATE_NAME
            )

        mail = Mail(schema)
        mail_data = _get_test_mail_data()

        # Action
        result = mail.send(content_template, mail_data)

        # Verify execution
        assert result['success'] is True
        assert os.path.exists(test_mail_file)

        print(f"\n[VISUAL CHECK] {content_template.upper()} Email: {os.path.abspath(test_mail_file)}")

        # Verify content
        with open(test_mail_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # CRITICAL: Verify snippets were resolved
        # We check for the call tag specifically to allow plain text references
        # which might exist in documentation or sample templates.
        assert "{:snip; mail_template_0yt2sa:" not in content
        assert "{:snip;" not in content
        assert "{:trans;" not in content

        # Basic data check
        if content_template in ['pin', 'account-pin']:
            assert "888999" in content

        return content

    finally:
        Config.MAIL_METHOD = original_method
        Config.MAIL_TO_FILE = original_file


def test_render_all_templates(flask_app):
    """Renders all available mail templates."""
    templates = ['pin', 'account-pin', 'register', 'reminder', 'sample']

    for tpl in templates:
        _render_mail_test(flask_app, tpl, f"test_mail_{tpl}.html")


def test_mail_data_fallback(flask_app):
    """Test that default values work when some data is missing."""
    test_mail_file = "tmp/mail-html-test/test_mail_fallback.html"
    os.makedirs("tmp/mail-html-test", exist_ok=True)

    original_method = Config.MAIL_METHOD
    original_file = Config.MAIL_TO_FILE
    Config.MAIL_METHOD = 'file'
    Config.MAIL_TO_FILE = test_mail_file

    try:
        schema = flask_app.components.schema
        if 'mail_template' in schema['data']['current']:
            mail_template_dir = schema['data']['current']['mail_template']['dir']
            schema['data']['MAIL_TEMPLATE_LAYOUT'] = os.path.join(
                mail_template_dir, 'layout', Config.MAIL_TEMPLATE_NAME
            )

        mail = Mail(schema)

        # Minimal data
        mail_data = {
            'to': 'minimal@example.com',
            'subject': 'Minimal Data Test'
        }

        result = mail.send('pin', mail_data)
        assert result['success'] is True

        with open(test_mail_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Should show fallback brand name (from site schema)
        # Assuming current->site->name is "Neutral"
        assert "PIN ERROR" in content # Because pin was missing
        assert "Neutral" in content

        # CRITICAL: Verify snippets were resolved
        assert "{:snip; mail_template_0yt2sa:" not in content
        assert "{:snip;" not in content
        assert "{:trans;" not in content

    finally:
        Config.MAIL_METHOD = original_method
        Config.MAIL_TO_FILE = original_file

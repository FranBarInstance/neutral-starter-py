"""
Tests for AI Manager.
"""

import sys
import os

from unittest.mock import MagicMock, patch

# Add lib to path
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.abspath(os.path.join(current_dir, "../lib"))
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

# pylint: disable=wrong-import-position
from ai_backend_0yt2sa import AIManager  # pylint: disable=import-error


def test_manager_initialization_empty():
    """Test initializing manager with empty config."""
    manager = AIManager({})
    assert not manager.profiles


@patch("ai_backend_0yt2sa.providers.openai.OpenAI")
def test_manager_profile_init(_):
    """Test initializing manager with a profile."""
    config = {
        "profiles": {
            "my_gpt": {
                "openai": {"enabled": True, "api_key": "sk-test", "model": "gpt-4"}
            }
        }
    }
    manager = AIManager(config)
    assert "my_gpt" in manager.profiles
    assert manager.profiles["my_gpt"].model == "gpt-4"


@patch("ai_backend_0yt2sa.providers.openai.OpenAI")
def test_manager_legacy_init(_):
    """Test initializing manager with legacy config style."""
    # Test support for old simple format
    config = {"openai": {"enabled": True, "api_key": "sk-test", "model": "gpt-3.5"}}
    manager = AIManager(config)
    assert "openai" in manager.profiles
    assert manager.profiles["openai"].model == "gpt-3.5"


@patch("ai_backend_0yt2sa.providers.openai.OpenAI")
def test_openai_generate_profile(mock_openai):
    """Test generating text using an OpenAI profile."""
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello world"
    mock_client.chat.completions.create.return_value = mock_response

    config = {
        "profiles": {
            "smart_bot": {
                "openai": {"enabled": True, "api_key": "sk-test", "model": "gpt-4"}
            }
        }
    }
    manager = AIManager(config)
    result = manager.prompt("smart_bot", "Say hello")
    assert result == "Hello world"
    # Basic verification that correct args were passed
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4"
    assert call_args.kwargs["messages"][0]["content"] == "Say hello"


@patch("ai_backend_0yt2sa.providers.openai.OpenAI")
def test_ollama_generate(mock_openai):
    """Test generating text using an Ollama profile."""
    # Setup mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Ollama says hello"
    mock_client.chat.completions.create.return_value = mock_response

    config = {
        "profiles": {"local_llama": {"ollama": {"enabled": True, "model": "llama3"}}}
    }
    manager = AIManager(config)
    assert "local_llama" in manager.profiles

    result = manager.prompt("local_llama", "Say hello", model="llama2")
    assert result == "Ollama says hello"

    # Verify base URL was passed
    mock_openai.assert_called_with(
        api_key="ollama", base_url="http://localhost:11434/v1"
    )

    # Verify call args
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "llama2"


@patch("ai_backend_0yt2sa.providers.google.genai")
def test_google_generate(mock_genai):
    """Test generating text using Google profile."""
    # Setup mock
    mock_client_cls = mock_genai.Client
    mock_client_instance = MagicMock()
    mock_client_cls.return_value = mock_client_instance

    # Mock models.generate_content
    mock_response = MagicMock()
    mock_response.text = "Gemini says hi"
    mock_client_instance.models.generate_content.return_value = mock_response

    config = {
        "profiles": {
            "gemini_test": {
                "google": {
                    "enabled": True,
                    "api_key": "AIzaTest",
                    "model": "gemini-1.5-pro",
                }
            }
        }
    }
    manager = AIManager(config)
    assert "gemini_test" in manager.profiles

    result = manager.prompt("gemini_test", "Hello Gemini")
    assert result == "Gemini says hi"

    # Verify client init
    mock_client_cls.assert_called_with(api_key="AIzaTest")

    # Verify generate call
    mock_client_instance.models.generate_content.assert_called()
    call_args = mock_client_instance.models.generate_content.call_args
    assert call_args.kwargs["model"] == "gemini-1.5-pro"
    assert call_args.kwargs["contents"] == "Hello Gemini"

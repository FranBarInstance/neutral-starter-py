"""Tests for AI Backend Providers."""

import importlib
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

COMPONENT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = COMPONENT_ROOT.name
OPENAI_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.providers.openai"
ANTHROPIC_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.providers.anthropic"
GOOGLE_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.providers.google"
OLLAMA_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.providers.ollama"


class TestOpenAIProvider:
    """Tests for OpenAIProvider."""

    @pytest.fixture
    def config(self):
        """Sample OpenAI config."""
        return {
            "api_key": "test-openai-key",
            "model": "gpt-4"
        }

    def test_init_without_library(self, config):
        """Test initialization raises ImportError when library not installed."""
        with patch(f"{OPENAI_MODULE}.OpenAI", None):
            OpenAIProvider = importlib.import_module(OPENAI_MODULE).OpenAIProvider

            with pytest.raises(ImportError):
                OpenAIProvider(config)

    def test_init_success(self, config):
        """Test successful initialization."""
        mock_client_class = MagicMock()

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OpenAIProvider = importlib.import_module(OPENAI_MODULE).OpenAIProvider

            provider = OpenAIProvider(config)

            assert provider.api_key == "test-openai-key"
            assert provider.model == "gpt-4"
            mock_client_class.assert_called_once_with(api_key="test-openai-key", base_url=None)

    def test_generate_success(self, config):
        """Test successful text generation."""
        mock_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OpenAIProvider = importlib.import_module(OPENAI_MODULE).OpenAIProvider

            provider = OpenAIProvider(config)
            result = provider.generate("Hello")

            assert result == "Generated text"
            mock_client.chat.completions.create.assert_called_once()

    def test_generate_with_system_prompt(self, config):
        """Test generation with system prompt."""
        mock_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OpenAIProvider = importlib.import_module(OPENAI_MODULE).OpenAIProvider

            provider = OpenAIProvider(config)
            result = provider.generate("Hello", system="You are helpful")

            assert result == "Generated text"
            # Check that system message was added
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args[1]['messages']
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are helpful"

    def test_generate_model_override(self, config):
        """Test generation with model override."""
        mock_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OpenAIProvider = importlib.import_module(OPENAI_MODULE).OpenAIProvider

            provider = OpenAIProvider(config)
            result = provider.generate("Hello", model="gpt-3.5-turbo")

            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == "gpt-3.5-turbo"


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    @pytest.fixture
    def config(self):
        """Sample Anthropic config."""
        return {
            "api_key": "test-anthropic-key",
            "model": "claude-3-opus"
        }

    def test_init_without_library(self, config):
        """Test initialization raises ImportError when library not installed."""
        with patch(f"{ANTHROPIC_MODULE}.anthropic", None):
            AnthropicProvider = importlib.import_module(ANTHROPIC_MODULE).AnthropicProvider

            with pytest.raises(ImportError):
                AnthropicProvider(config)

    def test_generate_success(self, config):
        """Test successful text generation."""
        mock_anthropic_module = MagicMock()
        mock_client = MagicMock()
        mock_anthropic_module.Anthropic.return_value = mock_client

        mock_message = MagicMock()
        mock_content = MagicMock()
        mock_content.text = "Generated text"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        with patch(f"{ANTHROPIC_MODULE}.anthropic", mock_anthropic_module):
            AnthropicProvider = importlib.import_module(ANTHROPIC_MODULE).AnthropicProvider

            provider = AnthropicProvider(config)
            result = provider.generate("Hello")

            assert result == "Generated text"


class TestGoogleProvider:
    """Tests for GoogleProvider."""

    @pytest.fixture
    def config(self):
        """Sample Google config."""
        return {
            "api_key": "test-google-key",
            "model": "gemini-1.5-pro"
        }

    def test_init_without_library(self, config):
        """Test initialization raises ImportError when library not installed."""
        with patch(f"{GOOGLE_MODULE}.genai", None):
            GoogleProvider = importlib.import_module(GOOGLE_MODULE).GoogleProvider

            with pytest.raises(ImportError):
                GoogleProvider(config)

    def test_generate_success(self, config):
        """Test successful text generation."""
        mock_genai = MagicMock()
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = "Generated text"
        mock_client.models.generate_content.return_value = mock_response

        with patch(f"{GOOGLE_MODULE}.genai", mock_genai):
            GoogleProvider = importlib.import_module(GOOGLE_MODULE).GoogleProvider

            provider = GoogleProvider(config)
            result = provider.generate("Hello")

            assert result == "Generated text"


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    @pytest.fixture
    def config(self):
        """Sample Ollama config."""
        return {
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1",
            "model": "llama3"
        }

    def test_init_with_base_url(self, config):
        """Test initialization with base_url."""
        mock_client_class = MagicMock()

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OllamaProvider = importlib.import_module(OLLAMA_MODULE).OllamaProvider

            provider = OllamaProvider(config)

            # Should call OpenAI with the provided base_url
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs['base_url'] == "http://localhost:11434/v1"

    def test_init_defaults(self):
        """Test initialization with default values."""
        config = {}  # Empty config
        mock_client_class = MagicMock()

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OllamaProvider = importlib.import_module(OLLAMA_MODULE).OllamaProvider

            provider = OllamaProvider(config)

            # Should set defaults
            call_kwargs = mock_client_class.call_args[1]
            assert call_kwargs['api_key'] == 'ollama'
            assert call_kwargs['base_url'] == "http://localhost:11434/v1"

    def test_inherits_generate(self, config):
        """Test that OllamaProvider inherits generate from OpenAIProvider."""
        mock_client_class = MagicMock()
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated text"
        mock_client.chat.completions.create.return_value = mock_response

        with patch(f"{OPENAI_MODULE}.OpenAI", mock_client_class):
            OllamaProvider = importlib.import_module(OLLAMA_MODULE).OllamaProvider

            provider = OllamaProvider(config)
            result = provider.generate("Hello")

            assert result == "Generated text"

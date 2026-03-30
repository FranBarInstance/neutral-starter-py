"""Tests for AI Backend Manager."""

import importlib
import json
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch, mock_open

COMPONENT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = COMPONENT_ROOT.name
MANAGER_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.manager"
BASE_PROVIDER_MODULE = f"component.{PACKAGE_NAME}.lib.ai_backend_0yt2sa.providers.base"


class TestAIManager:
    """Tests for AIManager class."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing."""
        return {
            "profiles": {
                "openai_default": {
                    "openai": {
                        "enabled": True,
                        "api_key": "test-openai-key",
                        "model": "gpt-4"
                    }
                },
                "claude_default": {
                    "anthropic": {
                        "enabled": False,
                        "api_key": "test-anthropic-key",
                        "model": "claude-3"
                    }
                },
                "ollama_local": {
                    "ollama": {
                        "enabled": True,
                        "api_key": "ollama",
                        "base_url": "http://localhost:11434/v1",
                        "model": "llama3"
                    }
                }
            }
        }

    @pytest.fixture
    def manager(self, sample_config):
        """Create AIManager instance with mocked providers."""
        with patch(f"{MANAGER_MODULE}.OpenAIProvider") as mock_openai, \
             patch(f"{MANAGER_MODULE}.OllamaProvider") as mock_ollama:

            mock_openai_instance = MagicMock()
            mock_ollama_instance = MagicMock()
            mock_openai.return_value = mock_openai_instance
            mock_ollama.return_value = mock_ollama_instance

            AIManager = importlib.import_module(MANAGER_MODULE).AIManager
            mgr = AIManager(config=sample_config)
            return mgr

    def test_init_with_config(self, sample_config):
        """Test initialization with provided config."""
        with patch(f"{MANAGER_MODULE}.OpenAIProvider") as mock_openai, \
             patch(f"{MANAGER_MODULE}.OllamaProvider") as mock_ollama:

            AIManager = importlib.import_module(MANAGER_MODULE).AIManager
            mgr = AIManager(config=sample_config)

            assert mgr.config == sample_config
            assert 'openai' in mgr.provider_classes
            assert 'anthropic' in mgr.provider_classes
            assert 'google' in mgr.provider_classes
            assert 'ollama' in mgr.provider_classes

    def test_load_profiles_skips_disabled(self, manager):
        """Test that disabled profiles are not loaded."""
        # Claude profile is disabled, should not be in profiles
        assert 'claude_default' not in manager.profiles

    def test_load_profiles_includes_enabled(self, manager):
        """Test that enabled profiles are loaded."""
        # OpenAI and Ollama are enabled
        assert 'openai_default' in manager.profiles
        assert 'ollama_local' in manager.profiles

    def test_get_provider_instance_existing(self, manager):
        """Test getting an existing provider instance."""
        provider = manager.get_provider_instance('openai_default')
        assert provider is not None

    def test_get_provider_instance_nonexistent(self, manager):
        """Test getting a non-existent provider instance."""
        provider = manager.get_provider_instance('nonexistent')
        assert provider is None

    def test_prompt_success(self, manager):
        """Test successful prompt execution."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "Test response"
        manager.profiles['test_profile'] = mock_provider

        result = manager.prompt('test_profile', 'Hello')

        assert result == "Test response"
        mock_provider.generate.assert_called_once_with('Hello')

    def test_prompt_profile_not_found(self, manager):
        """Test prompt with non-existent profile raises error."""
        with pytest.raises(ValueError) as exc_info:
            manager.prompt('nonexistent', 'Hello')

        assert "Profile 'nonexistent' not available" in str(exc_info.value)

    def test_merge_dicts_simple(self, manager):
        """Test simple dictionary merge."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = manager._merge_dicts(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_dicts_nested(self, manager):
        """Test nested dictionary merge."""
        base = {"profile": {"key1": "value1", "key2": "value2"}}
        override = {"profile": {"key2": "overridden"}}
        result = manager._merge_dicts(base, override)

        assert result["profile"]["key1"] == "value1"
        assert result["profile"]["key2"] == "overridden"

    @patch('builtins.open', mock_open(read_data='{"config": {"profiles": {}}}'))
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_config_from_manifest(self, mock_exists):
        """Test loading config from manifest file."""
        AIManager = importlib.import_module(MANAGER_MODULE).AIManager

        with patch(f"{MANAGER_MODULE}.OllamaProvider"):
            mgr = AIManager()

        assert isinstance(mgr.config, dict)

    def test_load_legacy_config(self):
        """Test loading legacy config format."""
        legacy_config = {
            "openai": {
                "enabled": True,
                "api_key": "test-key",
                "model": "gpt-4"
            }
        }

        with patch(f"{MANAGER_MODULE}.OpenAIProvider") as mock_openai:
            mock_instance = MagicMock()
            mock_openai.return_value = mock_instance

            AIManager = importlib.import_module(MANAGER_MODULE).AIManager
            mgr = AIManager(config=legacy_config)

        assert 'openai' in mgr.profiles


class TestBaseProvider:
    """Tests for BaseProvider abstract class."""

    def test_base_provider_init(self):
        """Test BaseProvider initialization."""
        BaseProvider = importlib.import_module(BASE_PROVIDER_MODULE).BaseProvider

        # Create a concrete implementation for testing
        class TestProvider(BaseProvider):
            def generate(self, prompt, **kwargs):
                return "test"

        config = {"api_key": "test-key", "model": "test-model"}
        provider = TestProvider(config)

        assert provider.api_key == "test-key"
        assert provider.model == "test-model"

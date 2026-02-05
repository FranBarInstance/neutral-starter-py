"""
Ollama Provider module.
"""
from .openai import OpenAIProvider

class OllamaProvider(OpenAIProvider):
    """Ollama API Provider (OpenAI Compatible)."""
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        # Create a copy to avoid side effects
        ollama_config = config.copy()

        # Defaults
        if not ollama_config.get('api_key'):
            ollama_config['api_key'] = 'ollama'

        if not ollama_config.get('base_url'):
            ollama_config['base_url'] = "http://localhost:11434/v1"

        # Call parent with augmented config
        super().__init__(ollama_config)

        # Inherit generate from OpenAIProvider

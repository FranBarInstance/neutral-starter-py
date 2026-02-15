"""
Base provider module.
"""
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Abstract base class for AI providers."""
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model')

    @abstractmethod
    def generate(self, prompt, **kwargs):
        """
        Generate text from a prompt.
        :param prompt: The user prompt.
        :param kwargs: Additional arguments (model, system, etc.)
        :return: Generated text as string.
        """

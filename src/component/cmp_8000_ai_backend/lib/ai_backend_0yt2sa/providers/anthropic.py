"""
Anthropic Provider module.
"""
try:
    import anthropic
except ImportError:
    anthropic = None

from .base import BaseProvider

class AnthropicProvider(BaseProvider):
    """Anthropic API Provider."""
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        super().__init__(config)
        if anthropic is None:
            raise ImportError(
                "Anthropic library not installed. Please install 'anthropic' package."
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt, **kwargs):
        model = kwargs.get('model', self.model)

        system = kwargs.get('system', "")

        # Anthropic messages API
        call_kwargs = {
            k: v for k, v in kwargs.items()
            if k not in ['model', 'system', 'api_key']
        }

        # Default max_tokens if not provided
        if 'max_tokens' not in call_kwargs:
            call_kwargs['max_tokens'] = 1024

        message = self.client.messages.create(
            model=model,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **call_kwargs
        )
        return message.content[0].text

"""
OpenAI Provider module.
"""
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    """OpenAI API Provider."""
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        super().__init__(config)
        if OpenAI is None:
            raise ImportError("OpenAI library not installed. Please install 'openai' package.")
        base_url = config.get('base_url')
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def generate(self, prompt, **kwargs):
        # Allow overriding model per request
        model = kwargs.get('model', self.model)

        messages = [{"role": "user", "content": prompt}]
        if 'system' in kwargs:
            messages.insert(0, {"role": "system", "content": kwargs['system']})

        # Filter kwargs to only pass valid parameters
        call_kwargs = {k: v for k, v in kwargs.items() if k not in ['model', 'system']}

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **call_kwargs
        )
        return response.choices[0].message.content

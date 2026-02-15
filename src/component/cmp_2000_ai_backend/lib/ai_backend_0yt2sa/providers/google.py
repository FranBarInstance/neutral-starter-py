"""
Google Provider module.
"""
try:
    from google import genai
except ImportError:
    genai = None

from .base import BaseProvider

class GoogleProvider(BaseProvider):
    """Google Gemini Provider using google-genai SDK."""
    # pylint: disable=too-few-public-methods
    def __init__(self, config):
        super().__init__(config)
        if genai is None:
            raise ImportError(
                "Google GenAI library ('google-genai') not installed."
            )
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, prompt, **kwargs):
        model_name = kwargs.get('model', self.model)

        # Map configuration
        config_args = {}
        for key in ['temperature', 'top_p', 'top_k', 'max_output_tokens']:
            if key in kwargs:
                config_args[key] = kwargs[key]

        if 'system' in kwargs:
            config_args['system_instruction'] = kwargs['system']

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_args if config_args else None
        )
        return response.text

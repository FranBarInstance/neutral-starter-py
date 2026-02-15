"""
AI Manager module.
Handles initialization and access to multiple AI providers.
"""
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .providers.google import GoogleProvider
from .providers.ollama import OllamaProvider

class AIManager:
    """
    Manager to handle Main AI providers interactions.
    """
    def __init__(self, config=None):
        self.config = config or {}
        # Stores provider instances keyed by profile name
        self.profiles = {}
        # Mapping available provider keys to classes
        self.provider_classes = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'google': GoogleProvider,
            'ollama': OllamaProvider
        }
        self._load_profiles()

    def _load_profiles(self):
        """
        Load profiles from config.
        Expected config structure:
        {
            "profiles": {
                "profile_name": {
                    "provider_type": { ... config ... }
                }
            }
        }
        """
        # Look for 'profiles' key, fallbacks for backward compat if necessary,
        # but focusing on new requirement.
        profiles_config = self.config.get('profiles', {})

        # If no profiles found, check if it's the old format
        # (direct provider keys under ai_models or root)
        # This preserves backward compatibility for tests or simple configs
        if not profiles_config and (
            'ai_models' in self.config or any(k in self.config for k in self.provider_classes)
        ):
            self._load_legacy_config()
            return

        for profile_name, profile_data in profiles_config.items():
            # profile_data should contain { "provider_type": { ... } }
            for provider_type, provider_config in profile_data.items():
                if provider_type in self.provider_classes:
                    if provider_config.get('enabled') is False:
                        continue

                    # Cloud providers require an API key
                    if provider_type != 'ollama' and not provider_config.get('api_key'):
                        continue

                    provider_class = self.provider_classes[provider_type]
                    try:
                        # Instantiate provider
                        instance = provider_class(provider_config)
                        self.profiles[profile_name] = instance
                        break  # Assume one provider per profile
                    except ImportError as e:
                        print(
                            f"Warning: Profile '{profile_name}' ({provider_type}) disabled. {e}"
                        )
                    # pylint: disable=broad-except
                    except Exception as e:
                        print(f"Error initializing profile '{profile_name}': {e}")

    def _load_legacy_config(self):
        """Load providers using the old structure (directly named after provider type)."""
        ai_config = self.config.get('ai_models', self.config)

        for name, cls in self.provider_classes.items():
            conf = ai_config.get(name)
            if conf and conf.get('enabled') and (conf.get('api_key') or name == 'ollama'):
                try:
                    self.profiles[name] = cls(conf)
                except ImportError:

                    print(
                        f"Warning: Provider '{name}' could not be loaded"
                        " due to missing dependencies."
                    )


    def get_provider_instance(self, profile_name):
        """Get a provider instance by profile name."""
        return self.profiles.get(profile_name)

    def prompt(self, profile_name, prompt_text, **kwargs):
        """
        Send a prompt to the specified profile.

        :param profile_name: Name of the profile (e.g., 'openai_default', 'my_custom_gpt')
        :param prompt_text: The prompt content
        :param kwargs: Additional arguments (model, max_tokens, etc.)
        :return: The generated text
        """
        provider = self.get_provider_instance(profile_name)
        if not provider:
            available = list(self.profiles.keys())
            raise ValueError(
                f"Profile '{profile_name}' not available. Configured profiles: {available}"
            )

        return provider.generate(prompt_text, **kwargs)

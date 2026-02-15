# AI Models Library Backend (ai_backend_0yt2sa)

This component provides a unified backend interface to interact with multiple AI model providers, including OpenAI, Anthropic (Claude), Google (Gemini), and Ollama (Local).

It abstracts the specific API details of each provider, allowing you to switch between models or providers using a simple usage profile system.

## Features

*   **Unified API**: Single interface (`prompt`) for all providers.
*   **Profile System**: Define multiple configurations (profiles) for different use cases (e.g., `openai_default`, `local_debugging`, `production_gpt4`).
*   **Multiple Providers**:
    *   **OpenAI**: Supports GPT-4, GPT-3.5, etc.
    *   **Anthropic**: Supports Claude 3 Opus, Sonnet, Haiku, etc.
    *   **Google**: Supports Gemini 1.5 Pro, Flash, etc.
    *   **Ollama**: Supports local models like Llama 3 (via OpenAI-compatible API).
*   **Resilient Configuration**: Configure via `manifest.json` (defaults) or `custom.json` (user overrides).

## Configuration

The configuration is structured around **Profiles**. Each profile maps to a specific provider and its settings.

### Default Configuration (`manifest.json`)
```json
"config": {
    "profiles": {
        "openai_default": {
            "openai": {
                "enabled": true,
                "api_key": "YOUR_KEY",
                "model": "gpt-4-turbo"
            }
        },
        "ollama_local": {
            "ollama": {
                "enabled": true,
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1",
                "model": "llama3"
            }
        }
    }
}
```

### User Overrides (`custom.json`)
To add your keys or change models locally without modifying the component code, create/edit `custom.json` in the component root:

```json
{
    "manifest": {
        "config": {
            "profiles": {
                "openai_default": {
                    "openai": {
                        "api_key": "sk-real-secret-key-...",
                        "model": "gpt-4o"
                    }
                }
            }
        }
    }
}
```

## Usage

This component exposes a Python library.

### 1. Import
The library module is named `ai_backend_0yt2sa`.

```python
from ai_backend_0yt2sa.manager import AIManager
```

### 2. Initialization
You typically initialize it with the component configuration.

```python
# In a Neutral component context
def init_component(component, component_schema, _schema):
    # The config is merged and available in component['config'] or similar
    # depending on how you load it.
    # Usually you extract the 'profiles' part.

    config = component.get('manifest', {}).get('config', {})
    ai_manager = AIManager(config)
```

### 3. Generative AI
Use the `prompt` method with a profile name.

```python
try:
    response = ai_manager.prompt('openai_default', 'Explain quantum computing in one sentence.')
    print(response)
except ValueError as e:
    print(f"Profile error: {e}")
```

## Supported Providers

| Provider | Key | Required Fields | Notes |
| :--- | :--- | :--- | :--- |
| **OpenAI** | `openai` | `api_key` | Supports `base_url` for proxies. |
| **Anthropic** | `anthropic` | `api_key` | |
| **Google** | `google` | `api_key` | Uses `google-generativeai`. |
| **Ollama** | `ollama` | `enabled` | Defaults to `http://localhost:11434/v1`. |

## Requirements
See `requirements.txt` in the project root.
*   `openai`
*   `anthropic`
*   `google-generativeai`

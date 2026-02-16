# cmp_6000_aichat

AI chat component integrated with `ai_backend_0yt2sa`.

## Current Security Status

Implemented:

- Session gating in UI using `HAS_SESSION`.
- Session enforcement in API endpoints (`/api/chat`, `/api/profiles`).
- Rate limiting for critical API endpoints:
  - `/api/chat` using `config.chat_api_limits`
  - `/api/profiles` using `config.profiles_api_limits`
- Generic HTTP 500 responses without internal exception leakage.
- Generic HTTP 400 for invalid chat requests without leaking provider details.
- Markdown rendering with HTML sanitization to reduce XSS risk.
- Automated tests for:
  - Unauthorized access (`401`) when session is missing.
  - Input validation (`400`) for malformed payloads.
  - Throttling behavior (`429`) on API endpoints.
  - Generic `500` error behavior without leaking exception details.

## Configuration

Configure limits in `manifest.json` under `"config"`:

- `chat_api_limits` (default: `"20 per minute"`)
- `profiles_api_limits` (default: `"60 per minute"`)

## Customization (`custom.json`)

For local overrides without modifying component source files, create:

- `src/component/cmp_6000_aichat/custom.json`

At load time, values under `custom.json -> manifest` override `manifest.json`.
Use this to customize route metadata and runtime config (`default_profile`, limits, prompts, etc.).

Example:

```json
{
    "schema": {},
    "manifest": {
        "route": "/assistant",
        "config": {
            "default_profile": "openai_default",
            "chat_api_limits": "10 per minute",
            "profiles_api_limits": "30 per minute",
            "prompts": [
                {
                    "id": "support",
                    "name": "Support Assistant",
                    "prompt": "Help me solve this issue step by step."
                },
                {
                    "id": "translator_en",
                    "name": "Translator to English",
                    "prompt": "Translate the text to English"
                }
            ]
        }
    }
}
```

Notes:

- `custom.json` is intended for local/project-specific customization.
- Do not distribute this file as part of the base component package.

## Production Note (Rate Limiting Storage)

Rate limiting depends on Flask-Limiter storage configuration (`LIMITER_STORAGE_URI`).

- Development/default example:
  - `LIMITER_STORAGE_URI=memory://`
- Production:
  - Use a shared backend (for example Redis), not `memory://`.
  - `memory://` only works reliably in single-process Flask development and does not share counters across workers/instances.

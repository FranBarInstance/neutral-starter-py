# Configuration

This directory contains environment-based configuration for the app.

## Files

- `.env.example`: template with all available environment variables.
- `.env`: your local runtime configuration (not committed).

## Quick Start

1. Create `.env` from the template:

```bash
cp .env.example .env
```

2. Set at minimum:
- `SECRET_KEY`
- `SITE_DOMAIN`
- `SITE_URL`
- `ALLOWED_HOSTS`

3. Adjust DB, mail, rate limits, and CSP to your environment.

## Notes

- List variables use comma separator: `value1,value2,value3`.
- `ALLOWED_HOSTS` supports wildcard patterns (for example: `*.example.com`).
- Empty values in `.env.example` are either optional or use code defaults in `src/app/config.py`.

## Variables

### Debug

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_FILE` | Path of the "debug switch" file. Debug mode is enabled only while this file exists and is fresh. | empty |
| `DEBUG_EXPIRE` | Max age (seconds) since the last modification time of `DEBUG_FILE`. `0` (or invalid) means debug stays disabled. | `0` |
| `WSGI_DEBUG_ALLOWED` | Second gate for WSGI entrypoints (`wsgi.py`, `wsgi_test.py`). Must be `true` in addition to other debug checks. | `false` |

Debug activation rules:

1. `FLASK_DEBUG` must be enabled (`true`, `1`, or `yes`).
2. `DEBUG_FILE` must point to an existing file.
3. `DEBUG_EXPIRE` must be a number greater than `0`.
4. The file modification time must be recent enough: `now - mtime <= DEBUG_EXPIRE`.
5. For WSGI entrypoints (`wsgi.py`, `wsgi_test.py`), `WSGI_DEBUG_ALLOWED=true` is also required.

If any check fails, debug is disabled.

Example `.env` for local development:

```env
FLASK_DEBUG=true
DEBUG_FILE=/tmp/enable-neutral-debug-<random-suffix>
DEBUG_EXPIRE=120
WSGI_DEBUG_ALLOWED=true
```

Development workflow example (refresh window):

```bash
touch /tmp/enable-neutral-debug-<random-suffix>
```

Use that same path in `DEBUG_FILE`.
The `<random-suffix>` part should be random (do not use a fixed/public name), which reduces accidental discovery.
The file can be empty; only its modification time is used.
To keep debug active in development, run `touch` periodically before `DEBUG_EXPIRE` is reached.

### Security / Site

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Secret used by app tokens/cookies. Must be strong in production. | none |
| `SITE_DOMAIN` | Canonical fallback host. | `localhost` |
| `SITE_URL` | Canonical fallback URL. | `http://localhost` |
| `ALLOWED_HOSTS` | Allowed request hosts, comma separated, wildcard supported. | `SITE_DOMAIN` |
| `TRUSTED_PROXY_CIDRS` | Trusted proxy IP/CIDR list for client IP extraction. | empty |

Example:

```env
ALLOWED_HOSTS=localhost,*.example.com,my-other-domain.org
TRUSTED_PROXY_CIDRS=127.0.0.1/32,::1/128,10.0.0.0/8
```

### Neutral Runtime

| Variable | Description | Default |
|----------|-------------|---------|
| `NEUTRAL_IPC` | Enable Neutral IPC mode. | `false` |
| `NEUTRAL_CACHE_DISABLE` | Disable Neutral cache. | `false` |

### Templates / Static

| Variable | Description | Default |
|----------|-------------|---------|
| `TEMPLATE_NAME` | Main layout filename. | `index.ntpl` |
| `TEMPLATE_NAME_ERROR` | Error layout filename. | `error.ntpl` |
| `TEMPLATE_HTML_MINIFY` | Minify rendered HTML output. | `false` |
| `STATIC_CACHE_CONTROL` | Cache-Control header for static responses. | `max-age=14400` |

### Rate Limiting

| Variable | Description | Default |
|----------|-------------|---------|
| `LIMITER_STORAGE_URI` | Flask-Limiter backend (`memory://`, `redis://`, etc.). | `memory://` |
| `DEFAULT_LIMITS` | Global default request limit. | `3600/hour` |
| `STATIC_LIMITS` | Limit for static endpoints. | `7200/hour` |
| `SIGNIN_LIMITS` | Limit for sign-in form POST. | `3 per 30 minutes` |
| `SIGNUP_LIMITS` | Limit for sign-up form POST. | `5 per 30 minutes` |
| `SIGNREMINDER_LIMITS` | Limit for reminder form POST. | `5 per 30 minutes` |
| `SIGNT_LIMITS` | Limit for pin/token form POST. | `5 per 30 minutes` |

Important note:

- `memory://` is development-only and must not be used in production.
- In production, you must set `LIMITER_STORAGE_URI` to a shared backend (for example `redis://...`, `memcached://...`, or `mongodb://...`).
- Treat `memory://` as invalid production configuration.

### User / Session / Token

| Variable | Description | Default |
|----------|-------------|---------|
| `VALIDATE_SIGNUP` | Keep signup accounts unvalidated until confirmation flow finishes. | `true` |
| `SESSION_TOKEN_LENGTH` | Session token entropy length for token generation. | `32` |
| `SESSION_IDLE_EXPIRES_SECONDS` | Session idle timeout in seconds. | `2592000` |
| `UTOKEN_IDLE_EXPIRES_SECONDS` | User-security token idle timeout in seconds. | `14400` |
| `FTOKEN_EXPIRES_SECONDS` | Form token expiration in seconds. | `240` |
| `PIN_EXPIRES_SECONDS` | PIN expiration in seconds. | `86400` |
| `TOKEN_LENGTH` | Generic token generation length. | `32` |
| `PIN_MIN` | Minimum PIN numeric value. | `100000` |
| `PIN_MAX` | Maximum PIN numeric value. | `999999` |
| `UUID_MIN` | Lower bound for generated numeric IDs. | `1000000000000` |
| `UUID_MAX` | Upper bound for generated numeric IDs. | `9999999999999` |

### Mail

| Variable | Description | Default |
|----------|-------------|---------|
| `MAIL_METHOD` | Mail backend: `smtp`, `sendmail`, `file`. | `smtp` |
| `MAIL_TO_FILE` | File path used when `MAIL_METHOD=file`. | `/tmp/test_mail.html` |
| `MAIL_SERVER` | SMTP server hostname. | empty |
| `MAIL_PORT` | SMTP server port. | `587` |
| `MAIL_USE_TLS` | Enable STARTTLS for SMTP. | `false` |
| `MAIL_USERNAME` | SMTP username. | empty |
| `MAIL_PASSWORD` | SMTP password. | empty |
| `MAIL_SENDER` | Default sender address. | empty |
| `MAIL_RETURN_PATH` | Return path/envelope sender. | empty |

### Database - PWA

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PWA_TYPE` | DB engine: `sqlite`, `postgresql`, `mysql`, etc. | `sqlite` |
| `DB_PWA_NAME` | Database name / sqlite file name. | `pwa.db` |
| `DB_PWA_USER` | DB username. | empty |
| `DB_PWA_PASSWORD` | DB password. | empty |
| `DB_PWA_HOST` | DB host. | `localhost` |
| `DB_PWA_PORT` | DB port. | empty |
| `DB_PWA_PATH` | SQLite folder path (used when sqlite). | `../storage` |

### Database - Safe

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_SAFE_TYPE` | DB engine. | `sqlite` |
| `DB_SAFE_NAME` | Database name / sqlite file name. | `safe.db` |
| `DB_SAFE_USER` | DB username. | empty |
| `DB_SAFE_PASSWORD` | DB password. | empty |
| `DB_SAFE_HOST` | DB host. | `localhost` |
| `DB_SAFE_PORT` | DB port. | empty |
| `DB_SAFE_PATH` | SQLite folder path (used when sqlite). | `../storage` |

### Database - Files

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_FILES_TYPE` | DB engine. | `sqlite` |
| `DB_FILES_NAME` | Database name / sqlite file name. | `files.db` |
| `DB_FILES_USER` | DB username. | empty |
| `DB_FILES_PASSWORD` | DB password. | empty |
| `DB_FILES_HOST` | DB host. | `localhost` |
| `DB_FILES_PORT` | DB port. | empty |
| `DB_FILES_PATH` | SQLite folder path (used when sqlite). | `../storage` |

### Content Security Policy (CSP)

| Variable | Description | Default |
|----------|-------------|---------|
| `CSP_ALLOWED_SCRIPT` | Allowed script sources. | `https://cdnjs.cloudflare.com` |
| `CSP_ALLOWED_STYLE` | Allowed style sources. | `https://cdnjs.cloudflare.com,https://fonts.googleapis.com` |
| `CSP_ALLOWED_IMG` | Allowed image sources. | `https://picsum.photos,https://fastly.picsum.photos` |
| `CSP_ALLOWED_FONT` | Allowed font sources. | `https://cdnjs.cloudflare.com,https://fonts.gstatic.com` |
| `CSP_ALLOWED_CONNECT` | Allowed fetch/XHR/WebSocket sources. | `https://cdnjs.cloudflare.com,https://picsum.photos,https://fastly.picsum.photos` |
| `CSP_ALLOWED_FRAME` | Allowed iframe/frame sources. | empty |
| `CSP_ALLOWED_SCRIPT_UNSAFE_INLINE` | Allow `'unsafe-inline'` for scripts (weakens security). | `false` |
| `CSP_ALLOWED_SCRIPT_UNSAFE_EVAL` | Allow `'unsafe-eval'` for scripts (weakens security). | `false` |
| `CSP_ALLOWED_STYLE_UNSAFE_INLINE` | Allow `'unsafe-inline'` for styles (weakens security). | `false` |

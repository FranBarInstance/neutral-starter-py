# Neutral TS Starter Py

**Neutral TS Starter Py** is a modular, opinionated starter kit for building Progressive Web Applications (PWA) using **Python (Flask)** on the backend and **[Neutral TS](https://github.com/FranBarInstance/neutralts)** as a universal templating engine.

This project is designed to be extensible via a "plug-and-play" component architecture, allowing scalability from quick prototypes to complex applications while maintaining a clean and decoupled structure.

## Project Status

This starter is in active development.

- Stable base: component loading, routing, template rendering, security headers, auth/session foundations.
- Ongoing work: broader edge-case test coverage and hardening of optional modules for production use.

## Features

*   **Flask application factory** with component-driven routing and blueprint registration.
*   **Modular component architecture** in `src/component` (manifest, schema, routes, templates, static assets).
*   **Neutral TS templating (NTPL)** with snippet composition and schema-driven data.
*   **Override model** using `custom.json` for local, per-component customization.
*   **Security defaults**: CSP, host allow-list validation, trusted proxy header guard, and security headers.
*   **Abuse protection**: form/session token flows and request rate limiting via Flask-Limiter.
*   **PWA support**: service worker, offline page, and web manifest component.
*   **Internationalization (i18n)** through component locale files (`locale-*.json`).
*   **Multiple data backends** configured from environment (SQLite by default).
*   **Automated tests** for app bootstrap and component behavior (`pytest`).

## Application Architecture

The project uses a layered architecture with clear responsibilities:

### 1. Presentation
- NTPL templates, component CSS/JS, and static assets.

### 2. Application Logic
- Component routes/controllers plus request guards (security headers, host/proxy checks, access rules).

### 3. Data
- JSON-backed models in `src/model/` and DB connectivity configured from `src/app/config.py`.

### 4. Services
- Shared utilities, environment/config loading, and i18n locale resolution.

### Request Flow

```
HTTP Client
    ↓
Security + Host/Proxy Guards
    ↓
Flask Router + Component Blueprint
    ↓
Component Route/Dispatcher
    ↓
Model/DB Access
    ↓
NTPL Render
    ↓
HTTP Response
```

## Prerequisites

*   Python 3.10 or higher.
*   pip (Python package manager).
*   Recommended: Virtual environment (`venv`).

## Quick Start

### 1. Clone and Configure Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Linux/Mac)
source .venv/bin/activate

# Activate environment (Windows)
.venv\Scripts\activate
```

### 2. Create Runtime Configuration

```bash
cp config/.env.example config/.env
```

At minimum, set a strong value for `SECRET_KEY` in `config/.env`.

### 3. Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run in Development with Debugging

```bash
source .venv/bin/activate

# Optional debug guard (enabled only when all conditions are met)
# 1) set DEBUG_EXPIRE and DEBUG_FILE in config/.env
#    e.g. DEBUG_EXPIRE=3600 and DEBUG_FILE=/tmp/neutral-debug.flag
export FLASK_DEBUG=1
touch /tmp/neutral-debug.flag

python src/run.py
```

The application will be available at `http://localhost:5000` (by default).

## Project Structure

```
neutral-starter-py/
├── src/
│   ├── app/                     # Flask application factory and core configuration
│   ├── component/               # MODULE COLLECTION (The most important part)
│   │   ├── cmp_7000_hellocomp/  # Example of a full component
│   │   └── ...                  # Other components (cmp_0100_*, cmp_0200_*, etc.)
│   ├── core/                    # Core utilities (dispatcher, helpers)
│   ├── model/                   # Data models
│   ├── neutral/                 # Template engine core
│   ├── utils/                   # Utility modules
│   ├── run.py                   # Execution script for development
│   └── wsgi.py                  # Entry point for production (Gunicorn/uWSGI)
├── config/                      # General configuration files
├── docs/                        # Project documentation
├── public/                      # Public static files
└── storage/                     # Storage directory for runtime data
```

## Component Architecture

The strength of this starter lies in `src/component`. Each folder there is a self-sufficient module.

### Basic Rules
1.  **Prefix**: Components must start with `cmp_` (e.g., `cmp_5000_login`).
2.  **Order**: They load alphabetically. `cmp_5005` will override `cmp_5000` if there are conflicts.
3.  **Content**: A component can have:
    *   `manifest.json`: Metadata and base path.
    *   `schema.json`: Configuration and customization settings.
    *   `route/`: Python logic (Flask Blueprints).
    *   `neutral/`: HTML templates and snippets.
    *   `static/`: Specific assets (JS/CSS).
    *   `__init__.py`: Component initialization.

Folders that do not start with `cmp_` are skipped by the loader. This is used for disabled/optional components (for example `_cmp_*`).

### Component Structure

Each component follows this structure:

```
cmp_component_name/
├── manifest.json      # Component metadata
├── schema.json        # Configuration and customization
├── route/             # Component-specific routes
│   ├── __init__.py
│   └── routes.py
├── neutral/           # Component templates
│   ├── component-init.ntpl
│   └── route/
│       └── root/
│           └── content-snippets.ntpl
├── static/            # Component static resources
│   ├── component.css
│   └── component.js
└── __init__.py        # Component initialization
```

For a detailed example, see the [Hello Component README](src/component/cmp_7000_hellocomp/README.md). For complete technical documentation on the component architecture, refer to [docs/component.md](docs/component.md).

## Configuration

Configuration is handled in layers:
1.  **Global**: Environment variables and Flask configuration.
2.  **Per Component**: `schema.json` within each component.
3.  **Customization**: `custom.json` allows overriding local configurations without affecting the codebase. It is ignored by git by default, with explicit repository exceptions such as the example `hellocomp` component.

Boolean environment variables follow a strict rule: **only** `true` (case-insensitive) enables the flag. Any other value (`false`, `0`, `no`, empty, typo) is treated as `False`.

## Security & CSP

The application implements a strict **Content Security Policy (CSP)**. By default, external resources are blocked unless explicitly allowed in the configuration.

In addition to CSP, production deployments should explicitly configure host and proxy trust boundaries:

```ini
# Allowed request hosts (comma separated, wildcard supported)
# Example: localhost,*.example.com,my-other-domain.org
ALLOWED_HOSTS=localhost

# Trusted reverse proxy CIDRs (comma separated)
# Example: 127.0.0.1/32,::1/128,10.0.0.0/8
TRUSTED_PROXY_CIDRS=
```

`ALLOWED_HOSTS` is enforced on every request. Requests with a Host header outside this allow-list are rejected with `400`.
`TRUSTED_PROXY_CIDRS` defines which upstream proxies are allowed to supply forwarded headers. If a request does not come from a trusted proxy, forwarded headers are stripped before Flask processes the request.

To ensure the core theme and components work correctly, you **must** whitelist the necessary CDNs in your `config/.env` file:

```ini
# Referrer policy (SEO-friendly: cross-site requests receive only origin, not path)
REFERRER_POLICY=strict-origin-when-cross-origin

# Permissions-Policy (optional). Empty = do not send header (current behavior)
# Example: geolocation=(), microphone=(), camera=(), payment=()
PERMISSIONS_POLICY=

# Security Content-Security-Policy (CSP) allowed domains
CSP_ALLOWED_SCRIPT=https://cdnjs.cloudflare.com
CSP_ALLOWED_STYLE=https://cdnjs.cloudflare.com,https://fonts.googleapis.com
CSP_ALLOWED_IMG=https://picsum.photos,https://fastly.picsum.photos
CSP_ALLOWED_FONT=https://cdnjs.cloudflare.com,https://fonts.gstatic.com
CSP_ALLOWED_CONNECT=https://cdnjs.cloudflare.com,https://picsum.photos,https://fastly.picsum.photos
CSP_ALLOWED_FRAME=

# Security Content-Security-Policy (CSP) unsafe directives
CSP_ALLOWED_SCRIPT_UNSAFE_INLINE=false
CSP_ALLOWED_SCRIPT_UNSAFE_EVAL=false
CSP_ALLOWED_STYLE_UNSAFE_INLINE=false
```

`REFERRER_POLICY` is configurable. The default (`strict-origin-when-cross-origin`) keeps path/query for same-origin navigation but sends only origin on cross-origin HTTPS requests.
`PERMISSIONS_POLICY` is optional and empty by default, so the header is not sent unless you explicitly define a policy.

If you add new external resources (JS, CSS, fonts), remember to update these variables to avoid console errors and broken layouts.

> [!TIP]
> **Flexibility vs. Security**: If you prefer to allow all external sources for a specific resource type (common in development or less critical production sites), you can use the wildcard `*`.
> For example: `CSP_ALLOWED_STYLE=*` will allow CSS from any domain. While this is less secure, it provides maximum compatibility and ease of use.

## Internationalization

The application provides comprehensive internationalization (i18n) support:

- **Multi-language Support**: Configurable per component
- **Translation Files**: JSON format in component `neutral/route/locale-*.json` files
- **Automatic Detection**: Based on browser headers or user preferences
- **Language Switching**: Built-in language selection mechanism

Components can define their own translations in `neutral/route/locale-{lang}.json` files, where `{lang}` is the language code (e.g., `en`, `es`, `fr`, `de`).

## Deployment

For production, use a WSGI server like Gunicorn pointing to `src/wsgi.py`:

```bash
source .venv/bin/activate
gunicorn --chdir src wsgi:application
```

Notes:

*   Keep `FLASK_DEBUG` disabled in production.
*   Configure `SECRET_KEY`, `SITE_DOMAIN`, `SITE_URL`, `ALLOWED_HOSTS`, and trusted proxy CIDRs in `config/.env`.
*   For distributed deployments, configure a shared rate-limit backend (for example Redis) instead of `memory://`.

## Testing

Run test suite:

```bash
source .venv/bin/activate
pytest -q
```

Component tests are located under each component folder in `src/component/*/tests/`, with shared fixtures in `src/component/conftest.py`.

Test scope evolves with the component set. Use the repository as source of truth (`src/component/*/tests/` and `tests/`), rather than a fixed list in this README.

Tests resolve blueprint names from the component directory at runtime (`bp_{component_folder}`), so they remain valid if a component changes numeric prefix (for example `cmp_1200_backtotop` to `cmp_1300_backtotop`).

## Documentation

For more detailed documentation, see the `docs/` directory:
*   `docs/component.md`: Complete guide on component architecture and creation.

Neutral TS template engine
--------------------------

- [Rust docs](https://docs.rs/neutralts/latest/neutralts/)
- [Template docs](https://franbarinstance.github.io/neutralts-docs/docs/neutralts/doc/)
- [IPC server](https://github.com/FranBarInstance/neutral-ipc/releases)
- [IPC clients](https://github.com/FranBarInstance/neutral-ipc/tree/master/clients)
- [Repository](https://github.com/FranBarInstance/neutralts)
- [Crate](https://crates.io/crates/neutralts)
- [PYPI Package](https://pypi.org/project/neutraltemplate/)
- [Examples](https://github.com/FranBarInstance/neutralts-docs/tree/master/examples)

## License

See the [LICENSE](LICENSE) file for details.

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
*   **Override model** using `custom.json` and optional `config/config.db` (`custom` table) for per-component customization.
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

*   Python 3.10 to 3.14.
*   pip (Python package manager).
*   Recommended: Virtual environment (`venv`).

## Quick Start

### 1. Automatic Installer (recommended)

The project includes interactive installers:

- `bin/install.sh` for Linux/macOS
- `bin/install.ps1` for Windows PowerShell

Installer features:

- Fetches repository tags and lets you choose from the latest 15 versions.
- Asks for installation directory (current directory by default).
- Creates `.venv` and installs dependencies.
- Copies `config/.env.example` to `config/.env`.
- Generates a random `SECRET_KEY`.
- Generates randomized admin routes in:
  - `src/component/cmp_7040_admin/custom.json` as `/admin-[random]`
  - `src/component/cmp_7050_dev_admin/custom.json` as `/dev-admin-[random]`
- Randomized admin routes are generated during installation as an extra hardening measure against automated scraping/scanning of default admin URLs. This is not security by itself; core protection remains authentication/authorization and rate limiting.
- Bootstraps databases with `bin/bootstrap_db.py`.
- Creates a `dev` role user via `bin/create_user.py` (asks for user data).
- Writes `DEV_ADMIN_*` values into `config/.env`.

Linux/macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/master/bin/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command "iwr -useb https://raw.githubusercontent.com/FranBarInstance/neutral-starter-py/master/bin/install.ps1 | iex"
```

Important: first sign-in may require the PIN generated for the created user. Keep that PIN from the installer output.

### 2. Manual Setup (alternative)

#### 2.1 Clone and Configure Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Linux/Mac)
source .venv/bin/activate

# Activate environment (Windows)
.venv\Scripts\activate
```

#### 2.2 Create Runtime Configuration

```bash
cp config/.env.example config/.env
```

At minimum, set a strong value for `SECRET_KEY` in `config/.env`.

#### 2.3 Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2.4 Run in Development with Debugging

```bash
source .venv/bin/activate

# Create/upgrade local DB schema (recommended first run)
python bin/bootstrap_db.py

# Optional debug guard (enabled only when all conditions are met)
# 1) set DEBUG_EXPIRE and DEBUG_FILE in config/.env
#    e.g. DEBUG_EXPIRE=3600 and DEBUG_FILE=/tmp/neutral-debug.flag
export FLASK_DEBUG=1
touch /tmp/neutral-debug.flag

python src/run.py
```

The application will be available at `http://localhost:5000` (by default).

### Optional Automatic DB Bootstrap (development)

You can enable automatic schema bootstrap at app startup:

```env
AUTO_BOOTSTRAP_DB=true
```

Default is `false` to avoid implicit schema changes in production-like environments.

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
4.  **Central Override DB (optional)**: `config/config.db` can store per-component JSON overrides by UUID. For overlapping keys, merge order is: base files -> `custom.json` -> `config.db`.

Boolean environment variables follow a strict rule: **only** `true` (case-insensitive) enables the flag. Any other value (`false`, `0`, `no`, empty, typo) is treated as `False`.

## Security

Security headers, CSP setup, host allow-list validation, and trusted proxy configuration are documented in:

- [docs/security-csp.md](docs/security-csp.md)

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
*   `docs/security-csp.md`: Security headers, CSP configuration, host allow-list, and proxy trust boundaries.

## AI and Agentic Capabilities

The primary goal of this application is to provide developers with agentic, AI-powered capabilities:

- **Component Creation**: AI can generate new application components on demand. You can ask AI to create a specific component for a concrete task within the application ecosystem.

To support this workflow, the project includes:

- **Skills**: Agent skill definitions under `.agent/skills`.
- **Technical Documentation**: Detailed implementation guides in the `docs/` directory.

By reading these skills and technical guides, AI can create components and related functionality on demand in a way that aligns with this project's architecture and conventions.

### Example AI Prompt

An effective example prompt:

```text
Your task is to create the component component_name, which must [functional description].

Use route: /my-route

To complete this task, review:
- .agent/skills/manage-component/SKILL.md
- .agent/skills/manage-neutral-templates/SKILL.md
- src/component/component_name (as a component example)

Define routes dynamically if needed, following the pattern used by other components.
```

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

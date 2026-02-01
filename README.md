# Neutral TS Starter Py

**Neutral TS Starter Py** is a modular scaffold for building Progressive Web Applications (PWA) using **Python (Flask)** on the backend and **Neutral TS** as a universal templating engine.

This project is designed to be extensible via a "plug-and-play" component architecture, allowing scalability from quick prototypes to complex applications while maintaining a clean and decoupled structure.

## Features

*   **Solid Backend**: Built on **Flask**, leveraging its ecosystem and simplicity.
*   **Modular Architecture**: Everything is a component. Logic, routes, templates, and configurations are encapsulated in independent modules within `src/component`.
*   **PWA Ready**: Configuration ready for Service Workers, manifests, and mobile optimization.
*   **Neutral Templating (NTPL)**: Powerful templating system allowing inheritance, mixins, and dynamic rendering.
*   **Override System**: Customize base components without touching their original code thanks to the cascading loading system.

## Prerequisites

*   Python 3.8 or higher.
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

### 2. Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run in Development with Debugging

```bash
export FLASK_DEBUG=1
source .venv/bin/activate
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
    *   `route/`: Python logic (Flask Blueprints).
    *   `neutral/`: HTML templates and snippets.
    *   `static/`: Specific assets (JS/CSS).

For a detailed example, see the [Hello Component README](src/component/cmp_7000_hellocomp/README.md). For complete technical documentation on the component architecture, refer to [docs/component.md](docs/component.md).

## Configuration

Configuration is handled in layers:
1.  **Global**: Environment variables and Flask configuration.
2.  **Per Component**: `schema.json` within each component.
3.  **Customization**: `custom.json` (ignored by git) allows overriding local configurations without affecting the codebase.

## Security & CSP

The application implements a strict **Content Security Policy (CSP)**. By default, external resources are blocked unless explicitly allowed in the configuration.

To ensure the core theme and components work correctly, you **must** whitelist the necessary CDNs in your `config/.env` file:

```ini
# Security Content-Security-Policy (CSP) allowed domains
CSP_ALLOWED_SCRIPT=https://cdnjs.cloudflare.com
CSP_ALLOWED_STYLE=https://cdnjs.cloudflare.com,https://fonts.googleapis.com
CSP_ALLOWED_IMG=https://picsum.photos,https://fastly.picsum.photos
CSP_ALLOWED_FONT=https://cdnjs.cloudflare.com,https://fonts.gstatic.com
CSP_ALLOWED_CONNECT=https://cdnjs.cloudflare.com,https://picsum.photos,https://fastly.picsum.photos
```

If you add new external resources (JS, CSS, fonts), remember to update these variables to avoid console errors and broken layouts.

## Deployment

For production, use a WSGI server like Gunicorn pointing to `src/wsgi.py`:

## Documentation

For more detailed documentation, see the `docs/` directory:
*   `docs/component.md`: Complete guide on component architecture and creation.

## License

See the [LICENSE](LICENSE) file for details.

# Neutral TS Starter Py

**Neutral TS Starter Py** is a modular scaffold for building Progressive Web Applications (PWA) using **Python (Flask)** on the backend and **Neutral TS** as a universal templating engine.

This project is designed to be extensible via a "plug-and-play" component architecture, allowing scalability from quick prototypes to complex applications while maintaining a clean and decoupled structure.

## Features

*   **Solid Backend**: Built on **Flask**, leveraging its ecosystem and simplicity.
*   **Modular Component Architecture**: Everything is a component. Logic, routes, templates, and configurations are encapsulated in independent modules within `src/component`.
*   **PWA Ready**: Configuration ready for Service Workers, manifests, and mobile optimization.
*   **Neutral Templating (NTPL)**: Powerful templating system allowing inheritance, mixins, and dynamic rendering.
*   **Override System**: Customize base components without touching their original code thanks to the cascading loading system.
*   **Internationalization Support (i18n)**: Multi-language support configurable per component.
*   **Security Headers & CSP**: X-Frame-Options, X-Content-Type-Options, and strict Content Security Policy.
*   **CSRF Protection**: Form token protection against Cross-Site Request Forgery attacks.
*   **Rate Limiting**: Built-in protection against abuse and brute force attacks.
*   **Responsive Design**: Adaptable to different devices and screen sizes.
*   **Database Integration**: Support for database connections and SQL queries.
*   **Customizable Themes**: Theme system with multiple theme support.
*   **Session Management**: Secure session handling and management.
*   **Form Validation**: Input validation rules defined in schemas.
*   **File Upload Handling**: Support for file uploads with security controls.
*   **Error Handling & Logging**: Comprehensive error handling and event logging system.
*   **API Endpoints**: RESTful API support for component interactions.
*   **Authentication & Authorization**: Built-in authentication and authorization mechanisms.
*   **Configuration Management**: Layered configuration system (global, per-component, and local overrides).
*   **Static File Serving**: Organized static file serving by component.
*   **Template Rendering**: Dynamic template rendering with caching support.
*   **URL Routing**: Flexible URL routing system with component-specific routes.
*   **Middleware Support**: Request handling, authentication, and authorization middleware.
*   **Testing Framework**: Structure prepared for unit and integration testing.
*   **Documentation Generation**: Automated documentation generation capabilities.

## Overview

Neutral TS Starter Py is a modular web application built on Flask following a component-based architectural pattern. The application enables the creation of customizable web interfaces with support for multiple languages, PWA capabilities, and robust security features.

The project is organized around a modular component system where each component encapsulates its own logic, routes, templates, and configuration, allowing for easy extension and customization.

## Application Architecture

The application follows a layered architecture pattern with clear separation of concerns:

### 1. Presentation Layer
- **Templates**: Uses the NeutralTemplate templating engine
- **Styles**: Customizable CSS per component
- **Interactivity**: Modular JavaScript per component
- **Static Resources**: CSS, JS, images organized by component

### 2. Application Logic Layer
- **Routes**: Defined in component route modules
- **Controllers**: Component-specific logic
- **Middleware**: Request handling, authentication, authorization

### 3. Data Layer
- **Models**: Defined in `src/model/`
- **SQL Queries**: Stored in JSON files
- **Database Connection**: Configured in `src/app/`

### 4. Service Layer
- **Utilities**: Helper functions in `src/utils/`
- **Configuration**: Global and component-specific parameters
- **Internationalization**: Language management in component locales

### Request Flow

```
HTTP Client
    ↓
Security Middleware
    ↓
Main Router
    ↓
[Select Component]
    ↓
Component Logic
    ↓
Model/Data
    ↓
Rendered Template
    ↓
HTTP Response
```

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
    *   `schema.json`: Configuration and customization settings.
    *   `route/`: Python logic (Flask Blueprints).
    *   `neutral/`: HTML templates and snippets.
    *   `static/`: Specific assets (JS/CSS).
    *   `__init__.py`: Component initialization.

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

# Security Content-Security-Policy (CSP) unsafe directives
CSP_ALLOWED_SCRIPT_UNSAFE_INLINE=false
CSP_ALLOWED_SCRIPT_UNSAFE_EVAL=false
CSP_ALLOWED_STYLE_UNSAFE_INLINE=false
```

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

## Documentation

For more detailed documentation, see the `docs/` directory:
*   `docs/component.md`: Complete guide on component architecture and creation.

## License

See the [LICENSE](LICENSE) file for details.

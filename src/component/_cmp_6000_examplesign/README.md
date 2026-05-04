# Example Sign Component (`examplesign_0yt2sa`)

## Overview

The `examplesign_0yt2sa` component is a didactic example demonstrating AJAX forms, declarative validation, form tokens, Bootstrap modals, and simple state management via cookies in Neutral Starter Py. It implements a fake login/logout system for educational purposes only.

**Warning:** This component is not intended for production use. It uses hardcoded credentials and fake sessions. Do not deploy this in real applications.

## Key Features

- **AJAX Forms**: Login and logout forms submitted asynchronously.
- **Declarative Validation**: Field validation defined in `/route/schema.json`.
- **Form Tokens**: Integration with `ftoken_0yt2sa` for CSRF protection.
- **Bootstrap Modals**: Forms renderable as full pages or modals.
- **Cookie-Based State**: Simple session management via `fake-login-session` cookie.
- **Internationalization**: Translations in multiple languages.
- **Security Patterns**: Demonstrates anti-bot validation and header requirements.

## Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/example-sign/` | Initial page showing session state |
| `GET` | `/example-sign/login` | Full login form page |
| `GET` | `/example-sign/login/ajax/<ltoken>` | AJAX login container |
| `POST` | `/example-sign/login/ajax/<ltoken>` | Submit login form |
| `GET` | `/example-sign/logout` | Full logout form page |
| `GET` | `/example-sign/logout/ajax/<ltoken>` | AJAX logout container |
| `POST` | `/example-sign/logout/ajax/<ltoken>` | Submit logout form |
| `GET` | `/example-sign/help/<item>` | AJAX-only help content |

## Usage

### Accessing the Component

The component is accessible at `/example-sign` (defined in `manifest.json`).

- Anonymous users see login options.
- "Logged-in" users (with fake cookie) see logout options.

### Fake Credentials

For testing:
- Email: `email@example.com`
- Password: `12345678`

### Forms

Forms validate fields and display errors. Login creates a `fake-login-session=true` cookie on success. Logout removes the cookie.

## Architecture

### Backend

- `route/routes.py`: Flask route definitions.
- `route/example_sign_handler.py`: Handlers extending `FormRequestHandler`.
- `route/schema.json`: Form validation schemas.

### Templates

- `neutral/route/form-snippets.ntpl`: AJAX form snippets.
- `neutral/route/root/`: Page templates.
- `neutral/route/locale-*.json`: Translations.

### Menu Integration

The component adds menu entries for both anonymous and logged-in states via `schema.json`.

## Development

### File Structure

```
_cmp_6000_examplesign/
├── manifest.json          # Component metadata and route
├── schema.json            # Menu and data schemas
├── route/
│   ├── routes.py          # Flask routes
│   ├── schema.json        # Form validation
│   └── example_sign_handler.py  # Request handlers
├── neutral/route/
│   ├── form-snippets.ntpl # Form templates
│   ├── index-snippets.ntpl
│   ├── locale-*.json      # Translations
│   └── root/              # Page templates
├── tests/
│   └── test_routes.py     # Unit tests
└── .specify/spec.md       # Detailed specification
```

### Enabling/Disabling

The component can be disabled by renaming the folder to start with `_` (already done as `_cmp_6000_examplesign`).

### Testing

Run tests with:

```bash
source .venv/bin/activate && pytest -q src/component/_cmp_6000_examplesign/tests
```

Tests derive the route from `manifest.json`.

## Security Notes

- Routes are publicly accessible (`security.routes_auth["/"] = false`).
- Security is enforced at the form level (tokens, anti-bot checks).
- AJAX help endpoints require `Requested-With-Ajax` header.
- `notrobot` field must be `human`; `notrobot-hidden` must be absent.

## Production Considerations

This is an example component. For real authentication:

- Replace fake logic with database-backed user management.
- Implement proper session handling.
- Add rate limiting and logging.
- Use secure cookies with proper attributes.

## License

Part of Neutral Starter Py project.
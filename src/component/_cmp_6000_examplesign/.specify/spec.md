# Component: examplesign_0yt2sa

## Executive Summary

Example component demonstrating AJAX forms, declarative validation, form tokens, Bootstrap modals, and state management via cookie. Provides a complete but fake authentication flow for teaching form patterns in Neutral Starter Py. The login uses constant credentials and creates a fake session cookie — not for production use, but as a reference for building real form flows.

## Identity

- **UUID**: `examplesign_0yt2sa`
- **Base Route**: `<manifest.route>`
- **Version**: `0.0.0`

## Functional Scope

The component must show a complete and minimal flow of:

- initial page with fake session state;
- login form renderable as full page and as modal;
- logout form renderable as full page and as modal;
- AJAX endpoints to load and submit forms;
- field validation via `/route/schema.json`;
- integration with `ftoken_0yt2sa` in the login form;
- help content loaded under mandatory AJAX header;
- translations per language in `/neutral/route/locale-*.json`;
- tests that derive the route from `/manifest.json`.

## Non-Objectives

- Should not be considered a real authentication system.
- Should not access database nor create real user sessions.
- Should not store credentials or secrets.
- Should not serve as a security pattern for productive login, except for the handler structure, validation, and tokens.

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes are publicly accessible (example/demo component)
- AJAX POSTs validate `LTOKEN` via `FormRequestHandler`
- Login form validates `ftoken` with `ftoken_check` (anti-bot)
- `notrobot-hidden` honeypot field must be absent
- `notrobot` field must exist with value `human`
- Help endpoints require `Requested-With-Ajax` header
- Fake session cookie (`fake-login-session`) for demonstration only — not a secure pattern

## Routes

`<manifest.route>` is defined in `/manifest.json`.

| Method | Route | Handler | Purpose |
|---|---|---|---|
| `GET` | `<manifest.route>/` | `ExampleSignRequestHandler` | Renders the initial page and fake cookie state. |
| `GET` | `<manifest.route>/<path>` | `ExampleSignRequestHandler` | Renders template routes under `/neutral/route/root/`. |
| `GET` | `<manifest.route>/login` | `ExampleSignInRequestHandler` | Renders the full page of the login form. |
| `GET` | `<manifest.route>/login/ajax/<ltoken>` | `ExampleSignInRequestHandler` | Renders the AJAX container of the login. |
| `POST` | `<manifest.route>/login/ajax/<ltoken>` | `ExampleSignInRequestHandler` | Validates the fake login and creates the cookie if applicable. |
| `GET` | `<manifest.route>/logout` | `ExampleSignOutRequestHandler` | Renders the full page of the logout form. |
| `GET` | `<manifest.route>/logout/ajax/<ltoken>` | `ExampleSignOutRequestHandler` | Renders the AJAX container of the logout. |
| `POST` | `<manifest.route>/logout/ajax/<ltoken>` | `ExampleSignOutRequestHandler` | Deletes the fake cookie if applicable. |
| `GET` | `<manifest.route>/help/<item>` | `ExampleSignRequestHandler` | Returns cacheable help only for AJAX requests. |

## Architecture

### Component Type
**Example** component. Provides:
- Fake authentication flow for teaching form patterns
- AJAX form submission examples
- Modal form demonstrations
- Form validation examples
- CSRF and anti-bot protection demonstrations

### Routes

| Method | Route | Handler | Auth | Purpose |
|--------|-------|---------|------|---------|
| `GET` | `<manifest.route>/` | `ExampleSignRequestHandler` | No | Initial page with fake session state |
| `GET` | `<manifest.route>/<path>` | `ExampleSignRequestHandler` | No | Template routes |
| `GET` | `<manifest.route>/login` | `ExampleSignInRequestHandler` | No | Full login form page |
| `GET/POST` | `<manifest.route>/login/ajax/<ltoken>` | `ExampleSignInRequestHandler` | No | AJAX login container/submit |
| `GET` | `<manifest.route>/logout` | `ExampleSignOutRequestHandler` | No | Full logout form page |
| `GET/POST` | `<manifest.route>/logout/ajax/<ltoken>` | `ExampleSignOutRequestHandler` | No | AJAX logout container/submit |
| `GET` | `<manifest.route>/help/<item>` | `ExampleSignRequestHandler` | No | Cacheable help (AJAX only) |

### Route Handlers (`/route/example_sign_handler.py`)

`ExampleSignRequestHandler` extends `FormRequestHandler`:

**Responsibilities:**
- GET validation with `valid_form_tokens_get`
- POST validation with `valid_form_tokens_post`, `valid_form_validation`, `any_error_form_fields`
- Anti-bot validation with `ftoken_check`
- Reading `fake-login-session` cookie
- Creating/deleting fake cookie via `view.add_cookie`

`ExampleSignInRequestHandler` adds fake credential check:
- Expected email: `email@example.com`
- Expected password: `12345678`
- Field errors communicated via `error["field"]` for template feedback

`ExampleSignOutRequestHandler` validates form and deletes cookie.

### Form Validation (`/route/schema.json`)

Two forms defined under `data.current_forms`:

**`fake_login` validates:**

- `email`: required, HTML pattern, backend email regex
- `password`: required, length 8-70, no leading/trailing spaces
- `notrobot`: required, value must be `human`
- `notrobot-hidden`: must not be present (honeypot)
- `ftoken.*`: allowed as auxiliary field for `ftoken_0yt2sa`

**`fake_logout` validates:**
- `logout`: required with value `1`
- Only `send` and `logout` fields allowed
- Field count between `minfields` and `maxfields`

### Templates

**`/neutral/route/index-snippets.ntpl`** — Loads shared snippets, makes form blocks available.

**`/neutral/route/form-snippets.ntpl`** — Main AJAX forms example:
- Includes snippets from `forms_0yt2sa`
- Error snippets per field for both forms
- Forms wrapped with `{:fetch; ... :}`
- Endpoints built with `{:;examplesign_0yt2sa->manifest->route:}`
- Bootstrap-compatible classes
- Modals moved to end of `<body>`
- Modal forms use `{:fetch; ... |visible| ... :}` to avoid state duplication

**Template routes under `/neutral/route/root/`:**
- `/login/content-snippets.ntpl` — Full login content
- `/login/ajax/content-snippets.ntpl` — AJAX container only
- `/logout/content-snippets.ntpl` — Full logout content
- `/logout/ajax/content-snippets.ntpl` — AJAX container only
- `/help/content-snippets.ntpl` — Help item resolution

## Data and Models

### Translations

6 language files (`/neutral/route/locale-*.json`): EN, ES, FR, DE, AR, ZH

Handler error references like `ref:fake_login_form_error_email_not_match` must exist in translations.

### Menu Integration

Drawer and menu entries for both anonymous and logged-in users:
- `data.current.drawer.menu["session:"]` and `["session:true"]`
- `data.current.menu["session:"]` and `["session:true"]`

Links use schema references to `examplesign_0yt2sa->manifest->route`.

---

## Acceptance Criteria (SDD)

### Functional
- [x] Root route renders without requiring real session
- [x] AJAX login rejects invalid tokens without breaking render
- [x] Correct login POST creates `fake-login-session=true` cookie
- [x] Incorrect login POST shows field errors
- [x] Correct logout POST deletes fake cookie
- [x] `/help/<item>` requires AJAX header, responds with cache headers

### Technical
- [x] Forms use `{:fetch; ... :}` for AJAX submission
- [x] No inline JavaScript or event handlers
- [x] All visible text uses `{:trans; ... :}`
- [x] Tests derive `<manifest.route>` from `/manifest.json`

## Technical Rationale

- **Form separation pattern**: Routes, handlers, validation schema, snippets, and translations are separated — this is the key pattern for production
- **Fake credentials**: Hardcoded credentials (`email@example.com` / `12345678`) are demonstration-only
- **AJAX-first forms**: Full-page and modal forms share handlers via `{:fetch; ... :}`
- **Anti-bot protection**: `ftoken` + honeypot field pattern for bot detection

## Known Limitations

- Fake cookie is not a secure session mechanism
- Constant credentials must never be used in production
- May conflict with real authentication components if both enabled
- Menu entries may confuse users if real auth also present

### Testing

```bash
source .venv/bin/activate && pytest -q <component-root>/tests
```

---

*Last updated: 2026-05-04*

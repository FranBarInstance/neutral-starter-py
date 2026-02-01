# Component: Sign (`sign_0yt2sa`)

The **Sign** component manages all user authentication processes, including signing in, signing up, password reminders, and signing out. It follows the standard Neutral PWA architecture, combining Flask back-end logic with NTPL front-end templates.

## Overview

- **UUID**: `sign_0yt2sa`
- **Route Prefix**: `/sign`
- **Dependencies**: Requires `ftoken_0yt2sa` for form security tokens.

## Key Features

- **User Authentication**: Secure sign-in and sign-up flows.
- **Session Management**: Logout functionality and session state handling.
- **Password Recovery**: Support for password reminders via email.
- **PIN Verification**: Handles PIN-based verification and registration steps.
- **Privacy First**: Silent reminders when a user tries to register with an existing email, preventing account enumeration.
- **Form Validation**: Comprehensive server-side and client-side validation rules defined in `schema.json`.
- **Modals & Navigation**: Pre-configured menu entries for Navbar, Drawer, and User menus, including modal triggers for Bootstrap.
- **Multilingual**: Built-in support for English, Spanish, French, and German.

## File Structure

- `manifest.json`: Registration metadata and dependencies.
- `schema.json`: Menu definitions, form validation rules, and global data.
- `route/`:
    - `routes.py`: Flask route definitions for all authentication actions.
    - `dispatcher_form_sign.py`: Business logic for handling form submissions and data processing.
- `neutral/`:
    - `component-init.ntpl`: Global snippets for authentication.
    - `snippets-session-true.ntpl` / `snippets-session-false.ntpl`: Conditional snippets based on user session state.
    - `route/`: NTPL templates for specific routes (in, up, out, reminder, etc.).

## Configuration (`schema.json`)

The component populates several menu structures:
- **Navbar**: Adds "Sign in" and "Sign up" buttons (with modal triggers) when no session is active, and "Sign out" when logged in.
- **Drawer**: Adds a User section in the side menu.
- **Menu**: Accessible via user profile, providing direct links to authentication pages.

### Form Validation
Rules for `sign_in_form`, `sign_up_form`, and `sign_reminder_form` are strictly defined under `data -> core -> forms`. These include:
- Required fields.
- Regex patterns (email, password, alias).
- Length constraints.
- Security fields (`notrobot`, `ftoken`).

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/sign/in` | GET | Renders the sign-in page. |
| `/sign/in/form/<ltoken>` | GET/POST | Handles the actual sign-in form submission. |
| `/sign/up` | GET | Renders the sign-up page. |
| `/sign/up/form/<ltoken>` | GET/POST | Handles user registration. |
| `/sign/reminder` | GET | Renders the password reminder page. |
| `/sign/reminder/form/<ltoken>` | GET/POST | Processes password reminder requests. |
| `/sign/out` | GET | Finalizes the user session and logs out. |
| `/sign/pin/<token>` | GET/POST | Handles PIN-based verification or actions. |
| `/sign/help/<item>` | GET | Serves help content for specific auth items (cached). |

## Integration

To link to a specific authentication page from another component, use the defined data paths:

```html
<!-- Sign In Link -->
<a href="[:;data->sign_0yt2sa->manifest->route:]/in">Sign In</a>

<!-- Sign Up Link -->
<a href="[:;data->sign_0yt2sa->manifest->route:]/up">Sign Up</a>
```

## Security & Privacy

- **Account Enumeration Protection**: During registration, if an email already exists in the database, the system will not disclose it. Instead, it silently sends a password reminder to that email.
- **Form Protection**: All forms are protected by `ftoken` (via the `ftoken_0yt2sa` component) and a `notrobot` honeypot/validation system to prevent automated submissions.
- **Rate Limiting**: Applied to sensitive routes (sign-in, sign-up, reminder) as defined in `app.config.Config`.
- **Session Security**: Sessions are tied to the User Agent and use secure cookies.

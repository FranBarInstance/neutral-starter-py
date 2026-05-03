# Mail Template Component

**UUID:** `mail_template_0yt2sa`

Default mail template provider for the Neutral Starter framework. This component implements the [Mail Template Provider Contract](../../.specify/specs/010-mail-system/provider-spec.md) and provides a complete set of email templates with a consistent theme system.

## Overview

This component registers itself as the active mail template provider during application initialization. It provides:

- **5 ready-to-use email templates**: `register`, `reminder`, `pin`, `account-pin`, `sample`
- **Shared snippet library** with fallback values from site configuration
- **Theme system** with customizable colors and styling
- **Multi-language support** (EN, ES, DE, FR)
- **Responsive HTML email rendering**

## File Structure

```
src/component/cmp_0200_mail_template/
├── manifest.json           # Component metadata
├── __init__.py            # Registers as mail template provider
└── neutral/
    └── layout/            # Template files (layout root)
        ├── index.ntpl          # Entry point layout
        ├── snippets.ntpl       # Shared snippets with fallbacks
        ├── theme-snippets.ntpl # Theme block definitions
        ├── theme.ntpl          # Main theme template
        ├── local-data.json     # Default theme data
        ├── locale.json         # Translations
        ├── mail-register-snippets.ntpl     # Registration email
        ├── mail-reminder-snippets.ntpl     # Password reminder email
        ├── mail-pin-snippets.ntpl          # PIN confirmation email
        ├── mail-account-pin-snippets.ntpl   # Account security PIN email
        └── mail-sample-snippets.ntpl       # Sample/demo email
```

## How It Works

### Template Resolution Flow

1. **Caller sends email** via `Mail.send(content_template, mail_data)`
2. **Core system** prepares `current_mail` data bag with:
   - `content_template`: The template identifier (e.g., `"register"`)
   - `mail_data`: All keys passed by the caller
   - `layout_data`: Optional presentation data
3. **This component's** `index.ntpl` renders by:
   - Loading locale and theme data
   - Including `snippets.ntpl` (shared snippets)
   - Including `mail-{content_template}-snippets.ntpl` (specific content)
   - Rendering through `theme.ntpl`

### Entry Point: `index.ntpl`

```ntpl
{:^include; {:flg; require :} >> #/snippets.ntpl :}
{:^include; {:flg; require :} >> #/mail-{:;current_mail->content_template:}-snippets.ntpl :}
{:^include; {:flg; require :} >> #/theme.ntpl :}
```

The dynamic include on line 26 loads the appropriate snippet file based on `content_template`.

## Shared Snippets (`snippets.ntpl`)

All templates have access to these shared snippets with automatic fallbacks:

| Snippet | Description | Fallback |
|---------|-------------|----------|
| `{:snip; mail_template_0yt2sa:url-home :}` | Home URL | `current->site->url` |
| `{:snip; mail_template_0yt2sa:url-logo :}` | Logo image URL | `{url-home}{site->logo}` |
| `{:snip; mail_template_0yt2sa:url-cover :}` | Cover/hero image URL | `{url-home}{site->cover}` |
| `{:snip; mail_template_0yt2sa:brand-text :}` | Brand name | `current->site->name` |
| `{:snip; mail_template_0yt2sa:cover-text :}` | Cover image alt text | `current->site->cover_text` |
| `{:snip; mail_template_0yt2sa:logo-text :}` | Logo alt text | `current->site->name` |
| `{:snip; mail_template_0yt2sa:auth-link :}` | Authentication link | `url-home` |
| `{:snip; mail_template_0yt2sa:pin :}` | PIN code | Empty string |

### Usage Example

```ntpl
{:code;
    {:param; url-link >> {:snip; mail_template_0yt2sa:url-home :} :}
    {:param; url-img >> {:snip; mail_template_0yt2sa:url-logo :} :}
    {:param; text >> {:snip; mail_template_0yt2sa:brand-text :} :}
    {:snip; mail_template_0yt2sa:theme-brand :}
:}
```

## Available Mail Templates

### 1. `register` - User Registration
**File:** `mail-register-snippets.ntpl`

Sent when a new user registers. Contains:
- Welcome message with brand header
- Hero image
- Call-to-action button with `auth_link`
- PIN display (if required)
- Expiration notice

**Expected `mail_data` keys:**
```python
{
    "to": "...",
    "subject": "...",
    "userId": "...",
    "profileId": "...",
    "alias": "...",
    "email": "...",
    "locale": "...",
    "token": "...",
    "pin": "...",
    "auth_link": "...",  # Optional; falls back to site URL
    "expires": "...",    # Optional; for expiration text
}
```

### 2. `reminder` - Password Reminder
**File:** `mail-reminder-snippets.ntpl`

Sent when user requests password recovery. Contains:
- Brand header and hero image
- Password reminder text
- Login button with `auth_link`
- PIN display
- Expiration warning

**Expected `mail_data` keys:** Same as `register` template.

### 3. `pin` - Email PIN Confirmation
**File:** `mail-pin-snippets.ntpl`

Sent to confirm email address changes. Contains:
- Brand header and hero image
- PIN explanation text
- Large PIN display
- Expiration notice (in hours)

**Expected `mail_data` keys:**
```python
{
    "to": "...",
    "subject": "...",
    "alias": "...",
    "locale": "...",
    "pin": "...",
    "token": "...",
    "expires": "...",  # Hours until expiration (minimum 1)
}
```

### 4. `account-pin` - Account Security PIN
**File:** `mail-account-pin-snippets.ntpl`

Sent for sensitive account operations. Contains:
- Brand header and hero image
- Security PIN text
- Large PIN display
- Short expiration notice

**Expected `mail_data` keys:** Same as `pin` template.

### 5. `sample` - Demo Template
**File:** `mail-sample-snippets.ntpl`

A comprehensive example showing all available theme blocks. Useful for:
- Testing email rendering
- Understanding available blocks
- Creating new templates

## Creating a New Mail Template

To add a new email template (e.g., `welcome`):

1. **Create snippet file:**
   ```bash
   touch neutral/layout/mail-welcome-snippets.ntpl
   ```

2. **Define required structure:**
   ```ntpl
   {:* Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE) *:}

   {:snip; mail_template_0yt2sa:theme-head-begin >>
       <title>{:trans; ref:email-welcome-title :}</title>
   :}

   {:snip; mail_template_0yt2sa:theme-blocks >>

       {:code;
           {:param; url-link >> {:snip; mail_template_0yt2sa:url-home :} :}
           {:param; url-img >> {:snip; mail_template_0yt2sa:url-logo :} :}
           {:param; text >> {:snip; mail_template_0yt2sa:brand-text :} :}
           {:snip; mail_template_0yt2sa:theme-brand :}
       :}

       {:code;
           {:param; url-link >> {:snip; mail_template_0yt2sa:url-home :} :}
           {:param; url-img >> {:snip; mail_template_0yt2sa:url-cover :} :}
           {:param; img-text >> {:snip; mail_template_0yt2sa:cover-text :} :}
           {:snip; mail_template_0yt2sa:theme-block-img-hero :}
       :}

       {:code;
           {:param; h1 >> {:trans; ref:email-welcome-subject :} :}
           {:param; p1 >> {:trans; ref:email-welcome-text :} :}
           {:param; p2 >> :}
           {:snip; mail_template_0yt2sa:theme-block-text :}
       :}

   :}
   ```

3. **Add translations to `locale.json`:**
   ```json
   {
       "en": {
           "ref:email-welcome-title": "Welcome",
           "ref:email-welcome-subject": "Welcome to our platform",
           "ref:email-welcome-text": "Thank you for joining us!"
       },
       "es": { ... },
       "de": { ... },
       "fr": { ... }
   }
   ```

4. **Use from handler:**
   ```python
   from core.mail import Mail

   mail_data = {
       "to": user_email,
       "subject": "Welcome!",
       "alias": user_alias,
       "locale": user_locale,
   }
   mail = Mail(self.schema.properties)
   mail.send("welcome", mail_data)
   ```

## Available Theme Blocks

The theme system (`theme-snippets.ntpl`) provides these reusable blocks:

| Block | Purpose | Parameters |
|-------|---------|------------|
| `mail-theme-brand` | Logo + brand name | `url-link`, `url-img`, `text` |
| `mail-theme-block-img-hero` | Hero image | `url-link`, `url-img`, `img-text` |
| `mail-theme-block-text` | Text content | `h1`, `p1`-`p5` |
| `mail-theme-block-button-primary` | CTA button | `url-link`, `txt-link` |
| `mail-theme-block-outline` | Highlighted box | `txt` |

## Customization

### Overriding This Provider

To replace this component with your own templates:

1. Create a new component (e.g., `cmp_custom_mail`)
2. Call `set_current_mail_template()` in its `__init__.py`
3. Provide the same file structure under `neutral/layout/`

See [Mail System Documentation](../../docs/mail-system.md) for details.

### Custom Theme Colors

Create `local-data-{color}.json` files for custom color schemes:

```json
{
    "colors": {
        "primary": "#your-color",
        "secondary": "#your-color",
        "background": "#your-color",
        "text": "#your-color"
    }
}
```

Pass `theme-color` in `layout_data` to activate:

```python
mail.send("register", mail_data, layout_data={"theme-color": "corporate"})
```

## References

- [Mail System Documentation](../../docs/mail-system.md) - Complete mail system architecture
- [Provider Specification](../../.specify/specs/010-mail-system/provider-spec.md) - Contract details
- [Mail System Spec](../../.specify/specs/010-mail-system/spec.md) - Full specification

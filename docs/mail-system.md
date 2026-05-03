# Mail System

## Overview

The mail system provides a generic, template-agnostic email transport layer. It is composed of three classes in `src/core/mail.py`, but **templates and presentation are not part of this system**. Any component can act as the mail template provider by registering its template directory at application startup.

| Class | Role | File |
|-------|------|------|
| `Mail` | Orchestrator: validates data, renders layout, dispatches to transport | `src/core/mail.py` |
| `MailTemplate` | NTPL renderer via `NeutralTemplate` | `src/core/mail.py` |
| `MailSend` | Transport: SMTP, sendmail, or file | `src/core/mail.py` |

## Architecture

```
Caller (any handler)
    |
    v
Mail(schema).send(content_template, mail_data, layout_data=None)
    |
    +-- _prepare_mail_data()  -> writes schema['data']['current_mail']
    +-- MailTemplate.render()   -> renders the layout NTPL to HTML
    +-- _html_to_text()         -> generates a plain text fallback
    +-- MailSend.send()         -> builds MIME and dispatches via transport
```

The `content_template` argument is an opaque identifier consumed by the layout template. The mail system does not interpret it. The template provider decides whether it is a snippet name, a file stem, or any other key.

---

## Sending an Email

### Minimal call

```python
from core.mail import Mail

mail = Mail(self.schema_data)
result = mail.send("alert", {
    'to':      user_email,
    'subject': 'System notification',
})
```

### Full call

```python
from core.mail import Mail
from app.config import Config

mail = Mail(self.schema_data)

mail_data = {
    'to':      user_email,
    'subject': 'Account verification',
    'from':    Config.MAIL_SENDER,   # optional; defaults to Config.MAIL_SENDER
    'code':    verification_code,   # available to the layout as current_mail->code
    'url':     verification_url,
}

layout_data = {
    'theme_color': '#375A7F',       # optional; only if the template provider expects it
}

result = mail.send("register", mail_data, layout_data)

if not result['success']:
    self.log_error(f"Mail failed: {result['error']}")
```

### Signature

```python
Mail.send(
    content_template: str,
    mail_data: dict,
    layout_data: dict = None
) -> dict
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `content_template` | Yes | Opaque identifier passed to the layout template. The provider decides how to map it to a snippet or file. |
| `mail_data['to']` | Yes | Recipient address. |
| `mail_data['subject']` | Yes | Email subject. |
| `mail_data['from']` | No | Sender address. Defaults to `Config.MAIL_SENDER`. |
| `mail_data[*]` | No | Any extra keys are merged into `current_mail` and are available to the layout. |
| `layout_data` | No | Presentation data for the layout (colors, logo, etc.). If the provider does not need extra presentation data, omit it. |

**Return value:**

```python
{'success': bool, 'message_id': str|None, 'error': str|None}
```

`send()` never raises. On any failure it returns `{'success': False, 'error': str(e)}`.

---

## Configuration

All transport settings live in `app/config.py` as environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `MAIL_METHOD` | `smtp` | Transport: `smtp`, `sendmail`, or `file` |
| `MAIL_SERVER` | `localhost` | SMTP host |
| `MAIL_PORT` | `587` | SMTP port |
| `MAIL_USERNAME` | `` | SMTP username |
| `MAIL_PASSWORD` | `` | **Secret** — only via environment |
| `MAIL_USE_TLS` | `false` | Enable STARTTLS |
| `MAIL_SENDER` | `` | Default sender address |
| `MAIL_RETURN_PATH` | `` | Return-Path for sendmail mode |
| `MAIL_TO_FILE` | `/tmp/test_mail.html` | Output path in `file` mode |
| `MAIL_TEMPLATE_NAME` | `index.ntpl` | Layout filename; same pattern as `TEMPLATE_NAME` |

Secrets must never be stored in `manifest.json` or `schema.json`. Follow **Standard 011 (Component Configuration)**.

---

## Data Flow

### 1. Template registration at startup

A component calls `set_current_mail_template()` in its `init_component()`:

```python
from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    set_current_mail_template(component, component_schema)
```

This writes:

```python
schema['data']['current']['mail_template'] = {
    'dir': '/absolute/path/to/component/neutral'
}
```

Then `core/schema.py._general_data()` resolves `MAIL_TEMPLATE_LAYOUT`:

```python
mail_template_dir = self.data['current']['mail_template']['dir']
self.data['MAIL_TEMPLATE_LAYOUT'] = os.path.join(
    mail_template_dir, 'layout', Config.MAIL_TEMPLATE_NAME
)
```

### 2. Sending at runtime

`Mail.__init__()` reads `MAIL_TEMPLATE_LAYOUT` from the schema:

```python
self.tpl = tpl or self.data.get('MAIL_TEMPLATE_LAYOUT')
```

If no component registered a mail template provider, `Mail()` raises `ValueError`.

### 3. Preparing the data bag

`_prepare_mail_data()` writes `schema['data']['current_mail']`:

```python
self.data['current_mail'] = {
    'content_template': content_template,
    **(layout_data or {}),
    **mail_data,          # mail_data wins in conflicts
}
```

The layout template reads from `current_mail`:

```
{:;current_mail->content_template:}
{:;current_mail->to:}
{:;current_mail->subject:}
{:;current_mail->code:}   # any extra key passed in mail_data
```

### Variables injected by callers

The mail system does not prescribe which extra keys a caller must include. Any component that sends an email can pass whatever the template provider expects.

For example, a registration handler might send:

```python
mail_data = {
    'to':        '...',
    'subject':   '...',
    'userId':    '...',
    'profileId': '...',
    'alias':     '...',
    'email':     '...',
    'locale':    '...',
    'token':     '...',
    'pin':       '...',
    'auth_link': '...',     # optional; fallback to site URL
    'expires':   '...',     # optional; used by translations that reference it
}

result = mail.send("register", mail_data)
```

A password reminder handler might send:

```python
mail_data = {
    'to':        '...',
    'subject':   '...',
    'alias':     '...',
    'email':     '...',
    'userId':    '...',
    'profileId': '...',
    'locale':    '...',
    'token':     '...',
    'pin':       '...',
    'auth_link': '...',
    'expires':   '...',
}

result = mail.send("reminder", mail_data)
```

PIN:

```python
{
    "to":      '...',
    "subject": '...',
    "alias":   '...',
    "locale":  '...',
    "pin":     '...',
    "token":   '...',
    "expires": '...',
}

result = mail.send("pin", mail_data)
```

The layout and snippets can then access any of those keys:

```
{:;current_mail->pin:}
{:;current_mail->token:}
{:;current_mail->alias:}
{:;current_mail->locale:}
{:;current_mail->userId:}
...
```

Because the merge is unconditional, the template provider should document which keys it expects for each `content_template` value, but the mail system itself does not validate them.

---

## Creating a Mail Template Provider

Any component can provide mail templates. The system is designed so that the **last component to call `set_current_mail_template()` wins**. If two components register, the second one becomes the active provider for the lifetime of the application.

### Minimum file structure

```
src/component/<your_component>/
├── manifest.json
├── __init__.py
└── neutral/
    └── layout/
        ├── index.ntpl          # layout entry point
        ├── local-data.json     # default visual variables
        └── locale.json         # translations
```

### 1. `__init__.py`

```python
from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    """Register this component as the active mail template provider."""
    set_current_mail_template(component, component_schema)
```

### 2. `manifest.json`

```json
{
    "uuid": "your_mail_template_uuid",
    "name": "Custom Mail Templates",
    "description": "Provides email layouts and snippets",
    "version": "1.0.0",
    "route": "",
    "security": {
        "routes_auth": {"/": false},
        "routes_role": {"/": ["*"]}
    },
    "config": {}
}
```

### 3. `neutral/layout/index.ntpl`

This is the entry point. The mail system renders this file via `NeutralTemplate`. It must use `current_mail->content_template` to decide which content to load.

```
{:* 1. Load defaults *:}
{:^data; {:flg; require :} >> #/local-data.json :}

{:* 2. Load translations *:}
{:^locale; {:flg; require :} >> #/locale.json :}

{:* 3. Include the content snippet based on content_template *:}
{:^include; {:flg; require :} >> #/mail-{:;current_mail->content_template:}-snippets.ntpl :}

{:* 4. Render the HTML wrapper *:}
{:^include; {:flg; require :} >> #/theme.ntpl :}
```

### 4. `neutral/layout/local-data.json`

Default visual variables. The layout should use `{:else; ... :}` so that callers can override them via `layout_data`.

```json
{
    "data": {
        "theme-color": "#ffffff",
        "background-color": "#333333",
        "button-primary-background-color": "#375A7F"
    }
}
```

### 5. `neutral/layout/mail-<name>-snippets.ntpl`

One snippet file per `content_template` value your application uses.

```
{:* mail-register-snippets.ntpl *:}
<h1>{:trans; Welcome :} {:;current_mail->alias:}!</h1>
<p>{:trans; Your verification code is: :}</p>
<p>{:;current_mail->code:}</p>
```

### Fallbacks and defaults

Always provide fallbacks in the layout so that missing `layout_data` does not break rendering:

```
{:;current_mail->logo:}{:else; {:;current->site->logo:} :}
```

---

## Overriding the Default Provider

The built-in provider is `cmp_0200_mail_template`. To override it:

1. Create a new component (e.g. `cmp_NNN1_custom_mail_template`).
2. Add it to `manifest.json` **after** the default provider, or disable the default provider.
3. Call `set_current_mail_template()` in its `__init__.py`.

Because **last wins**, your component becomes the active provider without touching any core code.

---

## Testing

### File mode (no SMTP needed)

Set `MAIL_METHOD=file` in your environment. The rendered HTML will be written to `MAIL_TO_FILE` (default `/tmp/test_mail.html`).

```python
from core.mail import Mail

mail = Mail(schema_data)
result = mail.send("register", {
    'to': 'test@example.com',
    'subject': 'Test',
    'code': '123456',
})

assert result['success']
assert '/tmp/test_mail.html' in result['message_id']
```

### Inspecting the data bag

```python
mail = Mail(schema_data)
mail.send("alert", mail_data, layout_data)

import json
print(json.dumps(schema_data['data'].get('current_mail', {}), indent=2))
```

---

## Reference

| Document | Purpose |
|----------|---------|
| `.specify/specs/010-mail-system/spec.md` | Transport system specification |
| `.specify/specs/010-mail-system/plan.md` | Implementation plan |
| `.specify/specs/010-mail-system/provider-spec.md` | Contract for template providers |

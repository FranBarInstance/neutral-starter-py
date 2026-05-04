# 010 - Mail System

## Executive Summary

This specification defines the **email transport system** of Neutral Starter
Py. It supports multiple transport methods (`smtp`, `sendmail`, `file`),
multipart MIME generation, and retry handling for temporary failures.

The architecture is intentionally split across three classes:

- **`Mail`** (`core/mail.py`): orchestrator. It receives the schema, prepares
  `current_mail` by merging `layout_data` and `mail_data`, then coordinates
  rendering and transport.
- **`MailTemplate`** (`core/mail.py`): NTPL mail layout rendering. It does not
  produce an HTTP response.
- **`MailSend`** (`core/mail.py`): SMTP / sendmail / file transport layer.

The active email layout is selected by a component calling
`set_current_mail_template()` from its `__init__.py`.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/011-component-configuration/spec.md` - configuration standard,
  especially the no-secrets-in-JSON rule.
- `specs/009-i18n-standard/spec.md` - email template internationalization.
- `specs/002-neutral-templates-standard/spec.md` - NTPL syntax rules.
- `src/core/mail.py` - mail transport implementation.
- `src/core/template.py` - baseline NTPL rendering pattern.

---

## 1. Goals

### 1.1 What this system must achieve

- flexible transport through SMTP, sendmail, or file output;
- NTPL-based mail layout rendering through `MAIL_TEMPLATE_LAYOUT`;
- multipart MIME generation with text and HTML parts;
- retries with exponential backoff for temporary failures;
- secure transport with TLS, safe header handling, and no credential logging.

### 1.2 Non-goals

- the system does not define the template provider's internal file structure;
- it does not implement a persistent queue;
- it does not track opens or clicks;
- it does not manage subscription lists.

---

## 2. Technical Contracts

### 2.1 Architecture

```text
Handler
    ↓
mail = Mail(schema)
mail.send("notification", mail_data, layout_data)
    ↓
    ├── Mail._prepare_mail_data()
    ├── MailTemplate.render()
    └── MailSend.send()
```

Layout resolution is dynamic:

1. the provider component calls `set_current_mail_template()` and registers
   `schema["data"]["current"]["mail_template"]["dir"]`;
2. the user sets `MAIL_TEMPLATE_NAME` in `.env` (default `index.ntpl`);
3. `core/schema.py` builds `MAIL_TEMPLATE_LAYOUT` from that directory plus
   `MAIL_TEMPLATE_NAME`;
4. `Mail.__init__` reads `MAIL_TEMPLATE_LAYOUT` from the schema.

The provider may offer multiple layouts (`index.ntpl`, `minimal.ntpl`,
`cache.ntpl`, and so on). `Mail` does not know those names in advance.

### 2.2 Configuration

#### Environment variables

| Variable | Default | Description | Type |
|----------|---------|-------------|------|
| `MAIL_METHOD` | `smtp` | `smtp`, `sendmail`, or `file` | Config |
| `MAIL_SERVER` | `` | SMTP server | Config |
| `MAIL_PORT` | `587` | SMTP port | Config |
| `MAIL_USERNAME` | `` | SMTP auth username | Config |
| `MAIL_PASSWORD` | `` | SMTP password | Secret |
| `MAIL_USE_TLS` | `false` | Enable STARTTLS | Config |
| `MAIL_SENDER` | `` | Default sender | Config |
| `MAIL_RETURN_PATH` | `` | Return-Path for sendmail | Config |
| `MAIL_TO_FILE` | `/tmp/test_mail.html` | Output path in `file` mode | Config |
| `MAIL_TEMPLATE_NAME` | `index.ntpl` | Mail layout filename | Config |

`Config.TEMPLATE_MAIL` as a hardcoded path is obsolete. The effective layout
must be resolved through `MAIL_TEMPLATE_LAYOUT` in the schema.

### 2.3 Class APIs

#### `Mail`

```python
class Mail:
    def __init__(self, schema: dict, tpl: str = None) -> None:
        self.schema = schema
        self.data = schema["data"]
        self.tpl = tpl or self.data["MAIL_TEMPLATE_LAYOUT"]

    def send(
        self,
        content_template: str,
        mail_data: dict,
        layout_data: dict = None
    ) -> dict:
        ...
```

`mail_data` must include at least:

- `to`
- `subject`

It may optionally include:

- `from`
- any template variables such as `pin`, `token`, `alias`, and similar fields.

If the same key exists in both `layout_data` and `mail_data`, `mail_data`
wins.

#### `MailTemplate`

```python
class MailTemplate:
    def __init__(self, schema: dict) -> None: ...

    def render(self, tpl: str) -> str:
        ...
```

It uses `NeutralTemplate` or `NeutralIpcTemplate` depending on
`Config.NEUTRAL_IPC`, matching the web template flow.

#### `MailSend`

```python
class MailSend:
    def __init__(self) -> None:
        self.method = Config.MAIL_METHOD

    def send(
        self,
        mail_data: dict,
        html_body: str,
        text_body: str = None
    ) -> dict:
        ...
```

The sender is resolved as:

`mail_data.get("from") or Config.MAIL_SENDER`

### 2.4 Mail templates

The concrete template structure is owned by the provider component. This
system only consumes the resolved layout through `MAIL_TEMPLATE_LAYOUT`.

Typical layouts consume the selected content through:

```ntpl
{:^include; {:flg; require :} >> #/{:;current_mail->content_template:}-snippets.ntpl :}
```

So `current_mail["content_template"]` becomes the contract between the caller
and the provider layout.

---

## 3. Behavior

### 3.1 Send flow

1. the caller creates `Mail(schema)`;
2. `Mail._prepare_mail_data()` writes `schema["data"]["current_mail"]`;
3. `MailTemplate.render()` renders the provider layout to HTML;
4. `Mail._html_to_text()` derives a plain-text fallback;
5. the system builds a `multipart/alternative` MIME message;
6. headers such as `From`, `To`, `Subject`, `Return-Path`, and `X-Mailer` are
   set;
7. `MailSend.send()` dispatches through the configured method;
8. the method returns `{"success": ..., "message_id": ..., "error": ...}`.

### 3.2 Preparing `current_mail`

The merge contract is:

```python
def _prepare_mail_data(content_template, mail_data, layout_data=None):
    self.data["current_mail"] = {
        "content_template": content_template,
        **(layout_data or {}),
        **mail_data,
    }
```

Responsibilities are split as follows:

- **`Mail`** validates the required transport fields and performs orchestration;
- **the caller** supplies business data and template variables;
- **the provider component** documents and consumes any optional layout data;
- **the template** may provide defaults through `{:else; ... :}`.

### 3.3 Retries and errors

| Error type | Behavior |
|------------|----------|
| Temporary `SMTPException` | Retry with exponential backoff, up to 3 times |
| Permanent `SMTPException` (5xx) | Fail immediately |
| Connection timeout | Retry |
| Sendmail pipe error | Retry |
| Any other exception | Return `{"success": False, "error": str(e)}` and do not raise |

### 3.4 `file` transport

When `MAIL_METHOD=file`, the rendered HTML is written to `Config.MAIL_TO_FILE`
so it can be inspected without a real SMTP server.

---

## 4. Security

### 4.1 Controls

- [x] SMTP should use STARTTLS when `MAIL_USE_TLS=true`;
- [x] `MAIL_PASSWORD` must never be logged;
- [x] one-time tokens or PINs placed in emails must be expired and invalidated
  by the caller;
- [x] sender and return-path handling must avoid spoofing surprises.

### 4.2 Risks

| Risk | Mitigation | Level |
|------|------------|-------|
| Email interception | TLS for SMTP transport | High |
| Enumeration via email-trigger flows | Generic UI messages | Medium |
| Token replay | Short expiration and single-use semantics | High |

---

## 5. Implementation

### 5.1 Dependency: `set_current_mail_template()` in `app/components.py`

The helper is analogous to `set_current_template()`. It registers the provider
directory in the schema and does **not** write `MAIL_TEMPLATE_LAYOUT`
directly.

```python
def set_current_mail_template(component, component_schema):
    template_dir = os.path.join(component["path"], "neutral")

    component_schema.setdefault("data", {})
    component_schema["data"].setdefault("current", {})
    component_schema["data"]["current"]["mail_template"] = {
        "dir": template_dir
    }

    return template_dir
```

Then `core/schema.py` builds `MAIL_TEMPLATE_LAYOUT`:

```python
if "mail_template" in self.data["current"]:
    mail_template_dir = self.data["current"]["mail_template"]["dir"]
    self.data["MAIL_TEMPLATE_LAYOUT"] = os.path.join(
        mail_template_dir, "layout", Config.MAIL_TEMPLATE_NAME
    )
```

### 5.2 `NeutralTemplate` vs `NeutralIpcTemplate`

`MailTemplate.render()` follows the same split as the web renderer:

```python
if Config.NEUTRAL_IPC:
    template = NeutralIpcTemplate(tpl, schema_msgpack, ...)
else:
    template = NeutralTemplate(tpl, schema_obj=self.schema)
html = template.render()
```

### 5.3 Sending from a handler

```python
from core.mail import Mail

mail = Mail(self.schema_data)

mail_data = {
    "to": recipient_email,
    "subject": "Message subject",
    "from": Config.MAIL_SENDER,
    "token": some_token,
    "code": verification_code,
}

layout_data = {
    "logo": self.schema_data["data"]["current"]["site"]["logo"],
    "url_home": self.schema_data["data"]["current"]["site"]["url"],
}

result = mail.send("notification", mail_data, layout_data)
```

Minimal call without `layout_data`:

```python
mail = Mail(self.schema_data)
result = mail.send("alert", {
    "to": user_email,
    "subject": "Important notification",
    "message": "Body content",
})
```

---

## 6. Testing

### 6.1 Required test cases

- [ ] successful SMTP send with TLS;
- [ ] local `sendmail` transport works;
- [ ] `file` transport writes HTML to `MAIL_TO_FILE`;
- [ ] NTPL rendering uses the correct locale;
- [ ] the email contains both text and HTML parts;
- [ ] temporary failures trigger retries;
- [ ] permanent failures do not retry;
- [ ] `send()` never raises and always returns a dict.

---

## 7. Acceptance Criteria

- [x] `Mail(schema, tpl=None)` accepts a schema and avoids hardcoded paths;
- [x] `Mail.send(content_template, mail_data, layout_data=None)` uses a simple
  consumer-facing API;
- [x] `MAIL_TEMPLATE_LAYOUT` is built by `core/schema.py` from the registered
  provider directory;
- [x] responsibilities stay split across `Mail`, `MailTemplate`, and
  `MailSend`;
- [x] SMTP, sendmail, and `file` transports are supported;
- [x] temporary failures may be retried;
- [x] TLS is used when configured;
- [x] `send()` always returns a structured result dict.

---

## 8. Impact

### 8.1 Mail-system actors

| Actor | Role | Usage |
|-------|------|-------|
| Mail template provider component | Provider | Registers directory and defines layout/snippets/locale |
| Any handler or component | Consumer | Calls `Mail.send(...)` |
| `core/mail.py` | Transport system | `Mail`, `MailTemplate`, `MailSend` |
| `app/components.py` | Infrastructure | `set_current_mail_template()` |

---

## 9. Decisions

### 9.1 Architectural decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| `Mail(schema, tpl=None)` | Same pattern as `Template(schema)` | Consistent framework API |
| `MAIL_TEMPLATE_LAYOUT` in schema | Mirrors `TEMPLATE_LAYOUT` for web | Provider can change without touching `core/mail.py` |
| Three separate classes | Better SRP and testability | Rendering and transport stay isolated |
| `send(content_template, mail_data, layout_data=None)` | Simple API for callers | Business code owns subject and variables |
| Subject from `mail_data` | Business context belongs to the caller | `core/mail.py` stays template-agnostic |
| NTPL for mail | Consistency with web templates | Shared i18n conventions |
| No persistent queue | Simplicity | Retries remain in-memory only |
| `multipart/alternative` | Maximum client compatibility | Dual text/HTML generation |

### 9.2 Implementation dependencies

| Order | System or component | Description |
|-------|----------------------|-------------|
| 1 | `app/components.py` | Provide `set_current_mail_template()` |
| 2 | Mail template provider component | Register itself in `init_component()` |
| 3 | `core/mail.py` | Implement the three-class split |
| 4 | Any consumer | Call `Mail.send(...)` as needed |

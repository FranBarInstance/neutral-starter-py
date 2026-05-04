# 010-mail-system - Mail Template Provider Requirements

## Executive Summary

This document defines the **interface contract** between the mail system
(`010-mail-system`) and any component that wants to provide email templates.

It is **not** a full template-system design specification. It only defines
what the mail subsystem expects from the active provider.

The provider is free to choose:

- internal file structure;
- rendering strategy (snippets, full templates, inline rendering);
- visual design, branding, and i18n;
- the organization of any required `layout_data`.

---

## 1. Mandatory Requirements

### 1.1 Schema registration

The provider must call `set_current_mail_template()` from its
`init_component()`:

```python
from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    set_current_mail_template(component, component_schema)
```

This registers `schema["data"]["current"]["mail_template"]["dir"]`.

### 1.2 Multiple providers: last one wins

Multiple active components may call `set_current_mail_template()`. The last
component that does so becomes the active provider.

This allows:

- overriding the default provider without editing it;
- application-specific specialization through installed components;
- choosing the provider through component activation and load order.

The choice happens at startup and remains static for the process lifetime.
`Mail.send()` does not know which provider is active; it only consumes
`MAIL_TEMPLATE_LAYOUT` from the schema.

### 1.3 Layout existence

The provider must expose an NTPL file at:

```text
{mail_template_dir}/layout/{MAIL_TEMPLATE_NAME}
```

By default:

```text
{mail_template_dir}/layout/index.ntpl
```

This is the entry point rendered by `MailTemplate.render()`.

---

## 2. Data Available in the Schema

### 2.1 `current_mail`

Location:

`schema["data"]["current_mail"]`

Minimum structure:

```python
{
    "content_template": str,
    # optional merge of layout_data
    # required merge of mail_data
}
```

### 2.2 Variables available to the layout

| Variable | Source | Description |
|----------|--------|-------------|
| `current_mail->content_template` | `Mail.send()` | Content identifier to render |
| `current_mail->to` | `mail_data["to"]` | Recipient |
| `current_mail->subject` | `mail_data["subject"]` | Subject |
| `current_mail->from` | `mail_data.get("from")` | Sender |
| `current_mail->*` | `mail_data`, `layout_data` | Additional caller-provided variables |
| `current->mail_template->dir` | `set_current_mail_template()` | Provider base directory |
| `MAIL_TEMPLATE_LAYOUT` | `core/schema.py` | Resolved full layout path |

---

## 3. Layout Responsibilities

### 3.1 Consume `content_template`

The layout must use `current_mail->content_template` to decide what content to
render.

Valid strategies include:

**A. Snippet strategy**

```ntpl
{:^include; {:flg; require :} >> #/{:;current_mail->content_template:}-snippets.ntpl :}
```

**B. Full-template strategy**

```ntpl
{:^include; {:flg; require :} >> #/{:;current_mail->content_template:}.ntpl :}
```

**C. Inline snippet strategy**

```ntpl
{:snip; {:;current_mail->content_template:} :}
```

### 3.2 Handle defaults

The layout should use `{:else; ... :}` to provide defaults when the caller
does not pass `layout_data`:

```ntpl
{:;current_mail->logo:}{:else; {:;current->site->logo:} :}
```

### 3.3 Email presentation

The provider is responsible for:

- HTML email structure and compatibility;
- CSS strategy, taking email-client limitations into account;
- consuming available mail variables coherently;
- optionally relying on `Mail._html_to_text()` for the plain-text fallback.

---

## 4. Optional Recommended Requirements

### 4.1 Internationalization

Supporting `locale.json` next to the mail layout is recommended.

### 4.2 Local data

Supporting `local-data.json` for visual defaults such as colors or logos is
recommended.

### 4.3 `layout_data` documentation

The provider should document which optional `layout_data` keys it expects.

---

## 5. Minimal Implementation Example

### 5.1 Component registration

```python
from app.components import set_current_mail_template

def init_component(component, component_schema, _schema):
    set_current_mail_template(component, component_schema)
```

### 5.2 Minimal layout

```text
neutral/
  layout/
    index.ntpl
```

```ntpl
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{:;current_mail->subject:}</title>
</head>
<body>
    {:^include; {:flg; require :} >> #/{:;current_mail->content_template:}.ntpl :}
</body>
</html>
```

---

## 6. Normative References

- `spec.md` (`010-mail-system`) - mail transport system
- `specs/002-neutral-templates-standard/spec.md` - NTPL syntax
- `specs/009-i18n-standard/spec.md` - internationalization

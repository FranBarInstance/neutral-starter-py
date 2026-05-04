# Standard Forms Specification

## Executive Summary

Forms in this project follow an **AJAX-first** pattern. Forms are submitted and
processed through `{:fetch; ... :}` without full-page reloads, except for
explicit success flows that require a global state transition such as login.
Validation lives declaratively in `route/schema.json`; the backend inherits
`FormRequestHandler` and executes a strict sequence of token validation,
field validation, business logic, and conditional rendering.

This specification is normative. New forms must follow it, and code review may
cite it as the source of truth.

## Goals

- AJAX by default;
- smooth asynchronous UX;
- declarative validation in route schema, not ad hoc Python checks;
- strong security through LTOKEN, CSRF, FTOKEN, rate limiting, and honeypots;
- fail-closed behavior;
- immediate field-level and form-level feedback without losing form state;
- handler/template separation of responsibilities.

## Normative References

- `specs/002-neutral-templates-standard/spec.md`
- `specs/001-component-standard/spec.md`
- `specs/000-core-system/spec.md`
- `docs/templates-neutrats-ajax.md`
- `.agents/skills/manage-ajax-forms/SKILL.md`

---

## 1. Form Data Structure (`route/schema.json`)

Each form is defined under `data.current_forms.<form_name>` inside the
component route schema.

### 1.1 General structure

```json
{
  "data": {
    "current_forms": {
      "<form_name>": {
        "check_fields": ["field1", "field2"],
        "validation": {
          "minfields": 2,
          "maxfields": 5,
          "allow_fields": ["field1", "field2", "send", "ftoken.*"]
        },
        "rules": {
          "field1": {
            "required": true,
            "minlength": 3,
            "maxlength": 50,
            "pattern": "^\\S+$",
            "regex": "^\\S+$"
          }
        }
      }
    }
  }
}
```

### 1.2 Configuration fields

| Key | Type | Description |
|---|---|---|
| `check_fields` | `string[]` | Fields validated one by one. |
| `validation.minfields` | `int` | Minimum number of submitted POST fields. |
| `validation.maxfields` | `int` | Maximum number of submitted POST fields. |
| `validation.allow_fields` | `string[]` | Allowed POST/FILE field names. Supports `fnmatch` patterns such as `ftoken.*`. |
| `rules.<field>` | `object` | Per-field validation rules. |

### 1.3 Field validation rules

| Rule | Purpose |
|---|---|
| `required` | Required in HTML and backend validation. |
| `minlength` / `maxlength` | Length validation in HTML and backend. |
| `pattern` | Native browser validation pattern. |
| `regex` | Backend regular expression check. |
| `value` | Exact expected value. |
| `set` | Field presence or absence requirement; useful for honeypots. |
| `match` | Must match another field. |
| `dns` | DNS lookup requirement for values such as emails. |
| `minage` / `maxage` | Age validation for `YYYY-MM-DD` dates. |

### 1.4 File validation rules

| Rule | Description |
|---|---|
| `required_file` | At least one file must be present. |
| `minfiles` / `maxfiles` | Minimum and maximum number of files. |
| `multiple` | Whether multiple files are allowed. |
| `max_file_size` | Max size per file. |
| `max_total_file_size` | Max total upload size. |
| `allowed_mime` | Allowed MIME list. |
| `allowed_extensions` | Allowed extension list. |

### 1.5 Notes

- `pattern` is for browser-side validation;
- `regex` is for backend-side validation;
- if FTOKEN is used, `allow_fields` must include `ftoken.*`.

---

## 2. Backend Lifecycle

### 2.1 Inheritance and responsibilities

Every form handler must inherit from `core.request_handler_form.FormRequestHandler`.
It provides:

- LTOKEN validation for GET and POST;
- schema-driven field validation;
- structured error management;
- `validate_get()` and `validate_post(error_prefix)` fail-closed flow.

### 2.2 GET validation flow

`validate_get()` performs token validation for the initial form-render path.
If validation fails, the form must not proceed as valid.

### 2.3 POST validation flow

`validate_post(error_prefix)` must follow this sequence:

1. `valid_form_tokens_post()`
2. `valid_form_validation()`
3. `any_error_form_fields(error_prefix)`
4. business logic only if all previous steps pass

#### Step 1: `valid_form_tokens_post()`

Validates LTOKEN and CSRF-related requirements. Failure stops the flow.

#### Step 2: `valid_form_validation()`

Validates:

- `minfields`
- `maxfields`
- `allow_fields`

Failure sets a form-level validation error.

#### Step 3: `any_error_form_fields(error_prefix)`

Iterates over `check_fields` and applies the configured rules. Field errors are
stored under the handler error structure using stable error keys.

#### Step 4: Business logic

This step must run only when the previous steps return success.

### 2.4 Errors and results

The handler owns the structured error/result state. Templates decide how to
render:

- form-level token or validation errors;
- field-level errors;
- success states;
- partial fragment replacement.

### 2.5 Typical handler implementation

A form handler should:

1. inherit from `FormRequestHandler`;
2. expose `get()` and/or `post()` methods;
3. call shared validation helpers first;
4. execute business logic only when validation passed;
5. return schema state for NTPL rendering.

### 2.6 Flask routes

Typical route sets include:

- full-page GET form page;
- AJAX GET form fragment;
- AJAX POST submission endpoint.

---

## 3. Template Architecture (NTPL)

### 3.1 Recommended directory structure

Forms usually combine:

- component `neutral/route/index-snippets.ntpl`
- optional shared `form-snippets.ntpl`
- route `content-snippets.ntpl`
- optional route-local `ajax/content-snippets.ntpl`

### 3.2 Form utilities

Reusable form snippets should live in shared snippets, often with support from
the form utility component.

### 3.3 Field error snippets

Field-specific snippets should read the handler error state and render localized
messages without duplicating validation logic in the template.

### 3.4 Form snippet with `{:fetch; ... :}`

AJAX forms must use `{:fetch; ... :}` as the primary interaction mechanism.

### 3.5 Coalesce container pattern

The container snippet should be able to render:

- the initial form;
- validation errors;
- success output;
- replacement fragments without losing local form state.

### 3.6 Full-page route template

The route `content-snippets.ntpl` must still define
`current:template:body-main-content`, even when the form itself is mostly AJAX.

### 3.7 AJAX route template

AJAX route fragments should return only the fragment needed by the target,
typically through the same coalesce/container snippet.

---

## 4. Security and Control

### 4.1 LTOKEN

LTOKEN protects the form flow and must be validated for GET and POST where the
handler contract requires it.

### 4.2 CSRF

CSRF protection is mandatory for state-changing form submissions.

### 4.3 FTOKEN

FTOKEN is the anti-bot token family used in supported form flows.

### 4.4 Honeypot

Honeypot fields should use rules such as `set: false` and must be included in
the schema contract when used.

### 4.5 Rate limiting

Sensitive form routes must apply the relevant rate limits.

### 4.6 CSP and nonce

Form templates must remain CSP-compatible and avoid unsafe inline patterns.

---

## 5. `{:fetch;}` Reference

### 5.1 Syntax

`{:fetch; ... :}` is the standard AJAX interaction primitive for forms and
fragment refreshes.

### 5.2 Events

Implementations may bind lifecycle behavior around fetch-driven fragment
replacement, but must remain consistent with the project's CSP and progressive
enhancement rules.

### 5.3 Patterns

Typical patterns include:

- load form fragment on demand;
- submit via AJAX POST;
- replace target container with returned fragment;
- keep form state and errors local to the component.

---

## 6. Modal Integration

### 6.1 Modal definition

Forms inside modals must still follow the same schema, validation, and AJAX
contracts.

### 6.2 Modal AJAX flow

The modal body should be refreshable through the same fragment return pattern as
non-modal forms.

### 6.3 Modal location

Modal markup should integrate through the shared template snippet system rather
than bypassing the route/layout contract.

---

## 7. Guidance for AI Agents

### 7.1 Imperative rules

- default to AJAX for new forms;
- keep validation in route schema, not duplicated in Python and NTPL;
- use `FormRequestHandler`;
- preserve fail-closed order;
- do not bypass LTOKEN/CSRF/FTOKEN mechanics.

### 7.2 Review checklist

- is the form AJAX-first?
- are schema rules complete?
- is the handler fail-closed?
- are field and form errors renderable through snippets?
- are rate limits and anti-bot protections appropriate?

---

## 8. Common Errors and Troubleshooting

- missing allowed fields cause validation rejection;
- missing `ftoken.*` in `allow_fields` breaks anti-bot validation;
- skipping the handler validation sequence causes unsafe business execution;
- returning a full page instead of a fragment breaks AJAX replacement flows.

---

## 9. Acceptance Criteria

- [x] forms are AJAX-first by default;
- [x] validation is declarative in `route/schema.json`;
- [x] handlers inherit from `FormRequestHandler`;
- [x] token validation happens before business logic;
- [x] templates render errors and success without duplicating backend logic;
- [x] security controls include LTOKEN, CSRF, and other required protections.

# Component: name_XXXXXX

> **Note**: The UUID is the stable component identifier. The folder name
> (`cmp_NNNN_*`) is dynamic and may change; never use it as the functional
> reference in specs, tests, or documentation.

## Executive Summary

> Describe in 2-3 sentences what functionality this component isolates.
> Example: "This component provides image album management, including CRUD
> operations, file validation, and gallery rendering."

## Identity

- **UUID**: `name_XXXXXX` — Stable identifier, never changes.
  - **Requirements**: `name_random` format (example: `default_0yt2sa`)
  - Length: 10-50 characters
  - Allowed characters: `a-z`, `0-9`, `_`
  - Must contain at least one `_`
  - All lowercase
- **Version**: `X.Y.Z`
- **Base Route**: `<manifest.route>` (value from `manifest.json`, example: `/album`)
- **Status**: [Active / Development / Maintenance]
- **Current Folder** (reference only): `cmp_NNNN_name` — subject to change, do not use as identity in specs

## Normative References

- `.specify/memory/constitution.md` — Immutable principles.
- [Relevant system specs]
- [Applicable agent skills: `manage-component`, `manage-ajax-forms`, etc.]
- [Component documentation in `docs/`, if applicable]

---

## 1. Objectives and Scope

### 1.1 Component Responsibility

[Clear description of what this component does and what it does NOT do]

### 1.2 Objectives

- Objective 1
- Objective 2
- Objective 3

### 1.3 Non-Objectives (Explicit Boundaries)

- Functionality it does NOT include
- Dependencies it does NOT manage
- Unsupported use cases

---

## 2. Architecture

### 2.1 Directory Structure

```text
src/component/cmp_NNNN_name/
├── manifest.json                         # Identity and metadata (required)
├── schema.json                           # Configuration, menus, i18n, global data
├── custom.json                           # Local overrides (if applicable)
├── __init__.py                           # Component initialization (if applicable)
├── README.md                             # Operational documentation
├── .specify/
│   ├── spec.md                           # Component SDD contract
│   └── data-model.md                     # Only if it introduces/changes persistence
├── route/
│   ├── __init__.py                       # Blueprint init
│   ├── routes.py                         # Flask route definitions
│   ├── schema.json                       # Form / route-handler rules
│   └── [handler].py                      # Specialized request handlers
├── neutral/
│   ├── component-init.ntpl               # App-wide snippets (optional)
│   ├── obj/
│   │   └── object.json                   # Neutral objects (if applicable)
│   └── route/
│       ├── index-snippets.ntpl           # Auto-loaded for component routes
│       ├── form-snippets.ntpl            # Shared forms (if applicable)
│       ├── locale-en.json                # Per-language translations
│       ├── locale-es.json
│       ├── locale-fr.json
│       ├── locale-de.json
│       ├── data.json                     # Shared route data (if applicable)
│       └── root/
│           ├── data.json                 # Base-route metadata
│           ├── content-snippets.ntpl     # Base-route content
│           └── [subroute]/
│               ├── data.json             # Subroute metadata
│               ├── content-snippets.ntpl # Subroute content
│               └── ajax/
│                   └── content-snippets.ntpl
├── model/
│   └── [model].json                      # Declarative JSON models
├── static/                               # Component static assets
│   ├── css/
│   ├── js/
│   └── img/
├── src/
│   └── [module].py                       # Python functions for templates (if applicable)
├── lib/
│   └── [uuid_or_namespace]/              # Private libraries (if applicable)
└── tests/
    ├── conftest.py
    └── test_*.py
```

### 2.2 Component Diagram

```text
[User/Browser]
    ↓
[Flask Blueprint: <manifest.route>]
    ↓
[RequestHandler/FormRequestHandler]
    ↓
[Data model] <-> [Database]
    ↓
[NTPL Template] -> [Rendered output]
```

### 2.3 Dependencies

| Type | Dependency | UUID | Notes |
|------|-------------|------|-------|
| Requires | Component X | `uuid_xxx` | For functionality Y |
| Provides | API Z | — | Used by other components |

---

## 3. Routes and Handlers

### 3.1 Route Table

| Route | Method | Handler | Auth | Role | Description |
|------|--------|---------|------|-----|-------------|
| `/` | GET | `PageHandler` | — | — | Main page |
| `/list` | GET | `ListHandler` | Yes | `user` | Item list |
| `/ajax/<ltoken>` | GET/POST | `AjaxHandler` | Yes | `user` | AJAX form |

### 3.2 Security Configuration (`manifest.json`)

```json
{
  "security": {
    "routes_auth": {
      "/": false,
      "/list": true,
      "/ajax": true,
      "/admin": true
    },
    "routes_role": {
      "/": ["*"],
      "/list": ["user"],
      "/ajax": ["user"],
      "/admin/*": ["admin"]
    }
  }
}
```

---

## 4. Data and Models

### 4.1 Validation Schema (`schema.json`)

```json
{
  "data": {
    "current_forms": {
      "example_form": {
        "check_fields": ["field1", "field2"],
        "validation": {
          "minfields": 2,
          "maxfields": 5,
          "allow_fields": ["field1", "field2", "send"]
        },
        "rules": {
          "field1": {
            "required": true,
            "minlength": 3,
            "maxlength": 50
          }
        }
      }
    }
  }
}
```

### 4.2 Data Models (`model/*.json`)

| Model | Purpose | Main Structure |
|--------|-----------|----------------------|
| `model/entity.json` | Description | `{ "id": int, "name": str, ... }` |

---

## 5. NTPL Templates

### 5.1 Main Snippets

| Snippet | Location | Purpose |
|---------|-----------|-----------|
| `cmp_uuid:content` | `content-snippets.ntpl` | Main page content |
| `cmp_uuid:form-container` | `form-snippets.ntpl` | Form container with Coalesce |
| `cmp_uuid:modals` | `index-snippets.ntpl` | Modal definitions |

### 5.2 Template Data Structure

```json
{
  "inherit": {
    "data": {
      "current": {
        "route": {
          "title": "Page title",
          "description": "Meta description",
          "h1": "Visible heading"
        }
      }
    }
  },
  "data": {
    "custom_data": "Component-specific value"
  }
}
```

Notes:

- if these values are defined in a route or subroute `data.json`, they are
  consumed in templates as `local::current->route->...`
- if the component needs global defaults that the base template consumes and
  that must remain dynamically overridable, they should be defined in
  `inherit.data`
- the base layout especially expects `current.route.title`,
  `current.route.description`, and `current.route.h1`
- each route `content-snippets.ntpl` must define
  `current:template:body-main-content`

Typical route `data.json` example:

```json
{
  "data": {
    "current": {
      "route": {
        "title": "Page title",
        "description": "Meta description",
        "h1": "Visible heading"
      }
    },
    "custom_data": "Route-specific value"
  }
}
```

### 5.3 AJAX Forms

| Form | Schema Key | Handler | `{:fetch;}` Event |
|------------|------------|---------|------------------|
| Form 1 | `form_1` | `Form1Handler` | `\|url\|form\|...\|` |

---

## 6. Static Assets

### 6.1 CSS

| File | Location | Purpose |
|---------|-----------|-----------|
| `component.css` | `static/css/` | Component-specific styles |

### 6.2 JavaScript

| File | Location | Purpose | CSP Nonce |
|---------|-----------|-----------|-----------|
| `component.js` | `static/js/` | Client-side logic | Required |

### 6.3 Images

| Resource | Location | Use |
|---------|-----------|-----|
| `icon.svg` | `static/img/` | Component icon |

---

## 7. Security

### 7.1 Security Matrix

| Aspect | Implementation | Verification |
|---------|----------------|--------------|
| Authentication | `routes_auth` in manifest | [ ] Protected routes |
| Authorization | `routes_role` in manifest | [ ] Roles verified |
| CSP | Nonce on inline scripts | [ ] `{:;CSP_NONCE:}` used |
| Forms | `LTOKEN` + `FTOKEN` | [ ] Tokens validated |
| Rate Limit | `@limiter.limit()` | [ ] Decorator applied |
| Input Validation | `schema.json` + handlers | [ ] Complete validation |
| Output Encoding | `{:trans; :}`, `{:allow; :}` | [ ] No XSS |

### 7.2 Risk Analysis

| Risk | Probability | Impact | Mitigation |
|--------|--------------|---------|------------|
| [Specific risk] | High/Medium/Low | High/Medium/Low | [Strategy] |

---

## 8. Testing

### 8.1 Testing Strategy

| Type | Location | Coverage |
|------|-----------|-----------|
| Unit | `tests/` | Handlers, helpers, auxiliary functions |
| Integration | `tests/` | Routes, templates, component contracts |
| E2E | `[if applicable]` | User flows outside unit/integration scope |

### 8.2 Critical Test Cases

- [ ] **TC1**: [Description of test case 1]
- [ ] **TC2**: [Description of test case 2]
- [ ] **TC3**: [Description of test case 3]

### 8.3 Execution Commands

```bash
source .venv/bin/activate

# Component tests
pytest src/component/<component-folder>/tests -v

# Current component tests with shorter traceback
pytest src/component/<component-folder>/tests -v --tb=short

# Localized coverage
pytest src/component/<component-folder>/tests --cov=src/component/<component-folder> --cov-report=html
```

Stability rules:

- do not assume that the `cmp_NNNN_name` folder name is stable
- resolve the component root from `Path(__file__).resolve().parents[...]`
- read `manifest.json` from that root
- derive the expected route from `manifest["route"]`
- build any file access relative to the computed root
- if a test needs to import component modules whose package depends on the
  folder name, construct that import dynamically

---

## 9. Acceptance Criteria

### 9.1 Functional

- [ ] All routes respond according to the specification
- [ ] AJAX forms work without full page reload
- [ ] Field validation follows `schema.json`
- [ ] Error messages are translated (`{:trans; :}`)

### 9.2 Technical

- [ ] Correct handler inheritance (`FormRequestHandler` when applicable)
- [ ] Stable identity by UUID (not folder name)
- [ ] Base routes derived from `<manifest.route>`
- [ ] No absolute system paths in code

### 9.3 Security

- [ ] Complete `routes_auth` and `routes_role` in `manifest.json`
- [ ] CSP nonce on inline scripts
- [ ] Rate limiting on POST routes
- [ ] LTOKEN/FTOKEN token validation

### 9.4 Quality

- [ ] Test coverage >= [X]%
- [ ] `pylint` with no critical errors
- [ ] `mypy` passes without errors
- [ ] Documentation complete

---

## 10. Operations

### 10.1 Deployment

| Action | Command/Procedure |
|--------|----------------------|
| Install | The active component loads automatically if its folder starts with `cmp_` |
| Enable | Use a `cmp_NNNN_name` folder |
| Disable | Rename the folder out of the `cmp_*` pattern, usually `_cmp_NNNN_name` |

### 10.2 Monitoring

| Metric | Tool | Alert |
|---------|-------------|--------|
| [Metric] | [Tool] | [Condition] |

### 10.3 Troubleshooting

| Symptom | Probable Cause | Solution |
|---------|----------------|----------|
| [Symptom] | [Cause] | [Steps] |

---

## 11. Change History

| Date | Version | Change | Author |
|-------|---------|--------|-------|
| YYYY-MM-DD | X.Y.Z | Description | Name |

---

*Template: component/spec.md*  
*Last updated: [YYYY-MM-DD]*

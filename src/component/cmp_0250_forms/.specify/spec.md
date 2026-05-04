# Component: forms_0yt2sa

## Executive Summary

Cross-cutting component that provides visual infrastructure and logic for form handling across the entire system. Has no user routes, but its snippets are essential for error display, token validation, and design consistency in any application form.

## Identity

- **UUID**: `forms_0yt2sa`
- **Base Route**: `` (no routes - provides snippets only)
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

## Architecture

### Component Type
**Cross-cutting snippets** component (no routes, no handlers, provides shared NTPL snippets).

### Directory Structure

```
src/component/cmp_NNNN_forms/
├── manifest.json          # Identity and security
├── schema.json            # Form styling configuration
└── neutral/
    ├── snippets.ntpl      # Core form snippets (errors, tokens, utilities)
    ├── locale.json        # Translations for error messages
    ├── country-snippets.ntpl   # Country selector snippets
    └── language-snippets.ntpl  # Language selector snippets
```

### Dependencies

- **No dependencies**: Self-contained snippet library
- **Used by**: Any component with forms (sign, user, etc.)

## Snippet Interface (Template API)

### 1. Token Error Management

| Snippet | Purpose |
|---------|---------|
| `forms:error-validation:true` | General form validation error alert |
| `forms:error-ftoken:true` | Form token (FTOKEN) failure alert |
| `forms:error-ltoken:true` | Link token (LTOKEN) failure alert (session security) |
| `forms:error-utoken` | User token error (delegates to `util:error-utoken`) |

### 2. Field Error Generation

**`forms:set-form-field-error`** - Core snippet that dynamically generates two sub-snippets given `field` and `msg` parameters:
- `is-invalid:{field}`: Returns CSS error class
- `error-msg:{field}`: Generates error message HTML with contextual help link

### 3. Form Utilities

| Snippet | Purpose |
|---------|---------|
| `forms:redirect-if-session` | Redirects to home if session detected (for login/register pages) |
| `forms:field-is-invalid` | Returns CSS error class constant (`text-danger`) |
| `form:field-error` | Generic field error display |

### 4. Client-side Logic (JS)

Injects global `formsAutoselectOption` function that:
- Finds `<select>` elements with `data-forms-autoselect-option` attribute
- Auto-selects the indicated value after DOM load or AJAX completion (`neutralFetchCompleted` event)

## Configuration (`schema.json`)

Injects values into schema for global form styling control:

| Key | Default | Purpose |
|-----|---------|---------|
| `current->forms->_class` | `forms-bt5-clean border border-0` | Base class for form containers |
| `current->forms->field-spacing` | `mb-2` | Bottom margin between fields |
| `current->forms->field-send-spacing` | `mt-3` | Top margin for submit button |

## Technical Rationale

- **Cross-cutting**: Centralizing error messages ensures any policy change reflects instantly across the entire application
- **Security**: Provides clear but generic messages on token failures, guiding users without exposing internal details

---

## Acceptance Criteria (SDD)

### Functional
- [x] Provides `forms:error-*` snippets for token and validation errors
- [x] `forms:set-form-field-error` generates dynamic error snippets correctly
- [x] `forms:redirect-if-session` handles session detection and redirects
- [x] `formsAutoselectOption` JavaScript function works on DOM load and AJAX
- [x] Translations available for all error messages via `locale.json`

### Technical
- [x] No routes exposed (empty base route)
- [x] No Python code (handlers, models)
- [x] CSP-compliant inline script with nonce
- [x] Bootstrap 5 compatible styling classes

### Integration
- [x] Snippets usable by any form component
- [x] Schema values inject correctly into `schema_local_data`
- [x] Delegates `error-utoken` to `util:error-utoken` snippet

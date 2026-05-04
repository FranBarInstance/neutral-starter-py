# Component: forms_0yt2sa

Cross-cutting form infrastructure component.

## Overview

This component provides shared snippets for form handling across the entire application. It centralizes error display, token validation messages, and form styling.

## Structure

- `manifest.json` - Component identity
- `schema.json` - Form styling configuration (classes, spacing)
- `neutral/snippets.ntpl` - Core form snippets (errors, tokens, utilities)
- `neutral/locale.json` - Translations for error messages
- `neutral/country-snippets.ntpl` - Country selector snippets
- `neutral/language-snippets.ntpl` - Language selector snippets

## Available Snippets

### Error Management
- `forms:error-validation:true` - General validation error alert
- `forms:error-ftoken:true` - Form token error
- `forms:error-ltoken:true` - Link token error

### Field Errors
- `forms:set-form-field-error` - Generates error snippets for a field
- `forms:field-is-invalid` - CSS error class constant

### Utilities
- `forms:redirect-if-session` - Redirect if user has session

## Usage

Other components use these snippets in their forms:

```ntpl
{:snip; forms:error-ltoken:{:;myform->error->form->ltoken:} :}
{:snip; forms:set-form-field-error >> {:param; field :}email {:param; msg :}Invalid email:}
```

## Configuration

Form styling via `schema.json`:
- `current->forms->class` - Base form container class
- `current->forms->field-spacing` - Field margin
- `current->forms->field-send-spacing` - Submit button margin

# 009 - Internationalization System (i18n)

## Executive Summary

This specification defines the Neutral Starter Py internationalization system.
It supports interface, message, and content translation across multiple
languages using a language negotiation cascade, JSON translation files, and
translation extraction from NTPL templates.

The design is component-modular: each component may ship and maintain its own
translations while inheriting the shared locale framework.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/002-neutral-templates-standard/spec.md` - NTPL syntax including
  `{:trans; :}`.
- `specs/001-component-standard/spec.md` - component structure and locale
  files.
- `.agents/skills/translate-component/SKILL.md` - extraction and translation
  workflow.
- `src/component/cmp_0500_locale/` - locale management component.

---

## 1. Goals

### 1.1 What this system must achieve

- automatic selection of the most appropriate language;
- per-component translation ownership;
- extractable strings from templates;
- stable reference keys with `ref:...`;
- graceful fallback when a translation is missing.

### 1.2 Non-goals

- no machine translation service;
- no locale-aware date or number formatting layer;
- no first-class RTL support yet.

---

## 2. Technical Contracts

### 2.1 Language negotiation cascade

The active language is resolved in this order:

```text
1. Query string: ?lang=es
2. Cookie: locale=es
3. Accept-Language header
4. User profile locale
5. System default language
```

### 2.2 Translation file structure

#### System locales

```text
src/component/cmp_0500_locale/
└── route/
    └── locale-xx.json
```

#### Component locales

```text
src/component/cmp_NNNN_name/
└── route/
    ├── locale.json
    ├── locale-en.json
    ├── locale-es.json
    └── ...
```

#### JSON format

```json
{
    "Original Text": "Translated Text",
    "Another string": "Otra cadena",
    "ref:reference_key": "Reference-based translation"
}
```

### 2.3 NTPL usage

#### Direct translation

```html
<h1>{:trans; Welcome to our site :}</h1>
```

#### Reference-based translation

```html
<button>{:trans; ref:sign_in_button :}</button>
```

#### Variables

For variable-containing strings, use a reference key and resolve interpolation
outside direct literal translation:

```html
<p>{:trans; ref:welcome_user :}</p>
```

### 2.4 Schema structure

#### Available languages

```json
{
    "data": {
        "current": {
            "site": {
                "languages": ["en", "es", "fr"],
                "default_language": "en"
            }
        }
    }
}
```

#### Locale inheritance

```json
{
    "inherit": {
        "locale": {
            "current": "es",
            "trans": {
                "en": {},
                "es": {
                    "Sign in": "Sign in",
                    "Sign out": "Sign out"
                }
            }
        }
    }
}
```

---

## 3. Behavior

### 3.1 Translation resolution flow

1. determine the active language through the negotiation cascade;
2. load the relevant component locale file;
3. resolve either the literal string or `ref:key`;
4. if found, return the translated string;
5. otherwise try the default language and finally fall back to the original
   text.

### 3.2 Automatic extraction

The translation workflow may:

1. scan `.ntpl` files for `{:trans; ... :}`;
2. extract source strings;
3. create or update `locale-xx.json` files;
4. preserve existing `ref:` keys.

### 3.3 Naming conventions for reference keys

| Prefix | Usage | Example |
|--------|-------|---------|
| `ref:btn_` | Buttons | `ref:btn_sign_in` |
| `ref:lbl_` | Labels | `ref:lbl_username` |
| `ref:msg_` | Messages | `ref:msg_success` |
| `ref:nav_` | Navigation | `ref:nav_home` |
| `ref:form_` | Forms | `ref:form_title_login` |

---

## 4. Security

### 4.1 Controls

- [x] translations are treated as plain strings, not executable code;
- [x] translations pass through standard HTML escaping;
- [x] `ref:` keys must use valid naming conventions.

### 4.2 Risks

| Risk | Mitigation | Level |
|------|------------|-------|
| XSS through malicious translation text | Standard escaping in rendering | High |
| DoS through huge locale files | Size limits during load | Low |

---

## 5. Implementation

### 5.1 Adding a new language

1. create `locale-xx.json` under the locale component route;
2. add the language code to `site.languages`;
3. translate base system strings;
4. update components that need component-specific translations.

### 5.2 Minimal translatable component structure

```text
src/component/cmp_XXXX_name/
├── manifest.json
├── schema.json
└── route/
    ├── routes.py
    └── locale-en.json
```

---

## 6. Testing

### 6.1 Required test cases

- [ ] the negotiation cascade selects the expected language;
- [ ] fallback to the default language works when a translation is missing;
- [ ] `{:trans; text :}` renders the correct translation;
- [ ] `{:trans; ref:key :}` resolves through locale files;
- [ ] UI-driven language changes persist through cookies.

---

## 7. Acceptance Criteria

- [x] the system supports multiple languages per component;
- [x] the negotiation cascade matches the documented order;
- [x] missing translations fall back gracefully;
- [x] automatic extraction remains possible;
- [x] NTPL text can be translated through `{:trans; :}`.

---

## 8. Impact

### 8.1 Affected components

| Component | i18n usage |
|-----------|------------|
| `cmp_0500_locale` | Base language definitions |
| `cmp_5100_sign` | Multilingual auth forms |
| `cmp_5000_user` | Language profile/settings |
| All components | Locale inheritance in schema |

---

## 9. Decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| JSON instead of gettext | Simpler NTPL integration | No standard PO/MO toolchain |
| Per-component locale files | Isolation and modularity | Possible duplication of shared strings |
| Negotiation cascade | Better user flexibility | More debugging complexity |

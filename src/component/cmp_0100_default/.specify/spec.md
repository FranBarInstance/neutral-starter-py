# Component: default_0yt2sa

## Executive Summary

Base configuration component that provides default values for the system.
Sets initial data for various variables.

Other components can inherit and override these values through the `inherit` mechanism in schema.json.

## Identity
- **UUID**: `default_0yt2sa`
- **Base Route**: ``
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
**Pure configuration** component (no routes, no handlers, no templates).
Provides default data through `schema.json` with inheritance mechanism.

> **Strict limit**: This component must be limited exclusively to setting default values in `schema.json`. It must not include business logic, handlers, routes, or templates.

### Directory Structure

```
src/component/cmp_NNNN_default/
├── manifest.json          # Identity and security
└── schema.json            # Configuration and default data
```

### Dependencies
- **No dependencies**: This is the base component, it does not require other components.
- **Consumers**: Any component that needs to override default configuration.

---

## Acceptance Criteria (SDD)

### Functional
- [x] `schema.json` is valid JSON without syntax errors
- [x] All locale keys follow the expected format for the loader
- [x] Translations cover the 6 base system languages (en, es, de, fr, ar, zh)
- [x] Default values are consistent with project branding

### Technical
- [x] Component exposes no routes (empty base route `''`)
- [x] No Python code (handlers, models, routes)
- [x] Loads first (lowest prefix 0100) to serve as base for other components

### Integration
- [ ] Other components can successfully override `locale` values (verified by component tests)
- [ ] Other components can successfully override `data.route` values (verified by component tests)
- [ ] Schema merging works according to `specs/011-component-configuration/` (verified by integration tests)

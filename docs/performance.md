# Performance Considerations

This document outlines best practices for optimizing component performance in the Neutral TS framework.

## Schema.json Optimization

### Avoid Empty Data Declarations

Do not define empty data objects unless initialization is strictly necessary:

```json
// BAD - Unnecessary empty data
{
    "inherit": {
        "locale": { ... },
        "data": {}
    },
    "data": {}
}

// GOOD - Omit the data key entirely when not needed
{
    "inherit": {
        "locale": { ... }
    }
}
```

### Prefer `data` Over `inherit.data`

Variables declared in `inherit.data` are inherited across the entire component hierarchy and add overhead to the whole application:

```json
// SLOW - Inherited data adds overhead system-wide
{
    "inherit": {
        "data": {
            "key": "value"
        }
    }
}

// FAST - Component-local data, no inheritance overhead
{
    "data": {
        "key": "value"
    }
}
```

**Guideline:** Use `inherit.data` only when you need values to be overwritable from templates using `{:data; ... :}`.

For your own component's data, define them in the appropriate `schema.json`:

| Location | Scope | File |
|----------|-------|------|
| Component root | Global (all routes) | `schema.json` |
| Route folder | Local (specific route) | `route/schema.json` |

Or set them at runtime using `{:data; ... :}` in your templates.

Avoid `inherit.data` unless you specifically need other components to be able to override the values.

## Schema Size Impact

The size of `schema.json` directly affects runtime performance. An excessively large schema can considerably reduce performance due to how Python handles dictionary operations:

- **Memory overhead:** Large dictionaries consume more RAM per request
- **Lookup time:** Dictionary key lookups become slower as size increases
- **Merge operations:** Schema merging during inheritance chains becomes expensive

### Recommendations

1. **Keep schemas minimal:** Only include configuration that is actually used
2. **Split large configurations:** Consider breaking large components into smaller, focused ones
3. **Audit inherited data:** Review and remove unused inherited variables
4. **Use local data:** Prefer `data` over `inherit.data` for component-local configuration. Only use `inherit.data` when other components need to override values

## Measuring Impact

When optimizing, consider:

- Schema parsing time during component initialization
- Memory footprint per request
- Template rendering latency
- Overall request throughput

A well-optimized schema typically contains only the data keys necessary for the component's specific functionality, with minimal inheritance overhead.

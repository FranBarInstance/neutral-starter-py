# 011 - Component Configuration Standard

## Executive Summary

This specification defines the standard for handling configuration variables
inside *Neutral TS Starter Py* components. The goal is to guarantee security
(by preventing secret leakage), establish a clear source of truth for default
values, and provide an explicit mechanism for safe overrides.

---

## 1. Core Rules

### 1.1 Zero Secrets in JSON Files

**Strict rule:** `manifest.json`, `schema.json`, and `data.json` must never
contain passwords, private tokens, API keys, or any other sensitive data.

- **Responsibility:** Each component is responsible for managing its own
  secrets through environment variables (`.env`), `os.getenv()`, or component
  Python code.

### 1.2 Base Configuration in `manifest.json`

**Rule:** Every non-secret configuration variable of a component must be
defined with its default value inside `manifest.json`, under a top-level
`"config"` key.

**Example `manifest.json`:**

```json
{
  "uuid": "rrss_0yt2sa",
  "name": "Read RSS",
  "version": "1.0.0",
  "route": "/rrss",
  "config": {
    "cache_seconds": 300,
    "rrss_default": "BBC",
    "rrss_urls": {
      "BBC": "https://feeds.bbci.co.uk/news/rss.xml"
    }
  }
}
```

**Core behavior:** On startup, the application core automatically reads
`manifest.json` and exposes an **immutable** schema branch with the full
component manifest. Base configuration is therefore always available in:

`data -> {UUID} -> manifest -> config`

### 1.3 Exposing Overridable Variables

**Rule:** Configuration stored in the manifest is immutable by default. If a
component wants certain settings to be overridable by the integrator
(for example, through route-level `data.json` files), it must explicitly copy
those values into the inheritable schema branch.

**Implementation:** This copy must happen in the component `__init__.py`, by
writing the chosen keys into:

`schema.json -> inherit -> data -> {UUID} -> config`

**Example `__init__.py`:**

```python
def init_component(component, component_schema, _schema):
    uuid = component["manifest"]["uuid"]
    manifest_config = component["manifest"]["config"]

    if uuid not in component_schema["inherit"]["data"]:
        component_schema["inherit"]["data"][uuid] = {}

    if "config" not in component_schema["inherit"]["data"][uuid]:
        component_schema["inherit"]["data"][uuid]["config"] = {}

    component_schema["inherit"]["data"][uuid]["config"]["rrss_default"] = (
        manifest_config["rrss_default"]
    )
    component_schema["inherit"]["data"][uuid]["config"]["cache_seconds"] = (
        manifest_config["cache_seconds"]
    )
```

---

## 2. Data Flow and Hierarchy

When this standard is followed, configuration flows as follows:

1. **Definition (defaults):** The component author defines the initial values
   and structure in `manifest.json -> config`.
2. **Core injection:** The core injects the full manifest into
   `data -> {UUID} -> manifest`. This is the immutable source of truth.
3. **Exposure (opt-in):** In `__init__.py`, the component decides which values
   from the original manifest config are copied into
   `inherit -> data -> {UUID} -> config`.
4. **Override:** The application integrator may add a route `data.json`, for
   example:

   ```json
   {
     "inherit": {
       "data": {
         "rrss_0yt2sa": {
           "config": {
             "rrss_default": "TechCrunch"
           }
         }
       }
     }
   }
   ```

5. **Usage in code and templates:** Python code and NTPL templates read the
   final merged value from the `inherit` tree. If a route overrides the value,
   they see the override; otherwise they see the value copied from the
   original manifest.

---

## 3. Benefits of This Architecture

- **Guaranteed security:** Secrets stay outside the JSON configuration
  ecosystem, removing the risk of exposing credentials in schema dumps or
  rendered HTML.
- **Clear responsibilities:** `manifest.json` declares *what exists*, Python
  code decides *what may change*, and `data.json` *applies the change*.
- **Collision prevention:** By grouping overridable settings under the
  component `{UUID}` inside `inherit`, one component cannot accidentally
  overwrite another component's configuration.
- **Immutable reference:** If a component needs the original factory value
  after a route override, it can always read the static branch injected by the
  core at `data -> {UUID} -> manifest -> config`.

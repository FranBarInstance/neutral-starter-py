# Component Overriding Guide

This guide details the methodologies for modifying or replacing entire components in the Neutral TS Starter Py framework. The system is designed to allow you to take control of any aspect of the application in a modular and external way.

---

## 1. Architecture Philosophy: The Component as a Unit

In this framework, a component is managed as an atomic package containing **Data (Schema)**, **Routes (Endpoints)**, and **Interface/Logic (Snippets)**. Overriding a component means taking control of this unit to alter its global behavior.

The architecture allows a "new" component to overlap a "base" one, inheriting and replacing its definitions transparently but decisively.

---

## 2. The Master Rule: Loading Order and Priorities

The component folder name (e.g., `cmp_0100_default`) determines the hierarchy and the order in which the system processes its resources.

### Data and Snippet Priority (Alphabetical Order)
`schema.json` files and snippets are processed in **ascending alphabetical order**.
- **Rule**: The last component to load has the final word.
- **Example**:
  ```
  cmp_0100_default    → Base values (loads first)
  cmp_0110_default    → Overrides values from cmp_0100_default
  ```

### Route Priority (Reverse Order)
Flask Blueprints are registered in **reverse alphabetical order** (from the highest number to the lowest).
- **Rule**: In Flask, the first one to register wins. The first route that matches a URL is the one that executes.
- **Registration Hierarchy**:
  ```
  cmp_0200_feature    → Registered 1st (Highest priority)
  cmp_0100_default    → Registered 2nd
  cmp_9100_catch_all  → Registered last (Fallback)
  ```

### The Special `cmp_9*` Group (Fallbacks)
Components starting with `cmp_9` (e.g., `cmp_9100_catch_all`) are always registered **at the very end of the process**. This makes them the system's "last resort", ideal for 404 error handlers or last-level routing processes.

---

## 3. Guide I: Overriding a Full Component

When you need a new component to functionally replace an existing one, you have two main methods:

### Method A: Replacement by Number/Prefix (Recommended)
This is the cleanest way to "overwrite" a component while keeping the original intact.
1. **New Folder**: Use a higher number (e.g., `cmp_0110_default` to replace `cmp_0100_default`).
2. **New UUID**: Each component **must have its own unique UUID**. Just like with the name prefix, we generate a new UUID so the system identifies the new version as the dominant entity.
3. **Result**: Your component will take control of the routes (due to registration priority) and the data (due to loading order).

### Method B: Replacement by Deactivation
Useful for a total break or to prevent the original component from executing residual logic.
1. **Deactivate**: Rename the original folder with an underscore (e.g., `cmp_0100_default` → `_cmp_0100_default`). The framework ignores any folder that does not strictly start with `cmp_`.
2. **Replace**: Create your new component with its own structure, UUID, and logic from scratch.

---

## 4. Guide II: Overriding Specific Elements

Sometimes you only need to adjust specific pieces without replacing the entire unit.

### Adjustments via `custom.json`
Allows overriding a component's `manifest.json` and `schema.json`. It is the standard method for a user to customize a component without modifying its source code.
- **Usage**: Create a `custom.json` in the component root.
- **Important**: This file **must not be uploaded to the repository** (it should be in `.gitignore`). This ensures that component updates do not overwrite user preferences.
- **Example**:
  ```json
  {
    "manifest": {
      "route": "/my-new-route"
    },
    "schema": {
      "data": {
        "current": {
          "site": {
            "title": "Custom Title"
          }
        }
      }
    }
  }
  ```

### Adjustments via `config.db`
Allows making changes without touching files, using the `custom` table of the `config.db` database.
- **Priority**: Values defined in **`config.db` override those in `custom.json`** and the original manifest/schema.
- **Usage**: The JSON stored in the `custom` table follows the same structure as a `custom.json` and is applied by looking up the component's UUID.

### Overriding Variables and Schema Data
Any key defined in a component that loads later will replace the previous one in the global schema.
```json
// In cmp_0110_custom/schema.json
{
  "data": {
    "current": {
      "site": {
        "title": "New Site Title"
      }
    }
  }
}
```

### Redefining Individual Snippets
If a base component defines an interface using `{:snip; name >> ... :}`, you can override it by defining another snippet with the **same name** in any `.ntpl` file of a component that loads later.
- **Rule**: The last processed definition is the one the system will store and use.

### Dynamic Overrides per Request (Evaluated on each request)
For changes that only affect a specific rendering within a template:
- `{:locale; file.json :}`: Overrides translations (`schema->inherit->locale`).
- `{:data; file.json :}`: Overrides inherited data (`schema->inherit->data`).

---

## 5. Technical Aspects of the Overriding Process

### Data Merge
The combination process is cumulative and deep:
- **Override**: New values replace old ones if the keys match.
- **Cleanup Strategy**: To "empty" a nested object or array, you must set that key to `null` in your override schema.

### Global Snippets and Initialization (`component-init.ntpl`)
`component-init.ntpl` files are processed at **application startup**.
- **Function**: They are responsible for defining global snippets that will be available to the entire application.
- **Override**: Just like any other snippet, the content defined within these files can be overridden by subsequently loaded components following the "last one wins" rule.

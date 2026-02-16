---
name: translate-component
description: Extract and translate web template strings from Neutral TS (.ntpl) files into component-specific locale JSON files.
---

# Translate Component Skill

This skill allows the agent to automatically find, extract, and translate strings within Neutral TS template files (`*.ntpl`) and update the corresponding localization files (`locale-xx.json`).

Use `view_file` on `docs/translation-component.md` for more advanced options.

## Context
In Neutral TS projects, web templates use the format `{:trans; Text to translate :}` or `{:trans; ref:reference_key :}`. These translations are stored in JSON files located in the component's `route` directory, named `locale-xx.json` (where `xx` is the language code).

## Workflow

1.  **Identify Component Path**:
    Determine the base directory of the component (e.g., `src/component/cmp_5100_sign_local/neutral`).

2.  **Scan for Template Files**:
    Find all `*.ntpl` files recursively within that directory.

3.  **Extract Strings**:
    Identify all strings marked for translation using the pattern `{:trans; (.*?) :}`.
    -   **References**: Strings starting with `ref:` (e.g., `ref:error_required`). These need translation in ALL languages, including English.
    -   **Default Text**: Plain text strings (e.g., `Login`). These are typically in English and only need translation in non-English locale files.

4.  **Manage Locale Files**:
    Locate or create the following files in the `route/` subdirectory:
    -   `locale-en.json`
    -   `locale-es.json`
    -   `locale-fr.json`
    -   `locale-de.json`

5.  **Update JSON Content**:
    Each file must strictly follow this structure:
    ```json
    {
        "trans": {
            "xx": {
                "Text or ref:key": "Translation"
            }
        }
    }
    ```
    *Note: Replace `xx` with the language code (es, fr, de, etc.).*

6.  **Preservation**:
    When updating existing files, do not remove current translations. Add new strings and update existing ones if necessary.

## Helper Commands

**Find all unique translation tags:**
```bash
grep -roPh "{:trans; .*? :}" [component_path] | sort | uniq
```

**Clean extraction of keys:**
```bash
grep -roPh "{:trans; .*? :}" [component_path] | sed 's/{:trans; \(.*\) :}/\1/' | sort | uniq
```

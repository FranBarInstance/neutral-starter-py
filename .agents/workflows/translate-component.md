---
description: Translate a component's .ntpl files into multiple languages
---

# Multi-language Component Translation Workflow

Use this workflow to automatically localize a Neutral TS component.

1. Identify the component directory (e.g., `src/component/cmp_XYZ/neutral`).
2. Run the `Translate component` skill:
   - Scan all `*.ntpl` files for `{:trans; ... :}` tags.
   - Extract unique keys.
   - For `locale-en.json`, add only `ref:` keys.
   - For `locale-es.json`, `locale-fr.json`, and `locale-de.json`, translate all extracted keys.
3. Verify that the JSON structure is correct and follows the schema:
   ```json
   {
       "trans": {
           "language_code": {
               "key": "value"
           }
       }
   }
   ```
4. Update the files and report the summary of added strings.

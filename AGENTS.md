## Mandatory Python Virtual Environment
- Before running any Python-related command (`python`, `pip`, `pytest`, `pylint`, `mypy`, `ruff`, etc.), always activate the local virtual environment.
- Use the single-shell form:
  `source .venv/bin/activate && <command>`
- Do not use global/system Python tools when `.venv` is available.
- For linting, prefer:
  `source .venv/bin/activate && python -m pylint <paths>`
- Check the `.agent/skills/` directory for available skills.

## Do Not Use Absolute Paths
- Never use absolute system paths anywhere in this repository.

## Content Security Policy
- The application is CSP-enabled and must be treated as running under a Content Security Policy.
- Avoid introducing inline JavaScript, inline event handlers, or inline styles unless the user explicitly requests a CSP-compatible exception strategy.
- Prefer external scripts, external styles, and DOM event binding from static assets.
- When an inline `<script>` or `<style>` is necessary, include the Neutral nonce placeholder `{:;CSP_NONCE:}` in the tag.
- Use these patterns:
  `<script nonce="{:;CSP_NONCE:}">`
  `<style nonce="{:;CSP_NONCE:}">`
- Apply the same nonce attribute to CSP-sensitive tags that require it in existing project patterns.

## Temporary Files
- For temporary files or temporary scripts in this repository, use `tmp/agent`.
- The `tmp/` directory always exists in this repository.
- If `tmp/agent` does not exist yet, it may be created before writing temporary files there.

## Component Naming
- The component folder name is dynamic and must not be treated as a stable identifier.
- The stable identifier is the component UUID from `manifest.json`.
- In documentation, avoid referring to components by folder name such as `cmp_5400_album_image`.
- In documentation, avoid absolute component paths that include the folder name when the goal is to describe files inside the component.
- Prefer UUID-based references when naming the component in prose.
- When documenting files inside a component, prefer component-relative paths such as `/schema.json`, `/route/routes.py`, `/neutral/snippets.ntpl`, or `/static/album-image-field.js`.
- Tests, docs, and examples must not assume the component folder name is known in advance.
- If load order matters, document the relative ordering requirement between components without relying on a specific folder name unless the repository state makes that ordering explicit and necessary.

## Component Routes
- The component base route is dynamic and must not be treated as a stable identifier.
- The effective route is the value of `route` in `manifest.json`.
- In documentation, avoid hardcoding concrete routes such as `/album-image/` unless the exact current repository state is the explicit subject of the documentation.
- Prefer abstract route notation such as `<manifest.route>/`, `<manifest.route>/field/list`, or similar when documenting component endpoints.
- If needed, add a short note that `<manifest.route>` is defined in `manifest.json`.
- Tests and examples should derive component routes from `manifest.json` whenever possible instead of assuming a fixed path string.


## Available Local Skills
- Review `.agent/skills/*/SKILL.md` before acting when the task matches one of these skills.
- Prefer the smallest applicable skill set. If multiple skills match, use them in this order: component structure, templates, AJAX forms, translations.
- Example components may exist as `cmp_*` or `_cmp_*`. Always use the variant that exists in the repository state.
- Respect component isolation: when a skill targets a component, avoid changing files outside that component unless the user explicitly asks for it.

### `manage-component`
- Summary: component creation and structural component changes in Neutral TS.
- Use when creating a new component or modifying an existing component's architecture, routes, manifest, schema, models, static files, backend logic, or tests.
- Read: `.agent/skills/manage-component/SKILL.md`

### `manage-neutral-templates`
- Summary: NTPL templates, route data, snippets, and template-driven page structure.
- Use when creating or editing `.ntpl` files, route `data.json`, shared snippets, or template-driven page structure in Neutral TS.
- Read: `.agent/skills/manage-neutral-templates/SKILL.md`

### `manage-ajax-forms`
- Summary: AJAX forms, modal flows, validation, and `{:fetch; ... :}` interactions.
- Use when building or modifying Neutral TS forms, AJAX form flows, modal forms, validation schemas, or `{:fetch; ... :}` interactions.
- Read: `.agent/skills/manage-ajax-forms/SKILL.md`
- Except in exceptional cases, use Ajax for all forms.

### `translate-component`
- Summary: extraction and maintenance of translations for a single component.
- Use when extracting, creating, or updating translations for a component from `.ntpl`, `data.json`, `schema.json`, or route locale files.
- Read: `.agent/skills/translate-component/SKILL.md`

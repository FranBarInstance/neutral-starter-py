## Mandatory Python Virtual Environment
- Before running any Python-related command (`python`, `pip`, `pytest`, `pylint`, `mypy`, `ruff`, etc.), always activate the local virtual environment.
- Use the single-shell form:
  `source .venv/bin/activate && <command>`
- Do not use global/system Python tools when `.venv` is available.
- For linting, prefer:
  `source .venv/bin/activate && python -m pylint <paths>`
- Check the `.agent/skills/` directory for available skills.

## Available Local Skills
- Review `.agent/skills/*/SKILL.md` before acting when the task matches one of these skills.
- Prefer the smallest applicable skill set. If multiple skills match, use them in this order: component structure, templates, AJAX forms, translations.
- Example components may exist as `cmp_*` or `_cmp_*`. Always use the variant that exists in the repository state.
- Respect component isolation: when a skill targets a component, avoid changing files outside that component unless the user explicitly asks for it.

### `manage-component`
- Use when creating a new component or modifying an existing component's architecture, routes, manifest, schema, models, static files, backend logic, or tests.
- Follow the Neutral TS component structure under `src/component/cmp_*`.
- Keep each component self-contained, including its own model and tests.
- Do not translate the component unless the user explicitly requests translation work.
- Prefer UUID-based references in documentation and route-related references, not folder-name-based references.
- Tests must not depend on the component folder name; derive paths dynamically from the current component directory.

### `manage-neutral-templates`
- Use when creating or editing `.ntpl` files, route `data.json`, shared snippets, or template-driven page structure in Neutral TS.
- Follow official NTPL syntax and existing project template patterns.
- Check data sources carefully: `schema.data`, `schema.inherit.data`, and `CONTEXT`.
- Wrap user-facing texts with `{:trans; ... :}` when appropriate.
- End rendered `content-snippets.ntpl` files with `{:^;:}`.
- Apply the template security rules from the skill, especially around user input and dynamic evaluation.

### `manage-ajax-forms`
- Use when building or modifying Neutral TS forms, AJAX form flows, modal forms, validation schemas, or `{:fetch; ... :}` interactions.
- Keep page templates and AJAX response templates separated.
- AJAX response templates under `ajax/content-snippets.ntpl` must not load `data.json` directly.
- If a form uses manual `fetch()` instead of Neutral automated classes, explicitly send the `Requested-With-Ajax: true` header.
- Use Bootstrap 5 modal structure when the task involves modals, and load modal body content through Neutral fetch on the visible event.
- Wrap all user-facing strings in `{:trans; ... :}` and end page `content-snippets.ntpl` files with `{:^;:}`.

### `translate-component`
- Use when extracting, creating, or updating translations for a component from `.ntpl`, `data.json`, `schema.json`, or route locale files.
- Limit translation changes to the target component directory.
- If the user does not specify languages, inspect `src/component/cmp_0500_locale/schema.json` for the available languages.
- Put global component texts such as menus and `component-init.ntpl` strings in `schema.json` under `inherit.locale.trans`.
- Put route-specific texts in `neutral/route/locale-xx.json` or `locale.json`, preserving existing translations.
- Translate strings found in `{:trans; ... :}` and user-visible texts inside route `data.current.route.*`.

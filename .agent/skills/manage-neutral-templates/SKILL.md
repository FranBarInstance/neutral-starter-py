---
name: manage-neutral-templates
description: Create or modify Neutral TS web template files (.ntpl) following the official syntax and security standards.
---

# Manage Neutral TS Templates Skill

This skill provides the guidelines and syntax reference for creating and modifying Neutral TS templates (`.ntpl` files).

## Documentation References
- **Full Internal Documentation**: [docs/templates-neutrats.md](docs/templates-neutrats.md)
- **Official Documentation**: [Neutral TS Doc](https://franbarinstance.github.io/neutralts-docs/docs/neutralts/doc/)

## Neutral TS Syntax Overview

Neutral TS uses **BIFs (Built-in Functions)** wrapped in `{::}`.

### Basic Structure
`{: [modifiers] name ; [flags] params >> code :}`

- **Modifiers**:
    - `^` : Eliminate preceding whitespace.
    - `!` : Negate condition or change behavior.
    - `+` : Promote to parent/current scope.
    - `&` : HTML escape output.

### Variables
- **Immutable Data**: `{:;varname:}`
- **Local Mutable Data**: `{:;local::varname:}`
- **Object/Array Access**: `{:;array->key:}`
- **Dynamic Access**: `{:;array->{:;key:}:}`

## Common Control Flow

### Conditionals
- `{:filled; varname >> content :}`: If variable has content.
- `{:defined; varname >> content :}`: If variable is defined (not null/undef).
- `{:bool; varname >> content :}`: If variable evaluates to true.
- `{:same; /a/b/ >> content :}`: If `a` equals `b`.
- `{:contains; /haystack/needle/ >> content :}`: Substring check.

### Iteration
- `{:each; array key value >> content :}`: Iterate over array/object.
- `{:for; var 1..10 >> content :}`: Numeric loop.

### Alternatives
- `{:else; content :}`: Used after a conditional or output BIF that produced no content.

## Features

### Modularization
- `{:include; file.ntpl :}`: Include another template.
- `{:snippet; name >> content :}`: Define a reusable block.
- `{:snippet; name :}`: Output a defined snippet.

### Localization
- `{:trans; Text :}`: Translate text using locale files.
- `{:locale; locale.json :}`: Load a specific translation file.

### Local data
- `{:data; local-data.json :}`: Load a specific translation file.
- `{:;local::varname:}`: Access local data.

### Advanced
- `{:cache; /300/ >> content :}`: Cache block for 300 seconds.
- `{:coalesce; {:;v1:} {:;v2:} :}`: Take first non-empty.
- `{:eval; code >> use {:;__eval__:} :}`: Evaluate code and use result.

## Security Standards (CRITICAL)

1.  **Context Isolation**: Always use user-provided data from the `CONTEXT` object (GET, POST, COOKIES, ENV).
2.  **Auto-Escaping**: Variables in `CONTEXT` are auto-escaped. Use `{:&;var:}` for manual escaping of other data.
3.  **Safe Includes**: Never use raw variables in `include`. Use `allow` lists:
    ```
    {:declare; valid >> home.ntpl login.ntpl :}
    {:include; {:allow; valid >> {:;file:} :} :}
    ```
4.  **No Injection**: Neutral TS does not evaluate variables by default. Use `{:allow; ... :}` only when explicit evaluation of partial strings is required.

## Workflow for Modification

1.  **Analysis**: Identify the data structure (the "schema") being passed to the template.
2.  **Structure**: Use HTML5 semantic tags.
3.  **Logic**: Implement control flow using BIFs.
4.  **Translation**: Wrap all UI text in `{:trans; ... :}`.
5.  **Validation**: Ensure all BIF tags are properly closed with `:}`.

## Route Content Strategy

Neutral TS uses a snippet-based strategy to render route-specific content within a common layout.

### 1. The Layout Entry Point (`index.ntpl`)
Located in `src/component/cmp_0200_template/neutral/layout/index.ntpl`, it acts as the orchestrator:
- It includes global utility and template snippets.
- It dynamically includes the route's snippet file:
  `{:include; {:;CURRENT_NEUTRAL_ROUTE:}/{:;CURRENT_COMP_ROUTE:}/content-snippets.ntpl :}`.
- It finally renders either the AJAX template or the full `template.ntpl`.

### 2. The Base Template (`template.ntpl`)
Located in `src/component/cmp_0200_template/neutral/layout/template.ntpl`, it defines the HTML structure:
- It renders the main content by calling the snippet: `{:snip; current:template:body-main-content :}`.
- It also uses common snippets like `{:snip; current:template:page-h1 :}`.

### 3. Global Layout Snippets (`template-snippets.ntpl`)
Located in `src/component/cmp_0200_template/neutral/layout/template-snippets.ntpl`, it defines reusable UI blocks used across the application:
- **Page Heading (`current:template:page-h1`)**: Automatically renders an `<h1>` if `local::current->route->h1` is defined.
- **Modals (`current:template:modals`)**: Common modal structures.
- **Footers & Spinners**: Standardized footer and loading indicators.

These snippets often rely on keys within the `local::current` data object.

**CRITICAL**: Do NOT modify `template-snippets.ntpl` directly. If you need to change a snippet's behavior for a route, overwrite it in the route's `content-snippets.ntpl`.

### 4. Route Specific Snippets (`content-snippets.ntpl`)
Each route must have a `content-snippets.ntpl` (e.g., in `src/component/cmp_xxxx/neutral/route/root/test1/`).
This file is responsible for:
- **Data Loading**: Route-specific data is typically loaded from a `data.json` file in the same directory. This data populates the `local` scope (accessible via `{:;local::...:}`).
  ```ntpl
  {:data; {:flg; require :} >> #/data.json :}
  ```
  Example `data.json`:
  ```json
  {
      "data": {
          "current": {
              "route": {
                  "title": "Page Title",
                  "description": "Page description for SEO",
                  "h1": "Visible Page Heading"
              }
          }
      }
  }
  ```
- **Locale**: Optionally loading route-specific translations.
  ```ntpl
  {:locale; {:flg; require :} >> #/locale.json :}
  ```
- **Layout Overrides**: Optionally disabling or modifying layout snippets (carousel, lateral bar, etc.).
  ```ntpl
  {:snip; current:template:body-lateral-bar >> :} {* Disable lateral bar *}
  ```
- **Main Content**: Defining the required `current:template:body-main-content` snippet.
  ```ntpl
  {:snip; current:template:body-main-content >>
    <p>{:trans; Welcome to my content. :}</p>
  :}
  ```
- **Forcing Output**: Always end the file with `{:^;:}` or `{:;:}` to ensure the `{:include; ... :}` BIF detects "success" content and doesn't trigger an `{:else; :}` block (like a 404).

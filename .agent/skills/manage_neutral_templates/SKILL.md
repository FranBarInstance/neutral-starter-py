---
name: Manage Neutral TS Templates
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
- `{:coalesce; {:;v1:} {:;v2:} >> default :}`: Take first non-empty.
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

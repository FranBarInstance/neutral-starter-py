---
name: manage-neutral-templates
description: Create or modify Neutral TS web template files (.ntpl) following the official syntax and security standards.
---

# Create or Modify Neutral TS Templates

Create, modify, and manage Neutral TS (NTPL) template files following the official Neutral TS syntax, security standards, and architectural patterns.

Use `view_file` on `src/component/cmp_7000_hellocomp` or `_src/component/cmp_7000_hellocomp` as a component example.
Use `view_file` on `docs/templates-neutrats.md` for more template options.
Use `view_file` on `docs/templates-neutrats-ajax.md` for AJAX requests.
Use `view_file` on `docs/development-style-guide.md` for more style guide.

---

### **Workflow for Creating/Modifying Templates**

#### **Step 1: Analyze Requirements**
- What data will the template receive? (schema.data vs schema.inherit.data)
- What user input needs handling? (CONTEXT)
- What translations are needed?
- Are there reusable snippets?

#### **Step 2: File Structure**
```
neutral/route/root/[route-name]/
├── content-snippets.ntpl    {:* Main template *:}
├── data.json                {:* Route metadata *:}
└── locale.json              {:* Translations (optional) *:}
```

#### **Step 3: Data Schema**
Define in `data.json`:
```json
{
    "data": {
        "current": {
            "route": {
                "title": "...",
                "description": "...",
                "h1": "..."
            }
        },
        "component_specific": {
            "items": [],
            "config": {}
        }
    }
}
```

#### **Step 4: Template Implementation**
1. Load data: `{:data; {:flg; require :} >> #/data.json :}`
2. Define `current:template:body-main-content`
3. Use `{:trans; ... :}` for all UI text
4. End with `{:^;:}`

#### **Step 5: Security Review**
- [ ] No direct variable evaluation without `allow`
- [ ] All user input from CONTEXT
- [ ] File includes use allowlists
- [ ] No `{:!;CONTEXT->...:}` without justification

---

## Core Syntax

### BIF (Built-in Function) Structure

```
{:[modifiers]name; [flags] params >> code :}
{:[modifiers]name; code :}
```

### Modifiers

| Modifier | Symbol | Description |
|----------|--------|-------------|
| Upline | `^` | Eliminates previous whitespace |
| Not | `!` | Negates condition or changes behavior |
| Scope | `+` | Adds scope to current level |
| Filter | `&` | Escapes HTML special characters |

Modifiers can be combined: `{:^!defined; varname >> ... :}`

## Variables

### Variable `schema.data` (Immutable)
```
{:;varname:}           # Simple variable
{:;array->key:}        # Array/object access
{:;array->{:;key:}:}   # Dynamic evaluation
```

### Local Variable `schema.inherit.data` (Mutable)
```
{:;local::varname:}           # Simple variable
{:;local::array->key:}        # Array/object access
{:;local::array->{:;key:}:}   # Dynamic evaluation
```

## Schema Structure
```json
{
  "config": {
    "comments": "remove",
    "cache_prefix": "neutral-cache",
    "cache_dir": "",
    "cache_on_post": false,
    "cache_on_get": true,
    "cache_on_cookies": true,
    "cache_disable": false,
    "filter_all": false,
    "disable_js": false,
    "debug_expire": 3600,
    "debug_file": ""
  },
  "inherit": {
    "locale": {
      "current": "en",
      "trans": {
        "en": {
          "Hello": "Hello"
        },
        "es": {
          "Hello": "Hola"
        }
      }
    },
    "data": {
      "my_var": "value"
    }
  },
  "data": {
    "CONTEXT": {
      "ROUTE": "",
      "HOST": "",
      "GET": {},
      "POST": {},
      "HEADERS": {},
      "FILES": {},
      "COOKIES": {},
      "SESSION": {},
      "ENV": {}
    },
    "my_var": "value",
    "my_obj": {
      "key": "value"
    }
  }
}
```

## Unprintable — `{:;:}`
Outputs empty string. Use `{:^;:}` to eliminate whitespace, or `{:;:}` to preserve spaces.

## Control Flow BIFs

### Conditionals
```
{:filled; varname >> content :}                  # If variable has content
{:!filled; varname >> content :}                 # If variable is empty
{:defined; varname >> content :}                 # If variable is defined
{:!defined; varname >> content :}                # If variable is undefined
{:bool; varname >> content :}                    # If variable is true
{:!bool; varname >> content :}                   # If variable is false
{:same; /a/b/ >> content :}                      # If a equals b
{:!same; /a/b/ >> content :}                     # If a not equals b
{:contains; /haystack/needle/ >> content :}      # If contains substring
{:!contains; /haystack/needle/ >> content :}     # If not contains
```

### Iteration
```
{:each; array key value >>
    {:;key:} = {:;value:}
:}

{:for; var 1..10 >>
    {:;var:}
:}
```

### Else Block
Evaluate whether the expression produces an empty block, not the Boolean expression
```
{:;varname:}{:else; shown if empty :}
{:filled; varname >> content :}{:else; alternative :}
```

## Content BIFs

### Variable Output
```
{:;varname:}           # Output variable
{:^;varname:}          # Output without preceding whitespace
{:&;varname:}          # Output with HTML escaping
{:!;varname:}          # Output without filtering
```

### Code Block
```
{:code; content :}                          # Basic code block
{:code; {:flg; safe :} >> content :}        # Safe mode (no parsing)
{:code; {:flg; noparse :} >> content :}     # No parsing
{:code; {:flg; encode_tags :} >> content :} # Encode HTML tags
```

### Include
```
{:include; file.ntpl :}                              # Include template
{:include; {:flg; require :} >> file.ntpl :}         # Required include
{:include; {:flg; noparse :} >> file.css :}          # Include without parsing
{:include; {:flg; safe :} >> file.txt :}             # Safe include
{:include; #/relative/path.ntpl :}                   # Relative to current file
{:include; anything-{:;varname:} :}                  # Dynamic include
{:include; {:;varname:} :}                           # Dynamic GET ERROR use allow
```

### Snippets

Snippets are reusable code fragments in templates, similar to functions, that avoid repetition by allowing you to define a block (such as a form) once and use it across multiple templates.

```
{:snip; my-form >>
    <form action="{:;action:}" method="{:;method:}">
      ...
    </form>
:}
```

And then use it like this:

```
{:snip; my-form :}
```

You can use `{:snippet; ... :}` or `{:snip; ... :}` interchangeably.

```
{:snippet; name >> content :}   # Define snippet
{:snippet; name :}              # Use snippet
{:snip; name >> content :}      # Alias for snippet
```

## Safety Features

### Context Variables
User-provided data should be placed in `CONTEXT`:
```json
{
    "data": {
        "CONTEXT": {
            "GET": {},
            "POST": {},
            "COOKIES": {},
            "ENV": {}
        }
    }
}
```

All `CONTEXT` variables are automatically HTML-escaped.

### Security

Use `nonce` in `<script>` and `<style>` tags.

```html
<script nonce="{:;CSP_NONCE:}">
    // Script content
</script>
<style nonce="{:;CSP_NONCE:}">
    /* Style content */
</style>
```

- Variables are **not evaluated** (template injection safe)
- Complete variable evaluation requires `{:allow; ... :}`
- Partial evaluation allowed: `{:; array->{:;key:} :}`
- Templates cannot access data not in schema.
- `CONTEXT` vars auto-escaped. `filter_all: true` escapes everything.

### File Security
```
# Error - insecure:
{:include; {:;varname:} :}

# Secure - with allow:
{:declare; valid-files >>
    home.ntpl
    login.ntpl
:}
{:include;
    {:allow; valid-files >> {:;varname:} :}
    {:else; error.ntpl :}
:}
```

### Allow/Deny Lists
```
{:declare; allowed >>
    word1
    word2
    *.ntpl
:}
{:allow; allowed >> {:;varname:} :}
```

Wildcards supported:
- `.` - matches any character
- `?` - matches exactly one character
- `*` - matches zero or more characters

## Advanced Features

### Caching
```
{:cache; /300/ >> content :}           # Cache for 300 seconds
{:cache; /300/custom-id/ >> content :} # Cache with custom ID
{:!cache; content :}                   # Exclude from cache
```

### Translations

For `{:trans; ... :}` with plain text (not `ref:`), the phrase itself is the source text.

- If a phrase is already written in language `xx`, do not add a redundant translation entry for `xx`.
- Add translations only for the other target languages.
- This rule is language-agnostic: the source language can be English, Spanish, French, etc., as long as that source is used consistently for the phrase.

```
{:trans; Hello :}                       # Translate text or text
{:!trans; Hello :}                      # Translate or empty
{:locale; translations.json :}          # Load translations
```

Translation in schema.json:
```json
{
    "inherit": {
        "locale": {
            "current": "en",
            "trans": {
                "en": { "Hello": "Hello" },
                "es": { "Hello": "Hola" }
            }
        }
    }
}
```

Translation in locale.json loaded by {:locale; locale.json :}:
```json
{
    "trans": {
        "en": { "Hello": "Hello" },
        "es": { "Hello": "Hola" }
    }
}
```

### Parameters
```
{:code;
    {:param; name >> value :}   # Set parameter
    {:param; name :}            # Get parameter
    ...
:}
```

### Coalesce
```
{:coalesce;
    {:;var1:}
    {:;var2:}
    {:code; default :}
:}
```

### Evaluation
```
{:eval; {:;varname:} >>
    Content if not empty: {:;__eval__:}
:}
```

## Scope & Inheritance
- Definitions are block-scoped, inherited by children, recovered on exit.
- `include` has block scope.
- `+` modifier promotes definitions to current/parent scope.

### Scope Modifier (`+`)
By default, definitions have block scope. `+` extends to current level:
```
{:code;
    {:include; snippet.ntpl :}
    {:snippet; name :}     # Not available outside
:}
{:snippet; name :}         # Not available

{:+code;
    {:include; snippet.ntpl :}
    {:snippet; name :}     # Available outside
:}
{:snippet; name :}         # Still available
```

## HTTP Features

### Exit/Redirect
```
{:exit; 404 :}                    # Exit with status
{:!exit; 302 :}                   # Set status, continue
{:exit; 301 >> /url :}            # Redirect
{:redirect; 301 >> /url :}        # HTTP redirect
{:redirect; js:reload:top :}      # JS redirect
```

### Fetch (AJAX)
```
{:fetch; |/url|auto| >> <div>loading...</div> :}
{:fetch; |/url|click| >> <button>Load</button> :}
{:fetch; |/url|form| >> ... :}
```

Events: `auto`, `none`, `click`, `visible`, `form`

## Comments
```
{:* single line comment *:}

{:*
    multi-line
    comment
*:}

{:; varname {:* inline comment *:} :}
```

## Quick Reference Table

| BIF | Purpose |
|-----|---------|
| `{:;var:}` | Output variable |
| `{:code; ... :}` | Code block |
| `{:filled; v >> c :}` | Conditional (has content) |
| `{:defined; v >> c :}` | Conditional (is defined) |
| `{:bool; v >> c :}` | Conditional (is true) |
| `{:each; arr k v >> c :}` | Loop through array |
| `{:for; v 1..10 >> c :}` | For loop |
| `{:include; file :}` | Include file |
| `{:snippet; n >> c :}` | Define snippet |
| `{:snippet; n :}` | Play snippet |
| `{:trans; text :}` | Translate |
| `{:cache; /t/ >> c :}` | Cache content |
| `{:coalesce; ... :}` | First non-empty |
| `{:join; /arr/sep/ :}` | Join array |
| `{:same; /a/b/ >> c :}` | String comparison |
| `{:contains; /h/n/ >> c :}` | Substring check |
| `{:allow; list >> val :}` | Whitelist check |
| `{:declare; name >> list :}` | Define whitelist |
| `{:exit; code :}` | HTTP status/exit |
| `{:redirect; code >> url :}` | Redirect |
| `{:fetch; |url|ev| >> c :}` | AJAX request |
| `{:else; c :}` | Else condition |
| `{:eval; c1 >> c2 :}` | Evaluate and output |
| `{:param; n >> v :}` | Set parameter |
| `{:moveto; tag >> c :}` | Move content to tag |
| `{:date; format :}` | Output date |
| `{:hash; text :}` | MD5 hash |
| `{:rand; 1..10 :}` | Random number |
| `{:sum; /a/b/ :}` | Sum values |
| `{:replace; /f/t/ >> c :}` | String replace |
| `{:count; ... :}` | Count (deprecated) |
| `{:data; file.json :}` | Load local data |
| `{:locale; file.json :}` | Load translations |
| `{:debug; key :}` | Debug output |
| `{:neutral; c :}` | No-parse output |
| `{:obj; config :}` | Execute external script |
| `{:; :}` | Unprintable (empty) |

## Security Best Practices

1. **Never trust context data** (GET, POST, COOKIES, ENV)
2. **Use `CONTEXT`** for all user-provided data
3. **Use `{:allow; ... :}`** for dynamic file inclusion
4. **Use `filter_all: true`** for maximum safety
5. **Validate variables** with `declare`/`allow` before evaluation
6. **Remove debug** BIFs before production
7. **Both application and templates** should implement security

## Truth Table
| Variable | Value | filled | defined | bool | array |
|----------|-------|--------|---------|------|-------|
| true | true | ✅ | ✅ | ✅ | ❌ |
| false | false | ✅ | ✅ | ❌ | ❌ |
| "hello" | string | ✅ | ✅ | ✅ | ❌ |
| "0" | string | ✅ | ✅ | ❌ | ❌ |
| "1" | string | ✅ | ✅ | ✅ | ❌ |
| "  " | spaces | ✅ | ✅ | ✅ | ❌ |
| "" | empty | ❌ | ✅ | ❌ | ❌ |
| null | null | ❌ | ❌ | ❌ | ❌ |
| undef | — | ❌ | ❌ | ❌ | ❌ |
| [] | empty arr | ❌ | ✅ | ❌ | ✅ |
| {...} | object | ✅ | ✅ | ✅ | ✅ |

## Page Content Strategy

The application uses a snippet-based architectural pattern to render dynamic route-specific content within a consistent global layout.

### Layout Orchestration (`index.ntpl`)

The entry point for rendering any page is typically `src/component/cmp_0200_template/neutral/layout/index.ntpl`. Its main functions are:

1.  **Global Includes**: It loads utility snippets, theme structures, and navigation components.
2.  **Route Inclusion**: It dynamically includes the `content-snippets.ntpl` file corresponding to the current route:
    ```ntpl
    {:include; {:;CURRENT_NEUTRAL_ROUTE:}/{:;CURRENT_COMP_ROUTE:}/content-snippets.ntpl :}
    ```
3.  **Template Execution**: Depending on the request type (AJAX vs. standard), it loads the final rendering structure (`template.ntpl` or `template-ajax.ntpl`).

### The Base Template (`template.ntpl`)

The `template.ntpl` file defines the semantic HTML5 skeleton. Instead of direct content, it uses **placeholders** (snippets) that are filled by the route-specific files:

- `{:snip; current:template:page-h1 :}`: Renders the page title.
- `{:snip; current:template:body-main-content :}`: Renders the primary page body.
- `{:snip; current:template:body-lateral-bar :}`: Renders an optional sidebar.

> [!IMPORTANT]
> All default implementations for these snippets are located in `src/component/cmp_0200_template/neutral/layout/template-snippets.ntpl`. **Modifying this file directly is not recommended.** Instead, you should overwrite the desired snippet in your route's `content-snippets.ntpl` file to customize behavior for that specific route.

### Route-Specific Dynamic (`content-snippets.ntpl`)

Each route (e.g., `src/component/cmp_xxxx_name/neutral/route/root/test1/`) provides its own `content-snippets.ntpl`. This file is responsible for:

1.  **Data Persistence**: Loading the local `data.json` to populate the `local::current` namespace.
    ```ntpl
    {:data; {:flg; require :} >> #/data.json :}
    ```
    *Example `data.json` for the global H1:*
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
2.  **Component Overrides**: Modifying or disabling global snippets (e.g., hiding the sidebar).
    ```ntpl
    {:snip; current:template:body-lateral-bar >> :}
    ```
3.  **Core Content**: Defining the final content for the main placeholder.
    ```ntpl
    {:snip; current:template:body-main-content >>
        <p>Dynamic Content Here</p>
    :}
    ```
4.  **Inclusion Force**: Always end with `{:^;:}` to ensure the include BIF detects success content.

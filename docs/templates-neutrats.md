# Neutral TS - Web Template Engine

## Overview

Neutral TS is a safe, modular, language-agnostic template engine built in Rust. It can be used as a native Rust library or via IPC for other languages (Python, PHP, Node.js, Go). Templates can be reused across multiple languages with consistent results.

This is a summary for the context of AI; the full documentation is here:: [Neutral TS Doc](https://franbarinstance.github.io/neutralts-docs/docs/neutralts/)

### Template File Example
```
{:*
    comment
*:}
{:locale; locale.json :}
{:data; local-data.json :}
{:include; theme-snippets.ntpl :}
<!DOCTYPE html>
<html lang="{:lang;:}">
    <head>
        <title>{:trans; Site title :}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        {:snippet; current-theme:head :}
        <link rel="stylesheet" href="bootstrap.min.css">
    </head>
    <body class="{:;body-class:}">
        {:snippet; current-theme:body_begin  :}
        {:snippet; current-theme:body-content :}
        {:snippet; current-theme:body-footer  :}
        <script src="jquery.min.js"></script>
    </body>
</html>
```

## Core Syntax

### BIF (Built-in Function) Structure

```
{:[modifiers]name; [flags] params >> code :}
```

Structure breakdown:
```
{:[modifiers]name; [flags] params >> code :}
 │    │         │      │       │     │  │
 │    │         │      │       │     │  └─ Close BIF
 │    │         │      │       │     └─ Code block
 │    │         │      │       └─ Params/Code separator
 │    │         │      └─ Parameters
 │    │         └─ Name separator
 │    └─ BIF name
 └─ Open BIF
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

### Variable Access
```
{:;varname:}           # Simple variable
{:;array->key:}        # Array/object access
{:;array->{:;key:}:}   # Dynamic evaluation
```

### Local Variable Access
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
{:filled; varname >> content :}      # If variable has content
{:!filled; varname >> content :}     # If variable is empty
{:defined; varname >> content :}     # If variable is defined
{:!defined; varname >> content :}    # If variable is undefined
{:bool; varname >> content :}        # If variable is true
{:!bool; varname >> content :}       # If variable is false
{:same; /a/b/ >> content :}          # If a equals b
{:!same; /a/b/ >> content :}         # If a not equals b
{:contains; /haystack/needle/ >> content :}  # If contains substring
{:!contains; /haystack/needle/ >> content :} # If not contains
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

### Variable Security
- Variables are **not evaluated** (template injection safe)
- Complete variable evaluation requires `{:allow; ... :}`
- Partial evaluation allowed: `{:; array->{:;key:} :}`

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
{:!cache; content :}                    # Exclude from cache
```

### Translations
```
{:trans; Hello :}                       # Translate text
{:!trans; Hello :}                      # Translate or empty
{:locale; translations.json :}          # Load translations
```

Translation schema:
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

### Parameters
```
{:code;
    {:param; name >> value :}   # Set parameter
    {:param; name :}             # Get parameter
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

### Scope Modifier (`+`)
By default, definitions have block scope. `+` extends to current level:
```
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

## Configuration Options

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
    }
}
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

## Scope & Inheritance
- Definitions are block-scoped, inherited by children, recovered on exit.
- `include` has block scope.
- `+` modifier promotes definitions to current/parent scope.

## Security
- Templates cannot access data not in schema.
- Variable values NEVER evaluated as BIFs (injection-safe).
- Full dynamic var/file names → error (use `allow`).
- `CONTEXT` vars auto-escaped. `filter_all: true` escapes everything.
- Rules: Never trust CONTEXT. Filter at BOTH app and template layers.

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

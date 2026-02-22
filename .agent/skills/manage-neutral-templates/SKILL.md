---
name: manage-neutral-templates
description: Create or modify Neutral TS web template files (.ntpl) following the official syntax and security standards.
---

# Create or Modify Neutral TS Templates

Create, modify, and manage Neutral TS (NTPL) template files following the official Neutral TS syntax, security standards, and architectural patterns.

Use `view_file` on `docs/templates-neutrats-ajax.md` for AJAX requests.
Use `view_file` on `docs/templates-neutrats.md` for more template options.
Use `view_file` on `docs/development-style-guide.md` for more style guide.

## Documentation References
- **Official Documentation**: [Neutral TS Doc](https://franbarinstance.github.io/neutralts-docs/docs/neutralts/)

---

### **1. NTPL File Fundamentals**

**File Extension:** `.ntpl` (Neutral Template)

**Core Philosophy:**
- **Safe by design**: Variables are NOT evaluated by default (prevents injection attacks)
- **Language-agnostic**: Same templates work across Python, Rust, PHP, Node.js, Go
- **Modular**: Component-based architecture with snippet reusability
- **Security-first**: Built-in XSS protection and context-aware escaping

---

### **2. BIF (Built-in Function) Structure**

All NTPL functionality uses BIFs with this exact syntax:

```
{:[modifiers]name; [flags] params >> code :}
```

**Anatomy:**
```
{:[modifiers]name; [flags] params >> code :}
 │            │  │     │       │      │   │
 │            │  │     │       │      │   └─ Close BIF (always :})
 │            │  │     │       │      └─ Code block (content to render)
 │            │  │     │       └─ Params/Code separator (>>)
 │            │  │     └─ Parameters (variables, files, conditions)
 │            │  └─ Name separator (;)
 │            └─ BIF name (snippet, trans, include, etc.)
 └─ Open BIF ({:)
```

**Modifiers (prefix before name):**
| Modifier | Symbol | Purpose |
|----------|--------|---------|
| Upline | `^` | Eliminates preceding whitespace |
| Not | `!` | Negates condition or changes behavior |
| Scope | `+` | Promotes definition to parent/current scope |
| Filter | `&` | Escapes HTML special characters |

**Example with modifiers:**
```ntpl
{:^!filled; varname >> content :}  {:* No whitespace, negated, filtered *:}
```

---

### **3. Comments**

**Syntax:**
```ntpl
{:* Single line comment *:}

{:*
    Multi-line comment
    ------------------
    Can span multiple lines
*:}

{:* Inline comment in BIF :}
{:;varname {:* get user name *:} :}

{:*
    Nested comments are supported
    {:* Inner comment *:}
    {:*
        Multiple levels
        {:* Deep nesting *:}
    *:}
*:}
```

---

### **4. Variable System**

#### **4.1 Immutable Data (`schema.data`)**
Accessed via `{:;varname:}` - set by Python/backend, cannot be overridden by templates.

```ntpl
{:;site_name:}                    {:* Simple variable *:}
{:;user->email:}                   {:* Object property *:}
{:;array->{:;index:}:}              {:* Dynamic array access *:}
```

#### **4.2 Local/Mutable Data (`schema.inherit.data`)**
Accessed via `{:;local::varname:}` - can be overridden by templates at runtime.

```ntpl
{:;local::current->route->title:}
{:;local::menu->session:->user->name:}
```

#### **4.3 CONTEXT (User Input)**
All user-provided data (GET, POST, COOKIES, ENV) is auto-escaped and stored in CONTEXT:

```ntpl
{:;CONTEXT->POST->username:}        {:* Auto-escaped POST data *:}
{:;CONTEXT->GET->id:}                {:* Auto-escaped GET parameter *:}
{:;CONTEXT->SESSION->userId:}         {:* Session data *:}
{:;CONTEXT->HEADERS->User-Agent:}    {:* Request headers *:}
```

**Security Rule:** Never use `{:!;CONTEXT->...:}` (unfiltered) unless absolutely necessary.

---

### **5. Core BIF Reference**

#### **5.1 Output & Variables**

| BIF | Syntax | Purpose |
|-----|--------|---------|
| Variable | `{:;varname:}` | Output immutable data |
| Local Variable | `{:;local::varname:}` | Output mutable local data |
| Unprintable | `{:;:}` or `{:^;:}` | Output empty string (whitespace control) |
| Filtered Output | `{:&;varname:}` | HTML-escaped output |

**Unprintable BIF details:**
```ntpl
{:* Basic unprintable - preserves spaces :}
{:;:}

{:* Upline unprintable - eliminates preceding whitespace :}
{:^;:}

{:* Usage examples :}
|<pre>
{:code;
    {:^;:}    {:* Eliminates leading newline *:}
    Hello
    {:^;:}    {:* Eliminates trailing newline *:}
:}
</pre>|
```

#### **5.2 Conditionals**

```ntpl
{:* Check if variable has content (non-empty, non-null, defined) *:}
{:filled; varname >>
    <p>Has content: {:;varname:}</p>
:}

{:* Negated - check if empty or undefined *:}
{:!filled; varname >>
    <p>Variable is empty or undefined</p>
:}

{:* Check if variable is defined (exists, even if null/empty) *:}
{:defined; varname >>
    <p>Variable exists</p>
:}

{:* Check if NOT defined *:}
{:!defined; varname >>
    <p>Variable does not exist</p>
:}

{:* Boolean check - true values: true, non-zero, non-empty strings *:}
{:bool; varname >>
    <p>Truthy value</p>
:}

{:* Boolean negated *:}
{:!bool; varname >>
    <p>Falsy value</p>
:}

{:* String comparison - any delimiter works :}
{:same; /{:;status:}/active/ >>
    <p>Status is active</p>
:}

{:* Negated comparison *:}
{:!same; /{:;status:}/active/ >>
    <p>Status is not active</p>
:}

{:* Substring check *:}
{:contains; /{:;text:}/search/ >>
    <p>Contains "search"</p>
:}

{:* Negated contains *:}
{:!contains; /{:;text:}/search/ >>
    <p>Does not contain "search"</p>
:}

{:* Array check *:}
{:array; varname >>
    <p>Is an array/object</p>
:}

{:* Negated array check *:}
{:!array; varname >>
    <p>Is not an array</p>
:}

{:* Use else *:}
{:filled; varname >>
    <p>Has content: {:;varname:}</p>
:}{:else;
    <p>Variable is empty or undefined</p>
:}

```

**Else blocks** (evaluate whether the PREVIOUS BIF produced output):
```ntpl
{:* Else evaluates if previous BIF output was empty *:}
{:filled; varname >> <p>Has content</p> :}
{:else; <p>Is empty</p> :}

{:* Chain multiple else blocks *:}
{:code;
    {:;foo:}
    {:;bar:}
:}{:else;
    foo and bar are empty
:}{:else;
    {:* This fires if previous else was empty (i.e., foo or bar had content) *:}
    foo or bar has content
:}
```

**Truth Table (from documentation):**
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

#### **5.3 Iteration**

```ntpl
{:* Loop through array/object - each *:}
{:each; users key user >>
    <div class="user">
        <span>{:;key:}</span>
        <span>{:;user->name:}</span>
        <span>{:;user->email:}</span>
    </div>
:}

{:* With upline modifier for clean output :}
{:^each; items idx item >>
    <li>{:;idx:}: {:;item:}</li>
:}

{:* Numeric loop - for *:}
{:for; i 1..10 >>
    <span>{:;i:}</span>
:}

{:* Reverse loop *:}
{:for; i 10..1 >>
    <span>{:;i:}</span>
:}

{:* Nested iteration example *:}
{:^each; array key val >>
    {:array; val >>
        {:;:}
        {:;key:}:
        {:^each; val key val >>
            {:array; val >>
                {:;:}
                {:;key:}:
                {:^each; val key val >>
                    {:;:}
                    {:;key:}={:;val:}
                :}
            :}{:else;
                {:;:}
                {:;key:}={:;val:}
            :}
        :}
    :}{:else;
        {:;:}
        {:;key:}={:;val:}
    :}
:}
```

#### **5.4 Snippets**

Snippets are reusable code fragments in templates, similar to functions, that avoid repetition by allowing you to define a block (such as a form) once and use it across multiple templates. You can use `{:snippet;` or `{:snip;` interchangeably.

```ntpl
{:* Define a snippet (must be in file with "snippet" in name) *:}
{:snip; user-card >>
    <div class="card">
        <h3>{:;local::user->name:}</h3>
        <p>{:;local::user->bio:}</p>
    </div>
:}

{:* Use the snippet *:}
{:snip; user-card :}

{:* Alternative syntax *:}
{:snip; user-card :}

{:* Snippet with static flag (parsed at definition time) *:}
{:snip; {:flg; static :} user-card-static >>
    {:;varname:}  {:* Evaluated when DEFINED, not when called *:}
:}

{:* Scope modifiers with snippets - + promotes to parent scope *:}
{:+code;
    {:include; snippet.ntpl :}
    {:snip; name :}  {:* Available outside due to + *:}
:}
{:snip; name :}  {:* Works because of + above *:}
```

#### **5.5 Includes**

```ntpl
{:* Basic include *:}
{:include; header.ntpl :}

{:* Required include (errors if missing) *:}
{:include; {:flg; require :} >> config.ntpl :}

{:* Include without parsing (raw content) *:}
{:include; {:flg; noparse :} >> styles.css :}

{:* Safe include (encoded, no parsing) *:}
{:include; {:flg; safe :} >> readme.txt :}

{:* Relative to current file - # symbol *:}
{:include; #/snippets.ntpl :}      {:* Same directory *:}
{:include; #/../shared/nav.ntpl :} {:* Parent directory *:}

{:* Dynamic include with allowlist (SECURITY CRITICAL) *:}
{:declare; valid-pages >>
    home.ntpl
    about.ntpl
    contact.ntpl
:}
{:include;
    {:allow; valid-pages >> {:;page:} :}
    {:else; error.ntpl :}
:}

{:* Prevent reparse with ! modifier *:}
{:!include; already-parsed.ntpl :}
```

#### **5.6 Translations**

```ntpl
{:* Basic translation *:}
{:trans; Hello World :}

{:* Translation with fallback to empty *:}
{:!trans; Hello World :}{:else; Default text :}

{:* Reference-based translation *:}
{:trans; ref:menu:home :}

{:* Load locale file *:}
{:locale; locale-en.json :}
{:locale; {:flg; require :} >> #/locale-{:lang;:}.json :}

{:* Prevent reload if already loaded *:}
{:!locale; locale-es.json :}

{:* Upline modifier for clean whitespace *:}
{:^trans; Hello :}
```

**Locale file structure (`locale-es.json`):**
```json
{
    "__comment_:trans": "This translation will be available for the entire Component",
    "trans": {
        "es": {
            "Hello World": "Hola Mundo",
            "ref:menu:home": "Inicio",
            "Welcome to {:;site-name:}": "Bienvenido a {:;site-name:}"
        }
    }
}
```

#### **5.7 Data Loading**

```ntpl
{:* Load local data from JSON *:}
{:data; local-data.json :}

{:* Inline data *:}
{:data; {:flg; inline :} >>
    {
        "data": {
            "items": ["one", "two", "three"]
        }
    }
:}

{:* Prevent reload *:}
{:!data; already-loaded.json :}

{:* Access loaded data via local:: *:}
{:;local::items->0:}
```

#### **5.8 Caching**

```ntpl
{:* Cache block for 300 seconds *:}
{:cache; /300/ >>
    <div>{:;expensive-content:}</div>
:}

{:* Cache with custom ID added to auto-generated ID *:}
{:cache; /300/my-custom-id/ >>
    <div>Content</div>
:}

{:* Replace auto-generated ID completely (third param = 1/true) *:}
{:cache; /300/my-id/1/ >>
    <div>Content</div>
:}

{:* Exclude from cache (always fresh) *:}
{:!cache;
    <div>{:date; %H:%M:%S :}</div>  {:* Current time, not cached *:}
:}

{:* Nested caching *:}
{:cache; /60/ >>
    Outer cached content (60s)
    {:cache; /300/ >>
        Inner cached longer (300s)
    :}
    {:!cache;
        Always fresh (not cached)
    :}
:}

{:* Upline modifier *:}
{:^cache; /60/ >> content :}
```

#### **5.9 Parameters**

```ntpl
{:* Set parameters within code block *:}
{:code;
    {:param; title >> Dashboard :}
    {:param; user_count >> 42 :}

    <h1>{:param; title :}</h1>
    <span>{:param; user_count :} users</span>
:}

{:* Parameters have block scope and recover their value *:}
{:code;
    {:param; name >> 1 :}
    {:code;
        {:param; name >> 2 :}
    :}
    {:* "name" recovers value 1 here *:}
    {:param; name :}  {:* Outputs 1 *:}
:}
```

#### **5.10 AJAX/Fetch**

```ntpl
{:* Auto-fetch on page load (default) *:}
{:fetch; |/api/data|auto| >>
    <div class="loading">Loading...</div>
:}

{:* Or simply (auto is default) *:}
{:fetch; "/api/data" >> <div>Loading...</div> :}

{:* Click-triggered fetch *:}
{:fetch; |/api/action|click| >>
    <button>Load Data</button>
:}

{:* Visible-triggered fetch (intersection observer) *:}
{:fetch; |/api/lazy|visible| >>
    <div class="placeholder">Scroll to load</div>
:}

{:* Form submission via fetch *:}
{:fetch; |/api/submit|form|form-wrapper|my-form-class|my-form-id| >>
    <input type="text" name="username">
    <button type="submit">Submit</button>
:}

{:* With wrapper ID for target container *:}
{:fetch; |/api/content|auto|content-wrapper| >>
    <div>Loading content...</div>
:}

{:* No event - manual trigger *:}
{:fetch; |/api/manual|none| >> <div>Manual load</div> :}

{:* Upline modifier *:}
{:^fetch; |/url|auto| >> content :}
```

**HTTP Header:** All fetch requests set `requested-with-ajax: fetch`

#### **5.11 Code Blocks**

```ntpl
{:* Basic code block (no action, just grouping) *:}
{:code;
    <div>Any content</div>
    {:;variable:}
:}

{:* Safe mode - encode everything *:}
{:code; {:flg; safe :} >>
    <div>{:;untrusted:}</div>  {:* Will be encoded *:}
:}

{:* No parse - output raw BIF syntax *:}
{:code; {:flg; noparse :} >>
    <div>{:;not-parsed:}</div>  {:* Shows literal {:;not-parsed:} *:}
:}

{:* Encode HTML tags *:}
{:code; {:flg; encode_tags :} >>
    <div>HTML tags encoded</div>
:}

{:* Encode BIFs *:}
{:code; {:flg; encode_bifs :} >>
    <div>{:;bif:}</div>  {:* Shows &#123;:;bif:&#125; *:}
:}

{:* Encode tags after parsing *:}
{:code; {:flg; encode_tags_after :} >>
    {:include; file.ntpl :}  {:* Parsed, then encoded *:}
:}

{:* Upline modifier *:}
{:^code; content :}

{:* Scope modifier *:}
{:+code; content :}
```

#### **5.12 Control Flow**

```ntpl
{:* Coalesce - first non-empty value *:}
{:coalesce;
    {:;option1:}
    {:;option2:}
    {:code; Default value :}
:}

{:* Evaluate and capture result *:}
{:eval; {:;complex-expression:} >>
    Result: {:;__eval__:}
:}

{:* Negated eval *:}
{:!eval; {:;empty-var:} >>
    Shown if empty
:}

{:* Exit with status code *:}
{:exit; 404 :}                    {:* Stop, 404 error, content cleared *:}
{:!exit; 302 :}                   {:* Set 302, continue execution *:}
{:exit; 301 >> /new-url :}        {:* Redirect to URL *:}

{:* Custom status codes (1000+ range for app-specific) *:}
{:exit; 10404 >> not-found :}     {:* Custom 404-like code *:}

{:* Redirect BIF *:}
{:redirect; 301 >> /destination :}
{:redirect; js:reload:top :}      {:* JS reload top window *:}
{:redirect; js:reload:self :}     {:* JS reload current frame *:}
{:redirect; js:redirect;top >> /url :}   {:* JS redirect top *:}
{:redirect; js:redirect;self >> /url :}  {:* JS redirect self *:}

{:* Upline modifiers *:}
{:^coalesce; ... :}
{:^eval; ... :}
{:^exit; ... :}
{:^redirect; ... :}
```

#### **5.13 Security BIFs**

```ntpl
{:* Declare allowlist - MUST be in snippet file *:}
{:declare; allowed-templates >>
    home.ntpl
    about.ntpl
    *.ntpl
:}

{:* Declare with wildcards *:}
{:declare; languages >>
    en
    en-??
    en_??
    es
    es-??
    es_??
:}

{:* Check against allowlist *:}
{:allow; allowed-templates >> {:;template:} :}

{:* Negated - check if NOT in list *:}
{:!allow; blocked-items >> {:;item:} :}

{:* With flags *:}
{:allow; {:flg; partial :} patterns >> {:;value:} :}    {:* Wildcard matching *:}
{:allow; {:flg; casein :} patterns >> {:;value:} :}      {:* Case-insensitive *:}
{:allow; {:flg; replace :} patterns >> {:;value:} :}   {:* Return matched pattern *:}
{:allow; {:flg; partial casein replace :} p >> v :}     {:* Combined *:}

{:* Upline modifier *:}
{:^declare; ... :}
{:^allow; ... :}
```

**Wildcard rules:**
- `.` - matches any single character
- `?` - matches exactly one character
- `*` - matches zero or more characters

#### **5.14 Utility BIFs**

```ntpl
{:* Date formatting *:}
{:date; :}                        {:* Unix timestamp *:}
{:date; %Y-%m-%d %H:%M:%S :}      {:* Formatted date UTC *:}

{:* MD5 hash *:}
{:hash; :}                        {:* Random hash *:}
{:hash; text to hash :}           {:* Specific hash *:}

{:* Random number *:}
{:rand; :}                        {:* Random integer *:}
{:rand; 1..100 :}                 {:* Range *:}

{:* String join *:}
{:join; |array|, | :}              {:* Join with comma *:}
{:join; /array/ - /keys/ :}        {:* Join keys with " - " *:}

{:* String replace *:}
{:replace; /old/new/ >> text :}
{:replace; ~ ~/~ >> path :}      {:* Replace / with ~ *:}

{:* Sum *:}
{:sum; /5/10/ :}                  {:* Outputs 15 *:}

{:* Move content to HTML tag *:}
{:moveto; </head >> <style>css</style> :}
{:moveto; <body >> <script>js</script> :}   {:* Beginning of body *:}
{:moveto; </body >> <script>js</script> :}  {:* End of body *:}

{:* Count (DEPRECATED per docs) *:}
{:count; ... :}  {:* Do not use *:}

{:* Upline modifiers *:}
{:^date; ... :}
{:^hash; ... :}
{:^rand; ... :}
{:^join; ... :}
{:^replace; ... :}
{:^sum; ... :}
{:^moveto; ... :}
```

#### **5.15 External Objects/Python**

```ntpl
{:* Execute Python script from JSON config *:}
{:obj; #/obj/config.json :}

{:* Inline configuration *:}
{:obj;
    {
        "engine": "Python",
        "file": "{:;component->path:}/src/script.py",
        "schema": false,
        "venv": "{:;VENV_DIR:}",
        "params": {
            "user_id": "{:;CONTEXT->SESSION->userId:}"
        },
        "callback": "main",
        "template": ""
    }
:}

{:* With inline template *:}
{:obj;
    {
        "engine": "Python",
        "file": "script.py",
        "params": {"name": "World"}
    }
    >>
    <div>{:;local::message:}</div>
:}

{:* Upline modifier *:}
{:^obj; ... :}

{:* Scope modifier *:}
{:+obj; ... :}
```

**Object JSON structure:**
```json
{
    "engine": "Python",
    "file": "path/to/script.py",
    "schema": false,
    "venv": "/path/to/venv",
    "params": {
        "key": "value"
    },
    "callback": "main",
    "template": "optional-template.ntpl"
}
```

**Python script:**
```python
def main(params=None):
    # Access schema if "schema": true
    schema = globals().get('__NEUTRAL_SCHEMA__')
    return {
        "data": {
            "message": f"Hello, {params.get('name', 'World')}!"
        }
    }
```

#### **5.16 Flags BIF**

```ntpl
{:* Set flags for other BIFs *:}
{:flg; flag1 flag2 flag3 :}

{:* Used within other BIFs *:}
{:include; {:flg; require noparse :} >> file.txt :}
{:data; {:flg; inline :} >> {...} :}
{:snip; {:flg; static :} name >> content :}
```

**Available flags:**
- `require` - Error if file missing
- `noparse` - Don't parse included file
- `safe` - Encode all (implies noparse, encode_tags, encode_bifs)
- `encode_tags` - Encode HTML tags
- `encode_bifs` - Encode BIF delimiters
- `encode_tags_after` - Encode after parsing
- `inline` - Inline data for data BIF
- `static` - Parse snippet at definition time
- `partial` - Allow wildcard matching in allow
- `casein` - Case-insensitive matching
- `replace` - Return matched pattern in allow

---

### **6. File Structure & Architecture**

#### **6.1 Component Template Structure**

```
src/component/cmp_XXXX_name/
├── neutral/
│   ├── component-init.ntpl          {:* Global snippets (loaded at startup) *:}
│   └── route/
│       ├── index-snippets.ntpl      {:* Shared across all routes *:}
│       ├── locale-en.json           {:* Component translations *:}
│       ├── locale-es.json
│       ├── locale-fr.json
│       ├── locale-de.json
│       ├── data.json                {:* Shared route data *:}
│       └── root/                    {:* Route templates *:}
│           ├── content-snippets.ntpl    {:* Root route / *:}
│           ├── data.json                {:* Route data *:}
│           └── subroute/                {:* /subroute *:}
│               ├── content-snippets.ntpl
│               └── data.json
```

#### **6.2 Route Content Strategy**

**Critical Pattern:** Every route MUST define `current:template:body-main-content`

```ntpl
{:* content-snippets.ntpl standard structure *:}

{:* 1. Load route data (REQUIRED) *:}
{:data; {:flg; require :} >> #/data.json :}

{:* 2. Optional: Load route-specific translations *:}
{:locale; {:flg; require :} >> #/locale.json :}

{:* 3. Include shared snippets *:}
{:!include; {:flg; require :} >> #/snippets.ntpl :}

{:* 4. Override global snippets if needed *:}
{:snip; current:template:body-carousel >> :}  {:* Disable carousel *:}
{:snip; current:template:body-lateral-bar >> :}  {:* Disable sidebar *:}

{:* 5. Override page heading *:}
{:snip; current:template:page-h1 >>
    <div class="container my-3">
        <h1 class="border-bottom p-2">{:trans; {:;local::current->route->h1:} :}</h1>
    </div>
:}

{:* 6. Define main content (REQUIRED) *:}
{:snip; current:template:body-main-content >>
    <div class="{:;local::current->theme->class->container:}">
        <h3>{:trans; Page Title :}</h3>
        <p>Content here...</p>
    </div>
:}

{:* 7. Force output (REQUIRED - prevents 404 fallback) *:}
{:^;:}
```

**Standard `data.json`:**
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

**Standard `index-snippets.ntpl` for component:**
```ntpl
{:* Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE) *:}

{:* Data for all routes *:}
{:data; {:flg; require :} >> #/data.json :}

{:* Locale for current language only *:}
{:locale;
    #/locale-{:lang;:}.json
:}{:else;
    {:locale; #/locale-en.json :}
:}

{:* Shared snippets for all routes *:}
{:snip; component-info >>
    <div>Component: {:;CURRENT_COMP_NAME:}</div>
    <div>Route: {:;CURRENT_COMP_ROUTE:}</div>
:}
```

---

### **7. Security Standards**

#### **7.1 Variable Evaluation Rules**

| Scenario | Safe | Unsafe |
|----------|------|--------|
| Direct output | `{:;varname:}` | - |
| Array access | `{:;array->key:}` | - |
| Dynamic key | `{:;array->{:;key:}:}` | - |
| **Full variable eval** | - | `{:;{:;varname:}:}` ⚠️ |
| With allowlist | `{:;{:allow; list >> {:;varname:} :}:}` | - |

**Never do this:**
```ntpl
{:* DANGEROUS - allows arbitrary code injection *:}
{:;{:;user_input:}:}
{:include; {:;user_file:} :}
```

**Always use allowlists for dynamic content:**
```ntpl
{:* SAFE - validated against allowlist *:}
{:declare; valid-pages >> home about contact :}
{:include;
    {:allow; valid-pages >> {:;page:} :}
    {:else; error.ntpl :}
:}
```

#### **7.2 CONTEXT Security**

All user input is in CONTEXT and is **auto-escaped**:
```ntpl
{:* Safe - auto-escaped *:}
{:;CONTEXT->POST->message:}

{:* Dangerous - unfiltered raw output *:}
{:!;CONTEXT->POST->message:}  {:* Only if you KNOW it's safe *:}
```

#### **7.3 File Inclusion Security**

```ntpl
{:* NEVER - direct variable in include *:}
{:include; {:;filename:} :}  {:* ERROR: insecure file name *:}

{:* NEVER - partial eval without allow *:}
{:include; page-{:;name:}.ntpl :}  {:* DANGEROUS *:}

{:* ALWAYS - use allowlist *:}
{:declare; allowed >> home about :}
{:include; {:allow; allowed >> {:;name:} :}.ntpl :}
```

#### **7.4 Schema Configuration**

```json
{
    "config": {
        "filter_all": false,      {:* true = escape ALL variables *:}
        "cache_disable": false,   {:* true = disable all caching *:}
        "disable_js": false,      {:* true = manual JS injection *:}
        "debug_expire": 3600,     {:* Debug file expiration *:}
        "debug_file": ""          {:* Debug enable file path *:}
    }
}
```

---

### **8. Common Patterns & Recipes**

#### **8.1 Form with Validation Errors**

```ntpl
{:* Define error display snippet *:}
{:snip; form-field-error >>
    {:filled; {:param; error :} >>
        <div class="invalid-feedback">{:trans; {:param; error :} :}</div>
    :}
:}

{:* Define form field with error handling *:}
{:snip; form-field:username >>
    <div class="input-group">
        <span class="input-group-text">@</span>
        <input
            type="text"
            name="username"
            value="{:;CONTEXT->POST->username:}"
            class="form-control {:filled; {:param; error :} >> is-invalid :}"
        >
    </div>
    {:param; error >> {:;form_errors->username:} :}
    {:snip; form-field-error :}
:}
```

#### **8.2 Conditional Layout**

```ntpl
{:bool; HAS_SESSION >>
    {:snip; user-dashboard :}
:}{:else;
    {:snip; guest-welcome :}
:}
```

#### **8.3 Dynamic Class Names**

```ntpl
<div class="btn {:same; /{:;status:}/active/ >> btn-primary :}{:else; btn-secondary :}">
    {:trans; {:;status:} :}
</div>
```

#### **8.4 Translation with Variables**

```ntpl
{:* In locale file: "Welcome back, {:;username:}" *:}
{:trans; Welcome back, {:;username:} :}
```

#### **8.5 Safe HTML Injection (Trusted Content)**

```ntpl
{:* When you trust the source but need HTML *:}
{:code; {:flg; noparse :} >> {:;trusted_html:} :}
```

#### **8.6 Wrapping Pattern (from docs)**

```ntpl
{:* Prevent empty wrapper when snippet is empty *:}
{:eval; {:snip; snippet-name :} >>
    <li>{:;__eval__:}</li>
:}
```

#### **8.7 Parameter Passing Pattern**

```ntpl
{:* Set parameters and include *:}
{:code;
    {:param; title >> My Title :}
    {:param; active >> true :}
    {:include; card.ntpl :}
:}

{:* In card.ntpl *:}
<div class="card {:bool; {:param; active :} >> active :}">
    <h3>{:param; title :}</h3>
</div>
```

---

### **9. Workflow for Creating/Modifying Templates**

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

### **10. Troubleshooting**

| Issue | Cause | Solution |
|-------|-------|----------|
| Template renders empty | Missing `{:^;:}` | Add at end |
| 404 on valid route | Include failed | Check `{:flg; require :}` paths |
| Variables not showing | Wrong scope | Use `{:;local::...:}` for inherit data |
| Security error "insecure varname" | Direct var eval | Use `{:allow; ... :}` |
| Security error "insecure file name" | Direct file eval | Use `{:allow; ... :}` |
| Translations not loading | Locale not included | Add `{:locale; ... :}` |
| Cache not updating | Aggressive caching | Use `{:!cache; ... :}` or clear cache |
| Snippet not found | Wrong file name | Snippets must be in files with "snippet" in name |
| Parameter not available | Wrong scope | Use `{:+code; ... :}` to promote scope |

---

### **11. Integration with Python/Dispatcher**

Templates receive data from `Dispatcher` classes:

```python
# In dispatcher.py
dispatch.schema_data["user"] = {"name": "John"}      # Immutable: {:;user->name:}
dispatch.schema_local_data["items"] = ["a", "b"]     # Mutable: {:;local::items:}
```

**Dispatcher sets automatically:**
- `CURRENT_COMP_ROUTE` - Current route path
- `CURRENT_COMP_ROUTE_SANITIZED` - Route with : instead of /
- `CURRENT_NEUTRAL_ROUTE` - Path to neutral/route directory
- `CURRENT_COMP_NAME` - Component directory name
- `CURRENT_COMP_UUID` - Component UUID
- `CONTEXT` - Request context (SESSION, POST, GET, HEADERS, etc.)
- `HAS_SESSION` - "true" or null
- `HAS_SESSION_STR` - "true" or "false"
- `CSP_NONCE` - Content Security Policy nonce
- `LTOKEN` - Link token for forms
- `COMPONENTS_MAP_BY_NAME` - Component name → UUID mapping
- `COMPONENTS_MAP_BY_UUID` - Component UUID → name mapping

---

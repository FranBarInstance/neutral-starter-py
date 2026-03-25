# Hello Component

Neutral Starter Py reference component that demonstrates a full implementation with snippets, translations, AJAX, and Bootstrap 5 modals.

## Disabling the Component

To disable this component without deleting it, rename the component folder with an underscore prefix (e.g., `_cmp_7000_hellocomp`). The framework will skip loading components that start with `_`, but AI assistants will still find it as a reference in the skills documentation.

## Identity

- UUID: `hellocomp_0yt2sa`
- Base route: `/hello-component`

## What This Component Shows

- Global snippet available across the app: `neutral/component-init.ntpl`
- Snippet for all component routes: `neutral/route/index-snippets.ntpl`
- Snippet specific to the current route: `neutral/route/root/content-snippets.ntpl`
- Visual UI example with cards, buttons, image, and Bootstrap 5 utilities
- Simple modal
- AJAX-loaded modal (click-triggered and auto-load)
- Modal with form (GET) submitted to `/test2`
- Business-logic example with a custom dispatcher on `/test1`
- Python object rendered in template (`neutral/obj/comp.json` + `src/comp.py`)
- Extra translation example for object-provided text (`neutral/obj/locale-obj-comp.json`)
- Translating content route with language-specific templates

## Routes

- `GET /hello-component/`
  - Component home with snippets, AJAX, and modal demos.
- `GET /hello-component/test1`
  - Uses `DispatcherHelloComp` and shows `dispatch_result`.
- `GET /hello-component/test2`
  - Displays form-submitted data (`name`, `topic`).
- `GET /hello-component/translating-content`
  - Demonstrates language-specific content templates (`content-{lang}.ntpl`).
- `GET /hello-component/redirect`
  - Demonstrates redirect functionality.
- `GET /hello-component/error-500`
  - Demonstrates error 500 page.
- `GET /hello-component/ajax/example`
  - Returns a partial AJAX block.
  - Requires header `Requested-With-Ajax`.
- `GET /hello-component/ajax/modal-content`
  - Returns AJAX modal content.
  - Requires header `Requested-With-Ajax`.
- `GET /hello-component/<static_file>`
  - Serves files from `static/` (for example `comp.webp`).

## Translations

- Global menu translations in `schema.json` (`inherit.locale.trans`).
- Component translations in `neutral/route/locale-{lang}.json`:
  - Supported languages: `ar`, `cs`, `de`, `el`, `en`, `es`, `fr`, `hi`, `hu`, `it`, `ja`, `nl`, `pl`, `pt`, `ro`, `ru`, `sv`, `uk`, `zh`
- Route-specific translations:
  - `neutral/route/root/test1/locale.json`
  - `neutral/route/root/test2/locale.json`
- Language-specific content templates in `neutral/route/root/translating-content/`:
  - `content-{lang}.ntpl` for each supported language.

Includes translations for template text and for strings defined in `data.json` (`title`, `description`, `h1`).

## Structure

```
cmp_7000_hellocomp/
├── __init__.py                   # Component registration (lib)
├── manifest.json                 # Component metadata
├── schema.json                   # Configuration schema, menus and global translations
├── custom.json                   # Custom configuration
├── README.md                     # This file
├── lib/
│   └── hellocomp_0yt2sa/         # Python library
│       ├── __init__.py
│       └── hellocomp.py          # Helper functions
├── neutral/
│   ├── component-init.ntpl       # Global snippet (loaded on every page)
│   ├── obj/
│   │   ├── comp.json             # Object data for template rendering
│   │   └── locale-obj-comp.json  # Object-specific translations
│   └── route/
│       ├── data.json             # Route data
│       ├── index-snippets.ntpl   # Snippets for all routes
│       ├── locale-{lang}.json    # Route translations
│       └── root/
│           ├── content-snippets.ntpl          # Contents for /hello-component
│           ├── data.json
│           ├── ajax/
│           │   ├── example/
│           │   │   └── content-snippets.ntpl  # Contents for /hello-component/ajax/exmple
│           │   └── modal-content/
│           │       └── content-snippets.ntpl  # Contents for /hello-component/modal-content/exmple
│           ├── error-500/
│           │   └── content-snippets.ntpl      # Contents for /hello-component/error-500
│           ├── redirect/
│           │   └── content-snippets.ntpl      # Contents for /hello-component/redirect
│           ├── test1/
│           │   ├── content-snippets.ntpl      # Contents for /hello-component/test1
│           │   ├── data.json
│           │   └── locale.json
│           ├── test2/
│           │   ├── content-snippets.ntpl      # Contents for /hello-component/test2
│           │   ├── data.json
│           │   └── locale.json
│           └── translating-content/
│               ├── content-snippets.ntpl      # Contents for /hello-component/translating-content
│               ├── data.json
│               └── content-{lang}.ntpl
├── route/
│   ├── __init__.py              # Component blueprint registration
│   ├── dispatcher_hellocomp.py  # Custom dispatcher for test1
│   └── routes.py                # Route definitions
├── src/
│   └── comp.py                  # Python object for comp.json
├── static/
│   └── comp.webp                # Static image
└── tests/
    ├── conftest.py
    └── test_hellocomp.py
```

## Tests

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7000_hellocomp/tests
```

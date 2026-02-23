# Hello Component

Neutral Starter Py reference component that demonstrates a full implementation with snippets, translations, AJAX, and Bootstrap 5 modals.

## Identity

- UUID: `hellocomp_0yt2sa`
- Base route: `/hello-component`
- Path: `src/component/cmp_7000_hellocomp`
- Version: `0.0.0`

## What This Component Shows

- Global snippet available across the app: `neutral/component-init.ntpl`
- Snippet for all component routes: `neutral/route/index-snippets.ntpl`
- Snippet specific to the current route: `neutral/route/root/content-snippets.ntpl`
- Visual UI example with cards, buttons, image, and Bootstrap 5 utilities (no extra CSS)
- Simple modal
- AJAX-loaded modal
- Modal with form (GET) submitted to `/test2`
- Business-logic example with a custom dispatcher on `/test1`
- Python object rendered in template (`neutral/obj/comp.json` + `src/comp.py`)
- Extra translation example for object-provided text (`neutral/obj/locale-obj-comp.json`)

## Routes

- `GET /hello-component/`
  - Component home with snippets, AJAX, and modal demos.
- `GET /hello-component/test1`
  - Uses `DispatcherHelloComp` and shows `dispatch_result`.
- `GET /hello-component/test2`
  - Displays form-submitted data (`name`, `topic`).
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
- Component translations in:
  - `neutral/route/locale-en.json`
  - `neutral/route/locale-es.json`
  - `neutral/route/locale-fr.json`
  - `neutral/route/locale-de.json`
- Route-specific translations:
  - `neutral/route/root/test1/locale.json`
  - `neutral/route/root/test2/locale.json`

Includes translations for template text and for strings defined in `data.json` (`title`, `description`, `h1`).

## Key Structure

```text
src/component/cmp_7000_hellocomp/
├── manifest.json
├── schema.json
├── route/
│   ├── routes.py
│   └── dispatcher_hellocomp.py
├── neutral/
│   ├── component-init.ntpl
│   ├── obj/
│   │   ├── comp.json
│   │   └── locale-obj-comp.json
│   └── route/
│       ├── index-snippets.ntpl
│       ├── locale-*.json
│       └── root/
│           ├── content-snippets.ntpl
│           ├── ajax/example/content-snippets.ntpl
│           ├── ajax/modal-content/content-snippets.ntpl
│           ├── test1/
│           └── test2/
├── src/comp.py
└── tests/
```

## Tests

```bash
source .venv/bin/activate && pytest -q src/component/cmp_7000_hellocomp/tests
```

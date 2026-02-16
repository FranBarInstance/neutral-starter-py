# AJAX Requests and `Requested-With-Ajax`

This document explains how AJAX requests are detected in this project and why the `Requested-With-Ajax` header matters.

## Core Rule

Many runtime behaviors (templates, cookies, token handling, route guards) branch on:

- `Requested-With-Ajax`

If that header is missing when expected, behavior can differ from standard in-app AJAX flows.

## Neutral TS Behavior

When a request is triggered via Neutral templates using `{:fetch; ... :}`, the Neutral JS runtime (`neutral.min.js`) ensures the AJAX header is present automatically.

The same applies when using Neutral's JS helpers directly.

In this project, Neutral auto-JS injection is disabled at schema level (`src/app/schema.json` uses `"disable_js": true`), so the runtime script is included manually in the base template (`cmp_0200_template`).

This means `{:fetch; ... :}` still works as expected, as long as `neutral.min.js` is loaded.

Official Neutral TS reference:

- https://franbarinstance.github.io/neutralts-docs/docs/neutralts/doc/#fetch--

## Plain JavaScript Behavior

If you send requests using custom JavaScript (`fetch`, `XMLHttpRequest`, etc.) outside the Neutral fetch flow, you must ensure this header is set yourself when you want AJAX semantics used by this app.

Example:

```js
fetch("/some/route", {
  method: "POST",
  headers: {
    "Requested-With-Ajax": "true",
    "Content-Type": "application/x-www-form-urlencoded"
  },
  body: new URLSearchParams({ key: "value" })
});
```

Note: server-side logic checks header presence (case-insensitive). The exact value is less important than ensuring the header exists.

## Using Neutral JS Without `{:fetch; ... :}`

You can also trigger AJAX flows via Neutral JS helpers/classes instead of writing `{:fetch; ... :}` directly in templates.

Common patterns include:

- Using Neutral JS functions (for example `neutral_fetch(...)` in custom scripts).
- Using Neutral CSS hooks/classes consumed by `neutral.min.js` (for example `neutral-fetch-form`, `neutral-fetch-click`, `neutral-fetch-visible`).

These paths still set the AJAX header through the Neutral runtime.

## Why It Matters in This Project

The dispatcher checks this header to determine AJAX mode. In AJAX mode:

- UTOKEN is extracted without forced rotation.
- Cookie refresh logic is skipped.
- Layout/templates may render AJAX-specific fragments instead of full page wrappers.

Some routes/components also explicitly require this header for AJAX-only endpoints.

## Scope Clarification

This convention is for app routes rendered/handled through the Neutral + Dispatcher flow.

It is not a requirement for independent API endpoints you may implement outside that rendering flow.

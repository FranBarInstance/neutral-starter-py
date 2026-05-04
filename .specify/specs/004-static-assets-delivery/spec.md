# Specification 004 - Static Asset Delivery and Performance

## Executive Summary

This specification defines the architectural pattern for efficient static asset
delivery (CSS, JS, images, and similar files) in Neutral Starter Py
applications. The main goal is to remove static file serving work from the
application server (Flask/Python) and delegate it directly to the web server
(Nginx/Apache) or to a CDN.

To achieve this, the system adopts the **Try Public First** pattern together
with a dynamic global variable for frontend static path resolution.

## Goals

- **Performance:** Minimize application-server load by serving static files
  directly from the web server.
- **Scalability:** Make CDN integration transparent without forcing template
  rewrites.
- **Standardization:** Define a clear contract for how developers reference
  static assets in NTPL views.

## The `public/` Directory

The `public/` directory at the project root acts as the first delivery layer
for static content. Unlike the `/static/` directory encapsulated inside each
component, `public/` is exposed directly by the HTTP server.

### Primary Uses

1. Global shared static assets such as `favicon.ico`, `robots.txt`, and fonts.
2. A root directory or mirror/cache that lets the web server resolve the
   request before proxying to the Python application.

## Component Static Assets

Assets inside a component `/static/` directory belong to that component's
internal contract. The component must work correctly without moving any of its
assets into `public/`; publishing component assets into `public/` or to a CDN
is an optional optimization, not a functional requirement.

The decision about which assets may be published belongs to the component
itself. Only the component knows whether a file is safe to expose as public
static content or must continue to be served through the application.

If a component includes static files that may be copied into `public/`, it
must document them explicitly. For each publishable asset, the component must
state:

- the source path inside the component;
- the expected public path under `public/`;
- any load-order, dependency, or security restrictions.

Until an automatic publication mechanism exists, copying those assets into
`public/` remains a manual install, update, or deployment step.

Templates may use `{:;current->site->static:}` only for assets that physically
exist in `public/` or in the configured CDN. Internal assets that have not
been published must keep using the mechanism defined by their own component.

## Infrastructure Configuration: The "Try Public First" Pattern

In production, the web server (for example, Nginx) should be configured to try
serving any request from `/public/` first. If the file exists physically, the
web server serves it directly. If it does not exist, the request is forwarded
to the Flask application through WSGI.

### Example Standard Nginx Configuration

```nginx
server {
    listen 80;
    server_name your_server_name;
    root <deploy.root>;

    location / {
        try_files /public$uri @wsgi;
    }

    location /public/ {
        alias <deploy.root>/public/;
    }

    location @wsgi {
        include uwsgi_params;
        uwsgi_pass unix:<uwsgi.socket>;
        uwsgi_param SCRIPT_NAME /;
        uwsgi_modifier1 30;
    }
}
```

## The CDN Environment Variable: `current.site.static`

The base site component already exposes a global configuration variable named
`static` in its schema.

Example base site `/schema.json`:

```json
{
    "data": {
        "current": {
            "site": {
                "static": "/"
            }
        }
    }
}
```

- **Local/default environment:** Points to `/`. Requests stay on the same
  domain and hit the Nginx `try_files` flow.
- **Production with CDN:** The value may be overridden in production
  (through `custom.json` or the configuration database) to a CDN domain, such
  as `https://cdn.example.com/`. Once changed, the whole application starts
  requesting public assets from the CDN without code changes.

`current.site.static` must always end with `/`. Asset paths concatenated after
this variable must not start with `/`.

## Developer Contract for NTPL Templates

For the CDN system and `public/` directory to work correctly, developers must
not hardcode absolute static asset paths in `.ntpl` templates.

Every static asset reference must be prefixed with
`{:;current->site->static:}`.

CSP-sensitive tags such as `<script>` and `<link>` must include
`nonce="{:;CSP_NONCE:}"` when used in NTPL templates.

### Incorrect

```html
<link nonce="{:;CSP_NONCE:}" rel="stylesheet" href="/css/style.css">
<img src="/img/logo.jpg" alt="Logo">
<script nonce="{:;CSP_NONCE:}" src="/js/app.js"></script>
```

### Correct

```html
<link nonce="{:;CSP_NONCE:}" rel="stylesheet" href="{:;current->site->static:}css/style.css">
<img src="{:;current->site->static:}img/logo.jpg" alt="Logo">
<script nonce="{:;CSP_NONCE:}" src="{:;current->site->static:}js/app.js"></script>
```

> If `static` equals `/`, the final rendered result is `/img/logo.jpg`. If the
> variable points to a CDN, the rendered output becomes
> `https://cdn.example.com/img/logo.jpg`.

## Development Environment and Lightweight Deployments (`cmp_9100_catch_all`)

In production, delegating static delivery to Nginx or Apache is the preferred
performance strategy. However, the project also supports out-of-the-box
operation without external infrastructure through the `cmp_9100_catch_all`
component. This component acts as a safety net and simulates static-server
behavior entirely in Flask.

### The Role of the `cmp_9*` Prefix

In `src/app/components.py`, components whose folder starts with `cmp_9*` are
intentionally processed at the end of blueprint registration. This places
their routes after ordinary component routes so they can work as a fallback
layer when no earlier specific route has matched the request.

Within the `cmp_9*` group itself, relative order still depends on the load
order applied by `components.py`. Therefore `cmp_9100_catch_all` should not be
treated as an unreplaceable fallback: another `cmp_9*` component may add,
extend, or override fallback behavior if it ends up with higher effective
priority.

### Selective Capture of File-Like Routes

`cmp_9100_catch_all` implements a dedicated route for file-like paths
(`/<anyext:asset_path>`). The `anyext` converter does not validate against a
closed extension list; it accepts any path whose last segment contains a dot,
such as `css/app.css`, `favicon.ico`, or `files/archive.v1`.

Its behavior is:

1. **Catch:** Intercept any unresolved request that matches the `anyext`
   pattern, meaning the last segment contains a dot.
2. **Check:** Test whether the file exists physically under
   `Config.STATIC_FOLDER` (mapped to `public/`).
3. **Serve:** If the file exists, return it with the headers configured in
   `Config.STATIC_CACHE_CONTROL`. If it does not exist, return a controlled
   standard 404 response instead of an infrastructure error.

This creates a transparent double barrier:

- **Barrier 1 (infrastructure):** If Nginx or Apache is present, it intercepts
  the static route and serves directly from `public/`.
- **Barrier 2 (Flask fallback):** If no intermediate web server exists
  (local development, standalone Docker, and similar setups), the request
  travels through components until `cmp_9100_catch_all` intercepts it, looks
  in the same `public/` directory, and serves it with equivalent behavior.

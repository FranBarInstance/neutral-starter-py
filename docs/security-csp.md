# Security and CSP Guide

This project ships with secure defaults and strict request/header validation. This guide explains how to configure those controls in `config/.env` for development and production.

## Overview

Security is enforced in four layers:

1. Content Security Policy (CSP): blocks external resources unless explicitly allowed.
2. Host allow-list (`ALLOWED_HOSTS`): validates the `Host` header on every request.
3. Trusted proxy boundaries (`TRUSTED_PROXY_CIDRS`): controls when forwarded headers are trusted.
4. Browser security headers: `Referrer-Policy` and optional `Permissions-Policy`.

## Host and Proxy Trust Boundaries

Use these variables in production:

```ini
# Allowed request hosts (comma separated, wildcard supported)
# Example: localhost,*.example.com,my-other-domain.org
ALLOWED_HOSTS=localhost

# Trusted reverse proxy CIDRs (comma separated)
# Example: 127.0.0.1/32,::1/128,10.0.0.0/8
TRUSTED_PROXY_CIDRS=
```

Behavior:

- `ALLOWED_HOSTS`: requests with a non-allowed `Host` are rejected (`400`).
- `TRUSTED_PROXY_CIDRS`: only requests coming from these proxy networks can provide forwarded headers (such as `X-Forwarded-Proto`, `X-Forwarded-For`, `X-Forwarded-Host`). For non-trusted origins, those headers are stripped.

Recommendation:

- Keep `ALLOWED_HOSTS` explicit in production (avoid broad wildcards unless necessary).
- Set `TRUSTED_PROXY_CIDRS` when running behind Nginx, Traefik, load balancers, or platform ingress.

## CSP Configuration

By default, CSP is strict. If an external domain is not declared, the browser blocks it.

Set the allowed origins by resource type:

```ini
# Security Content-Security-Policy (CSP) allowed domains
CSP_ALLOWED_SCRIPT=https://cdnjs.cloudflare.com
CSP_ALLOWED_STYLE=https://cdnjs.cloudflare.com,https://fonts.googleapis.com
CSP_ALLOWED_IMG=https://picsum.photos,https://fastly.picsum.photos
CSP_ALLOWED_FONT=https://cdnjs.cloudflare.com,https://fonts.gstatic.com
CSP_ALLOWED_CONNECT=https://cdnjs.cloudflare.com,https://picsum.photos,https://fastly.picsum.photos
CSP_ALLOWED_FRAME=
```

Unsafe directives are disabled by default:

```ini
# Security Content-Security-Policy (CSP) unsafe directives
CSP_ALLOWED_SCRIPT_UNSAFE_INLINE=false
CSP_ALLOWED_SCRIPT_UNSAFE_EVAL=false
CSP_ALLOWED_STYLE_UNSAFE_INLINE=false
```

Recommendations:

- Keep unsafe directives disabled in production whenever possible.
- Add only domains you actually use.
- If a component adds new JS/CSS/fonts/images from external sources, update the relevant `CSP_ALLOWED_*` variable.

## Additional Security Headers

```ini
# Referrer policy (SEO-friendly: cross-site requests receive only origin, not path)
REFERRER_POLICY=strict-origin-when-cross-origin

# Permissions-Policy (optional). Empty = do not send header
# Example: geolocation=(), microphone=(), camera=(), payment=()
PERMISSIONS_POLICY=
```

Notes:

- `REFERRER_POLICY` default is `strict-origin-when-cross-origin`: same-origin keeps full referrer; cross-origin sends origin only.
- `PERMISSIONS_POLICY` is optional and unset by default.

## Development vs Production

In development, you may relax CSP to speed up integration testing with third-party assets.

Example:

```ini
CSP_ALLOWED_STYLE=*
```

This is convenient but less secure. Prefer explicit domains in production.

## Quick Troubleshooting

- Browser console shows CSP errors:
  - Add the blocked origin to the matching `CSP_ALLOWED_*` variable.
- App behind reverse proxy behaves incorrectly (URL scheme/host/client IP):
  - Verify `TRUSTED_PROXY_CIDRS` includes your proxy network.
- Unexpected `400` due to host validation:
  - Ensure the domain is present in `ALLOWED_HOSTS`.

## Production Checklist

- `ALLOWED_HOSTS` set to real domains.
- `TRUSTED_PROXY_CIDRS` set when using reverse proxies.
- No unnecessary wildcard (`*`) entries in CSP.
- Unsafe CSP directives remain `false` unless justified.
- `REFERRER_POLICY` and `PERMISSIONS_POLICY` reviewed for your compliance/privacy needs.

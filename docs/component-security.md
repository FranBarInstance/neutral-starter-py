# Component Security Configuration

## Overview

The component security system controls access to routes through two mandatory policies defined in each component's `manifest.json`:

- **`routes_auth`**: Controls whether authentication is required
- **`routes_role`**: Controls which roles can access specific routes

## Manifest Structure

```json
{
    "uuid": "example_0yt2sa",
    "name": "Example Component",
    "route": "/example",
    "security": {
        "routes_auth": {
            "/": false,
            "/admin": true
        },
        "routes_role": {
            "/": ["*"],
            "/admin": ["admin", "dev"]
        }
    }
}
```

## Policy: routes_auth

Controls whether a session-authenticated user is required for each route.

### Values

| Value | Meaning |
|-------|---------|
| `true` | Authentication required (user must have a valid session) |
| `false` | Public route (no authentication required) |

### Examples

```json
{
    "routes_auth": {
        "/": false,           // Public homepage
        "/profile": true,     // Requires login
        "/admin": true        // Requires login
    }
}
```

## Policy: routes_role

Controls which roles can access each route.

### Values

| Value | Meaning |
|-------|---------|
| `["*"]` | Wildcard - any role is allowed (including no role if auth not required) |
| `["admin", "dev"]` | Only users with "admin" OR "dev" role |
| `["moderator"]` | Only users with "moderator" role |

### Role Matching

- Role matching uses **OR** logic: user needs ANY of the listed roles
- Roles are case-insensitive but stored in lowercase
- The wildcard `"*"` cannot be mixed with explicit roles in the same entry

### Examples

```json
{
    "routes_role": {
        "/": ["*"],                              // Anyone can access
        "/user": ["admin", "dev", "moderator"],  // Admin, dev, or moderator
        "/profile": ["admin", "dev"],            // Only admin or dev
        "/admin": ["admin"]                      // Only admin
    }
}
```

## Route Matching

Policies use **prefix matching** (most specific wins):

| Route | Policy Key `/` | Policy Key `/admin` | Result |
|-------|----------------|---------------------|--------|
| `/` | ✅ Matches | ❌ | Uses `/` policy |
| `/admin` | ✅ | ✅ Matches | Uses `/admin` policy (more specific) |
| `/admin/users` | ✅ | ✅ Matches | Uses `/admin` policy |

### Simplifying Security Configuration

When **all routes in a component share the same security requirements**, you only need to define the root route `"/"`:

```json
{
    "security": {
        "routes_auth": {
            "/": true
        },
        "routes_role": {
            "/": ["*"]
        }
    }
}
```

This single configuration applies to all routes in the component:
- `/component`
- `/component/profile`
- `/component/profile/ajax`
- `/component/admin`
- etc.


```json
{
    "security": {
        "routes_auth": {
            "/": true
        },
        "routes_role": {
            "/": ["*"],
            "/admin": ["admin"],
        }
    }
}
```

In this last case, the `/component/admin` route will be accessible only to users with the "admin".

## Evaluation Order

When a request is received, security is evaluated in this order:

1. **Authentication Check** (`routes_auth`)
   - If route requires auth and user is not authenticated → **401**

2. **Status Restrictions** (core policy)
   - If user has restricted status (deleted, moderated, etc.) → **403**

3. **Role Check** (`routes_role`)
   - If user doesn't have required role → **403**

## Mandatory Fields

### Required Structure

Both `routes_auth` and `routes_role` are **mandatory** in the `security` block:

```json
{
    "security": {
        "routes_auth": {},  // REQUIRED - cannot be omitted
        "routes_role": {}   // REQUIRED - cannot be omitted
    }
}
```

### Root Route Requirement

At minimum, the root route `"/"` must be defined in both policies:

```json
{
    "security": {
        "routes_auth": {
            "/": false  // REQUIRED
        },
        "routes_role": {
            "/": ["*"]   // REQUIRED
        }
    }
}
```

> **Fail-Closed Behavior**: If a route is not mapped in either policy, access is **denied by default**.

## Complete Examples

### Public Component

```json
{
    "uuid": "public_0yt2sa",
    "name": "Public Component",
    "route": "/public",
    "security": {
        "routes_auth": {
            "/": false
        },
        "routes_role": {
            "/": ["*"]
        }
    }
}
```

### Authenticated Component (Any User)

```json
{
    "uuid": "private_0yt2sa",
    "name": "Private Component",
    "route": "/private",
    "security": {
        "routes_auth": {
            "/": true
        },
        "routes_role": {
            "/": ["*"]
        }
    }
}
```

### Admin-Only Component

```json
{
    "uuid": "admin_0yt2sa",
    "name": "Admin Panel",
    "route": "/admin",
    "security": {
        "routes_auth": {
            "/": true
        },
        "routes_role": {
            "/": ["admin", "dev"]
        }
    }
}
```

### Mixed Access Component

```json
{
    "uuid": "mixed_0yt2sa",
    "name": "Mixed Component",
    "route": "/mixed",
    "security": {
        "routes_auth": {
            "/": false,        // Public homepage
            "/dashboard": true, // Requires login
            "/admin": true      // Requires login
        },
        "routes_role": {
            "/": ["*"],                    // Public
            "/dashboard": ["*"],           // Any authenticated user
            "/admin": ["admin", "dev"]     // Only admin/dev
        }
    }
}
```

## Validation Rules

At application startup, the framework validates:

1. `security.routes_role` exists and is a dictionary
2. `security.routes_auth` exists and is a dictionary
3. Route keys are normalized absolute paths (start with `/`)
4. Role lists are non-empty arrays of strings
5. `"*"` is not mixed with explicit roles in the same entry

**Any validation error will prevent the application from starting** (fail-closed design).



## Best Practices

1. **Always define `"/"`** in both policies as a fallback
2. **Use specific paths** for sensitive routes (`/admin`, `/api/private`)
3. **Use wildcard sparingly** - only for truly public routes
4. **Test with different roles** to ensure permissions work as expected
5. **Keep role names consistent** across components (lowercase recommended)

## Special Roles

### The `dev` Role

The `dev` role is **special** and behaves differently from other roles:

- **NOT stored in database**: The `dev` role should never be added to the database role tables
- **Development-only**: Automatically granted when using `SessionDev` (local development login)
- **Cannot be assigned**: Do not assign `dev` role to users via `create_user.py` or admin panels
- **Local access only**: Intended strictly for local development and debugging

```json
// Valid use in manifest - allows access during local development
{
    "routes_role": {
        "/": ["admin", "dev"]  // dev is valid here for local testing
    }
}
```

**Production deployments** should remove `dev` from all `routes_role` entries.

### Standard Roles

These roles are stored in the database and can be assigned to users:

| Role | Typical Use |
|------|-------------|
| `admin` | Full system administration |
| `moderator` | Content moderation, user management (limited) |
| `editor` | Content creation and editing |

## Troubleshooting

### Access Denied (403)

Check the logs for the deny reason:
- `route_not_mapped_in_auth_policy` - Add route to `routes_auth`
- `route_not_mapped_in_roles_policy` - Add route to `routes_role`
- `auth_required` - User needs to log in
- `role_not_allowed` - User doesn't have required role

### Missing Security Section

If you see errors at startup:
```
missing_routes_auth_policy
missing_routes_role_policy
```

Add the `security` block with both required policies to your `manifest.json`.

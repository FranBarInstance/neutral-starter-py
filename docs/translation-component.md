# Translation Guide

> [!NOTE]
> You can ask the AI to translate a full component using the `translate-component` skill.

This guide documents how translations are handled in this project and what is recommended when writing templates.

## 1. Always Use `{:trans; ... :}` for UI Text

Prefer:

```html
<div>{:trans; Hello :}</div>
```

over:

```html
<div>Hello</div>
```

Why:

- It keeps templates ready for future localization.
- If no translation is configured yet, `{:trans; Hello :}` still resolves to `Hello`, so behavior is safe by default.

## 2. Where to Put Translations

### Global/Shared Translations (`schema.json`)

Put translations in component `schema.json` when they must be available broadly, for example:

- menu labels (`drawer` / `menu`),
- shared snippet text that can appear in other components/routes,
- reusable references such as `ref:*` keys used across multiple templates.

Typical location:

- `inherit.locale.trans`

Example:
```json
{
    "inherit": {
        "locale": {
            "trans": {
                "en": {},
                "es": {
                    "User": "Usuario",
                    "Sign in": "Iniciar sesión",
                    "Sign out": "Cerrar sesión"
                }
            }
        }
    },
    "data": {
        "current": {
            "drawer": {
                "menu": {
                    "session:": {
                        "user": {
                            "name": "User",
                            "tabs": "user",
                            "icon": "x-icon-user"
                        }
                    },
                    "session:true": {
                        "user": {
                            "name": "User",
                            "tabs": "user",
                            "icon": "x-icon-user"
                        }
                    }
                }
            },
            "menu": {
                "session:": {
                    "user": {
                        "login": {
                            "text": "Sign in",
                            "link": "[:;data->sign_0yt2sa->manifest->route:]/in",
                            "icon": "x-icon-sign-in"
                        }
                    }
                },
                "session:true": {
                    "user": {
                        "logout": {
                            "text": "Sign out",
                            "link": "[:;data->sign_0yt2sa->manifest->route:]/out",
                            "icon": "x-icon-sign-out"
                        }
                    }
                }
            }
        },
        "navbar": {
            "menu": {
                "session:": {
                    "signin": {
                        "name": "Sign in",
                        "link": "#loginModal",
                        "icon": "x-icon-sign-in",
                        "prop": {
                            "data-bs-toggle": "modal",
                            "data-bs-target": "#loginModal"
                        }
                    }
                },
                "session:true": {
                    "signout": {
                        "name": "Sign out",
                        "link": "#logoutModal",
                        "icon": "x-icon-sign-out",
                        "prop": {
                            "data-bs-toggle": "modal",
                            "data-bs-target": "#logoutModal"
                        }
                    }
                }
            }
        }
    }
}
```

### Route/Component Template Translations (locale files)

For route-specific page text, use locale files loaded from templates via `{:locale; ... :}`.

In this project, locale files are JSON (not JS), commonly:

- `locale-en.json`
- `locale-es.json`
- `locale-fr.json`
- `locale-de.json`

They can technically use other names, but `locale-xx.json` is the preferred convention.

### Example: `locale-xx.json` (single language file)

Example based on `src/component/cmp_7000_hellocomp/neutral/route/locale-es.json`:

```json
{
    "__comment_:trans": "This translation will be available for the entire Component",
    "trans": {
        "es": {
            "Hello Component": "Componente Hola",
            "Component example, ilustrates the basic structure of a component": "Componente ejemplo, ilustra la estructura básica de un componente",
            "Example of a simple component": "Ejemplo de un componente simple",
            "Hello from hello component": "Hola desde el componente hello"
        }
    }
}
```

### Example: `locale.json` (multiple languages in one file)

```json
{
    "__comment_:trans": "Multi-language locale example",
    "trans": {
        "es": {
            "Hello Component": "Componente Hola",
            "Component example, ilustrates the basic structure of a component": "Componente ejemplo, ilustra la estructura básica de un componente",
            "Example of a simple component": "Ejemplo de un componente simple",
            "Hello from hello component": "Hola desde el componente hello"
        },
        "de": {
            "Hello Component": "Hallo-Komponente",
            "Component example, ilustrates the basic structure of a component": "Komponentenbeispiel, veranschaulicht die grundlegende Struktur einer Komponente",
            "Example of a simple component": "Komponentenbeispiel, veranschaulicht die grundlegende Struktur einer Komponente",
            "Hello from hello component": "Hallo vom hello component"
        },
        "fr": {
            "Hello Component": "Composant Bonjour",
            "Component example, ilustrates the basic structure of a component": "Composant exemple, illustre la structure de base d'un composant",
            "Example of a simple component": "Exemple d'un composant simple",
            "Hello from hello component": "Bonjour du composant hello"
        }
    }
}
```

## 3. Load Scope and Override Behavior

Translations can be loaded at different scopes. Later loads override previous keys when the same translation key exists.

### Route scope (most specific)

Load only for one route/subroute (example: `root/test1`):

```ntpl
{:locale; {:flg; require :} >> #/locale.json :}
```

Example location:

- `src/component/cmp_7000_hellocomp/neutral/route/root/test1/content-snippets.ntpl`

### Component route scope

Load once for all routes in a component (from `neutral/route/index-snippets.ntpl`).

To load only current language (more efficient), use:

```ntpl
{:locale;
    #/locale-{:lang;:}.json
:}{:else;
    {:locale; #/locale-en.json :}
:}
```

Example location:

- `src/component/cmp_7000_hellocomp/neutral/route/index-snippets.ntpl`

### Application-wide scope

If translations must be available globally across components, use one of these:

- Component/app `schema.json` in `inherit.locale.trans`
- `neutral/component-init.ntpl` with `{:locale; ... :}`

## 4. Placement Strategy (Important)

Place locale files as close as possible to the route where they are needed.

Why:

- It is more efficient: only necessary translations are loaded.
- It reduces global translation noise.
- It keeps component maintenance easier as pages grow.

Examples:

- Component-level route locale: `src/component/<cmp>/neutral/route/locale-xx.json`
- Subroute-only locale: `src/component/<cmp>/neutral/route/root/<subroute>/locale.json`

## 5. Workflow

Recommended workflow:

1. Ensure UI text in NTPL is wrapped with `{:trans; ... :}`.
2. Ask AI to run `translate-component` for the target component.
3. Review generated/updated `locale-xx.json` files.
4. Keep shared/global translation keys in `schema.json` when needed app-wide.

## 6. Strategy for translating content

The Neutral TS translation system is designed to translate the user interface of components. Therefore, it is not intended to translate the content of components.

Taking advantage of Neutral TS features, we can load specific content for each language. We can see an example in the component `cmp_7000_hellocomp` at `src/component/cmp_7000_hellocomp/neutral/route/root/translating-content`.

In `content-snippets.ntpl` we have the following:

```ntpl
{:snip; current:template:body-main-content >>
    <div class="container">
        {:include; #/content-{:lang;:}.ntpl :}
        {:else; {:include; #/content-en.ntpl :} :}
    </div>
:}
```

At the same time, in the same path we have different files for each language, `content-en.ntpl`, `content-es.ntpl`, etc.

What happens is that with `{:include; #/content-{:lang;:}.ntpl :}` it will try to load the file for the current language, and if it doesn't exist, it will load the default file `content-en.ntpl`.

This same strategy can be followed with snippets:

```ntpl
{:snip; content-en >>
    English
:}
{:snip; content-es >>
    Español
:}
```

And then in `content-snippets.ntpl` we can have the following:

```ntpl
{:snip; current:template:body-main-content >>
    <div class="container">
        {:snip; content-{:lang;:} :}{:else; {:snip; content-en :} :}
    </div>
:}
```

`{:lang;:}` contains the current language, for example `en`.

---

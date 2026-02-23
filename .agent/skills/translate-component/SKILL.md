---
name: translate-component
description: Create or modify components translations. Extract and translate web template strings from Neutral TS (.ntpl) files into component-specific locale JSON files.
---

# Translate Component Skill

This skill allows the agent to automatically find, extract, and translate strings within Neutral TS template files (`*.ntpl`) and update the corresponding localization files (`locale-xx.json`).

- Use `view_file` on `docs/translation-component.md` for more advanced options.
- Use `view_file` on `src/component/cmp_7000_hellocomp` as a component example.

- **IMPORTANT**: The components are isolated parts, and nothing should be changed outside of their directory structure.

## Context

In Neutral TS projects, web templates use the format `{:trans; Text to translate :}` or `{:trans; ref:reference_key :}`. These translations are stored in JSON files located in the component's `route` directory, named `locale-xx.json` (where `xx` is the language code).

## Languages to translate

Translate to the languages ​​requested; if nothing is specified, the available languages ​​are indicated in `src/component/cmp_0500_locale/schema.json` `data.current.site.languages`.

- Use `view_file` on `dsrc/component/cmp_0500_locale/schema.json` to get the available language to translate.

### Translation Storage Locations

There are several places where translations can be stored:

- **schema.json**: This file only includes translations for global elements, such as menus and content in `component-init.ntpl`.
- **locale.json**: This file includes translations for specific routes; the file can have a different name.
- **locale-xx.json**: This file includes translations for all routes of the component. This is the ideal system.

In the following example, since the texts are already in English, it is not necessary to translate them into English. The default language is usually English, unless otherwise specified.

**schema.json**:
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
        },
        "data": {
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
}
```

**locale-xx.json** contains only the language `xx`:

```json
{
    "trans": {
        "xx": {
            "Text or ref:key": "Translation"
        }
    }
}
```

**locale.json** contains all languages in a single file:

```json
{
    "trans": {
        "en": {
            "Text or ref:key": "Translation"
        },
        "es": {
            "Text or ref:key": "Translation"
        },
        "fr": {
            "Text or ref:key": "Translation"
        }
    }
}
```

**The best strategy** (when modifying a component, you may encounter different strategies) is to use `schema.json` for global texts (menus and `component-init.ntpl` content) and `locale-xx.json` for texts that appear in any route of the component. Place these files in the folder: `src/component/cmp_XXXX_componentname/neutral/route`, and they are loaded in `src/component/cmp_XXXX_componentname/neutral/route/index-snippets.ntpl` as follows:

```
{:locale;
    #/locale-{:lang;:}.json
:}{:else;
    {:locale; #/locale-en.json :}
:}
```

## Workflow

1.  **Identify Component Path**:
    Determine the base directory of the component (e.g., `src/component/cmp_XXXX_componentname/`).

2. **Identify Global Translations**:
    - Look for menu texts in `schema`: `data.drawer.menu.session.rrss.name` and `menu.session.xxxx.xxxx.text`.
    - Look for texts with the pattern `{:trans; ... :}` in the file `src/component/cmp_XXXX_componentname/neutral/component-init.ntpl` and put them in `schema.json`.
    - **schema.json Translation**: Scan `schema.json` for any text strings in:
        - `data.drawer.menu.*.name`
        - `data.drawer.menu.*.tabs`
        - `data.menu.*.*.text`
        - `data.navbar.menu.*.name`
        - Any other human-readable text fields that should be translated
    - Add these texts to the translations in `schema.json` under `inherit.locale.trans`.

3.  **Scan for Template Files**:
    Find all `*.ntpl` files recursively within that directory.

4.  **Extract Strings**:
    Identify all strings marked for translation using the pattern `{:trans; (.*?) :}`.
    -   **References**: Strings starting with `ref:` (e.g., `ref:error_required`). These need translation in **all** languages, including English.
    -   **Default Text**: Plain text strings (e.g., `Login`). These are typically in English and only need translation in non-English locale files.

5.  **Manage Locale Files**:
    Locate or create the following files in the `neutral/route/` subdirectory:
    -   `locale-en.json`
    -   `locale-es.json`
    -   `locale-fr.json`
    -   `locale-de.json`

6.  **Update JSON Content**:
    Each file must strictly follow this structure:
    ```json
    {
        "trans": {
            "xx": {
                "Text or ref:key": "Translation"
            }
        }
    }
    ```
    *Note: Replace `xx` with the language code (es, fr, de, etc.).*

7.  **Preservation**:
    When updating existing files, do not remove current translations. Add new strings and update existing ones if necessary.

## Translation Source-Language Rule (Important)

For `{:trans; ... :}` with plain text (not `ref:`), the phrase itself is the source text.

- If a phrase is already written in language `xx`, do not add a redundant translation entry for `xx`.
- Add translations only for the other target languages.
- This rule is language-agnostic: the source language can be English, Spanish, French, etc., as long as that source is used consistently for the phrase.

### Exception: `ref:` keys

If translations use reference keys, for example `{:trans; ref:text:greeting :}`, the key must be defined in every locale (including the source language), because `ref:text:greeting` is an identifier, not display text.

### Examples

- Plain text:
  - `{:trans; Hello :}`
  - `Hello` is already English source text, so an `en` entry is optional/redundant.
  - Provide `es`, `fr`, `de`, etc.

- Reference key:
  - `{:trans; ref:text:greeting :}`
  - Must exist in all locales: `en`, `es`, `fr`, `de`, etc.

## Helper Commands

**Find all unique translation tags:**
```bash
grep -roPh "{:trans; .*? :}" [component_path] | sort | uniq
```

**Clean extraction of keys:**
```bash
grep -roPh "{:trans; .*? :}" [component_path] | sed 's/{:trans; \(.*\) :}/\1/' | sort | uniq
```

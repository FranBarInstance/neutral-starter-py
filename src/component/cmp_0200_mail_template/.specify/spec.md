# Component: mail_template_0yt2sa

## Executive Summary

This component acts as the **default template provider** for the mail system (`010-mail-system`).
Its sole responsibility is to provide the visual layout (HTML/CSS) and content snippets for different system emails (registration, password recovery, etc.).

It contains no transport logic or Python sending helpers; all of that is handled abstractly by `core/mail.py` according to the `010-mail-system` specification.

## Identity

- **UUID**: `mail_template_0yt2sa`
- **Base Route**: `` (no routes - provides templates only)
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": false
}
- **Allowed roles**: {
  "/": [
    "*"
  ]
}

## Normative References

- `specs/010-mail-system/spec.md` - Sistema de transporte de correos.
- `specs/010-mail-system/provider-spec.md` - Contrato para proveedores de plantillas.
- `specs/009-i18n-standard/spec.md` - Internacionalización de plantillas.
- `specs/002-neutral-templates-standard/spec.md` - Sintaxis NTPL.

---

## 1. Contrato de Proveedor

Este componente cumple estrictamente con `provider-spec.md`:

1.  **Registro**: Su `__init__.py` llama a `set_current_mail_template()` durante el arranque para registrar su ruta en el schema.
2.  **Layout**: Provee `neutral/layout/index.ntpl` que sirve como plantilla base (`MAIL_TEMPLATE_LAYOUT`).
3.  **Consumo de contenido**: El layout usa la instrucción de inclusión NTPL `{:^include; {:flg; require :} >> #/mail-{:;current_mail->content_template:}-snippets.ntpl :}` para inyectar el contenido específico dinámicamente según lo que pase el consumidor.
4.  **Datos locales**: Usa `local-data.json` en su carpeta de layout para definir sus colores o variables por defecto (ej: `header_color`), utilizando `{:else; ... :}` en el layout si el `layout_data` inyectado por el consumidor no proporciona esos valores.

---

## 2. Estructura de Directorios

```text
src/component/cmp_0200_mail_template/
├── manifest.json               # Define uuid y dependencias
├── __init__.py                 # Llama a set_current_mail_template()
└── neutral/
    └── layout/
        ├── index.ntpl          # Layout maestro y despachador
        ├── local-data.json     # Variables visuales por defecto (ej. header_color)
        ├── locale.json         # Traducciones de los textos de los correos
        ├── theme.ntpl          # Layout general del correo (estructura HTML)
        ├── theme-snippets.ntpl # Snippets base del theme
        ├── mail-account-pin-snippets.ntpl
        ├── mail-pin-snippets.ntpl
        ├── mail-register-snippets.ntpl
        ├── mail-reminder-snippets.ntpl
        └── mail-sample-snippets.ntpl
```

---

## 3. Comportamiento del Layout

El `index.ntpl` estructura el email utilizando tablas (compatibilidad con clientes de correo), un header (generalmente con el logo), el bloque central para el snippet de contenido y un footer.

Ejemplo de uso de variables en el layout:

```html
<style nonce="{:;CSP_NONCE:}">
    /* El caller puede inyectar header_color, si no, se usa el local-data.json */
    .header { background-color: {:;current_mail->header_color:}{:else; {:;current->mail_template->header_color:} :}; }
</style>

<!-- Logo del sitio con fallback a data del schema -->
<img src="{:;current_mail->logo:}{:else; {:;current->site->logo:} :}" alt="{:;current->site->name:}">

<div class="content">
    <!-- Inyección dinámica del contenido -->
    {:^include; {:flg; require :} >> #/mail-{:;current_mail->content_template:}-snippets.ntpl :}
</div>
```

**Jerarquía de resolución esperada:**
1.  `current_mail->X`: Valor pasado explícitamente por el consumidor en `layout_data` o `mail_data` a través de `Mail.send()`.
2.  `current->mail_template->X`: Valor definido en el `local-data.json` del componente.
3.  `current->site->X`: Valores globales configurados a nivel de sitio.

---

## 4. Diseño de Snippets

Los archivos `-snippets.ntpl` (por ejemplo `mail-register-snippets.ntpl`) definen únicamente el contenido interior del correo (etiquetas `<h1>`, `<p>`, enlaces/botones).

No se preocupan del `<head>`, ni del layout externo. Extraen las variables dinámicas de `current_mail`.

**Ejemplo de `mail-register-snippets.ntpl`:**
```html
<h1>{:trans; Welcome, :} {:;current_mail->alias:}!</h1>

<p>{:trans; Thank you for joining us. Please use this verification code: :}</p>

<h2>{:;current_mail->code:}</h2>

<p>{:trans; This code expires soon. :}</p>
```

Al integrarse todo, si el consumidor ejecuta `mail.send('register', mail_data={'alias': 'Juan', 'code': '123456', ...})`, el core inyectará el `mail-register-snippets.ntpl` dentro del `index.ntpl` reemplazando los parámetros.

---

## 5. Acceptance Criteria (SDD)

### Functional
- [x] `__init__.py` registers component via `set_current_mail_template()`
- [x] Provides `neutral/layout/index.ntpl` as master layout
- [x] Implements dynamic content inclusion via `mail-{template}-snippets.ntpl` pattern
- [x] Defines 5 email templates: `register`, `reminder`, `pin`, `account-pin`, `sample`
- [x] Multi-language support (EN, ES, DE, FR) via `locale.json`
- [x] Theme system with customizable colors via `local-data.json`

### Technical
- [x] No routes exposed (empty base route)
- [x] No transport logic (delegated to `core/mail.py`)
- [x] CSP-compliant inline styles with nonce
- [x] Table-based layout for email client compatibility

### Integration
- [x] Compatible with `010-mail-system` provider contract
- [x] Variable resolution hierarchy works: `current_mail` > `local-data` > `site` data

---

*Specification updated per 010-mail-system architecture (2026-05-03)*

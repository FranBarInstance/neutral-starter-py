# Component: http_errors_0yt2sa

HTTP error handler component.

## Overview

This component provides centralized HTTP error handling for the application. It catches exceptions (both HTTP errors and unhandled exceptions) and renders user-friendly error pages with proper status codes and translations.

## Structure

- `manifest.json` - Component identity and security
- `route/routes.py` - Error handler registration
- `schema.json` - Error message translations

## Error Handler

**`@bp.errorhandler(Exception)`**
- Catches all exceptions for the component's blueprint
- Handles two types:
  - **HTTPException**: Uses exception's code, name, and description
  - **Generic Exception**: Returns 500 Internal Server Error

**Error Response:**
- Code: HTTP status code (or 500 for unhandled)
- Name: HTTP error name
- Description: Error details (sanitized in production)
- Rendering: Uses `RequestHandler` with "HTTP_ERROR" type

## Debug Mode Behavior

**Production:** Generic exceptions show "Internal Server Error" without details (prevents information leakage)

**Debug mode:** Could show full exception details (commented out in current code)

## Translations

Provides error message translations in 6 languages:
- EN: Internal Server Error / An internal error occurred in app.
- ES: Error interno del servidor / Se produjo un error interno...
- DE: Interner Serverfehler / Ein interner Fehler ist...
- FR: Erreur interne du serveur / Une erreur interne s'est produite...
- AR: خطأ داخلي في الخادم / حدث خطأ داخلي في التطبيق.
- ZH: 内部服务器错误 / 应用程序中发生内部错误。

## Dependencies

- **None**: Self-contained error handler
- **Used by**: All routes (global error handling)

# _cmp_6000_aichat (disabled)

This component is intentionally disabled.

## Why it is disabled

The chat API was exposed without complete security controls:

- No authentication/authorization in chat endpoints.
- No abuse protection/rate limiting in chat endpoints.

If paid AI providers are enabled, this can allow unauthorized usage and unwanted costs.

## Re-enable

Do not re-enable until the pending security work is implemented and tested.

Minimum requirements before enabling:

- Add authentication/authorization to all API routes.
- Add rate limiting and abuse controls.
- Avoid exposing internal exception details in API responses.
- Add automated tests for auth and throttling behavior.

To re-enable after hardening, rename this folder back to:

- `src/component/cmp_6000_aichat`

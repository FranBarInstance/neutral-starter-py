# Component FToken

This component handles the generation and validation of CSRF tokens (Form Tokens) for the client side. It includes both the backend logic (Python) and the frontend resources (JS/Templates).

## Overview

The `ftoken` mechanism aims to prevent CSRF attacks by generating a unique, time-limited token linked to a specific user session and form action.

## Library (`ftoken_0yt2sa`)

This component exposes a Python library that can be used by other components to securely generate and verify tokens.

### Import
The component automatically registers its internal library path, allowing direct imports:

```python
from ftoken_0yt2sa import ftoken_create, ftoken_check
```

### Functions

#### `ftoken_create(key, fetch_id, form_id, user_token) -> dict`
Generates a new signed token.

*   **key**: A unique identifier or seed for the token.
*   **fetch_id**: Client-side ID for fetching/updating the token.
*   **form_id**: The ID of the form this token belongs to.
*   **user_token**: The user's session token (UTOKEN) to bind the CSRF token to the session.

**Returns**: A dictionary containing `name`, `value`, `expire`, etc.

#### `ftoken_check(field_key_name, data, user_token) -> bool`
Validates a received token against expiration and signature.

*   **field_key_name**: The name of the field in `data` that contains the key/seed.
*   **data**: The dictionary of data submitted (must contain the token fields).
*   **user_token**: The user's session token for verification.

**Returns**: `True` if valid, `False` otherwise.

## Frontend Integration

The component provides templates (NTPL) and a Javascript file (`ftoken.min.js`) to handle token injection in forms automatically.

### Snippets (NTPL)
The component exports snippets via `neutral/snippets.ntpl` (loaded globally via `component-init.ntpl` or component index).

*   `{:snip; ftoken:form-field :}`: Injects the hidden fields for the CSRF token. It intelligently handles AJAX loading or error states.
*   `{:snip; ftoken:form-field-field :}`: The actual input fields.
*   `{:snip; ftoken:form-field-error :}`: Error message if token generation fails.

### Usage in Forms

To implement `ftoken` in a form, you need to:

1.  **Define the key field**: Add an input field that will hold the seed for the token. It must have the classes `ftoken-field-key` and `ftoken-field-value`, and the `data-ftokenid` attribute matching the `ftoken_form_id`.
    ```html
    <input
        type="hidden"
        id="my-field-id"
        name="my_field_name"
        value="my_seed_value"
        class="ftoken-field-key ftoken-field-value"
        data-ftokenid="my-ftoken-id"
        required
    >
    ```

2.  **Generate the token fields**: Use the `ftoken:form-field` snippet.
    ```html
    {:code;
        {:param; ftoken_fetch_id >> my-fetch-id :}
        {:param; ftoken_form_id >> my-ftoken-id :}
        {:snip; ftoken:form-field :}
    :}
    ```

*Note: If the form token is not updated due to an error, the submit button will be automatically disabled by the included Javascript.*

### Routes
The component exposes the following routes (defined in `route/routes.py`):

*   `GET /ftoken/<key>/<fetch_id>/<form_id>`: Endpoint to fetch a new token via AJAX.
*   `GET /ftoken/ftoken.min.js`: Serves the static JS file.

## Configuration

The component relies on the following application configurations (in `app.config`):

*   `Config.FTOKEN_EXPIRES_SECONDS`: Duration in seconds before a token expires.
*   `Config.SECRET_KEY`: keys used for HMAC signing.

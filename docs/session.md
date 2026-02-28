# Session Management

The `Session` class (`src/core/session.py`) provides the core session management for standard users in the Neutral TS Starter Py application. It is entirely database-backed and ensures secure, stateful session handling.

## Overview

The `Session` module is responsible for:
- Creating, retrieving, updating, and securely closing user sessions.
- Generating cryptographically secure session tokens.
- Storing session data and metadata (like user agent and timestamps) directly in the secure database (`DB_SAFE`).
- Managing secure cookies with modern standards (`HttpOnly`, `Secure`, `SameSite=Lax`).

## How it Works

1. **Initialization**: The `Session` class is instantiated with an existing `session_id` (usually retrieved from the user's cookie) and connects to the safe database (`Config.DB_SAFE`).
2. **Retrieval & Auto-renewal (`get`)**:
   - Checks the database to ensure the session is valid, open, and not expired.
   - If the session was last modified more than 15 minutes ago, it automatically updates the `modified` timestamp and extends the expiration time in the database, seamlessly returning an updated cookie.
3. **Creation (`create`)**:
   - Generates a URL-safe random token (`secrets.token_urlsafe`).
   - Inserts a new session record into the database linking the `userId`, the user agent (`ua`), and any additional `session_data` JSON string.
   - Returns a configured dictionary to set the session cookie in the user's browser.
4. **Properties (`get_session_properties`)**:
   - Allows retrieving the specific `properties` JSON object originally saved during the user's login. This is useful to recover context like previous URLs, login methods, or specific flags without querying the main user table.
5. **Closing (`close`)**:
   - Marks the session as `open=0` in the database.
   - Returns a cookie dictionary designed to immediately expire and delete the session cookie on the client side.

## Configuration Parameters

The session behavior is highly dependent on `app.config.Config`:

- `SESSION_KEY`: The name of the cookie (default: `"SESSION"`).
- `SESSION_TOKEN_LENGTH`: Number of bytes for the generated token (default: `32`).
- `SESSION_IDLE_EXPIRES_SECONDS`: How long a session lives before it expires (default: 30 days / `2592000` seconds).
- `SESSION_OPEN`: The database boolean values indicating if a session is active.

## Code Example

```python
from core.session import Session
from flask import request

# Initialize with the cookie from the request
current_token = request.cookies.get("SESSION")
session_manager = Session(current_token)

# Retrieve the validated session ID and the cookie (if it was updated)
valid_session_id, cookie_response = session_manager.get()

if valid_session_id:
    # Read properties
    props = session_manager.get_session_properties()

    # Close session
    deletion_cookie = session_manager.close()
else:
    # Create a new session for a user id
    new_cookie = session_manager.create("user_id_123", "Mozilla/5.0...", {"login_method": "email"})
```

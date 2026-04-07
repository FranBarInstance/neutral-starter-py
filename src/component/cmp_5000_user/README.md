# User Profile Management Component

Component for user profile management.

## UUID

`user_0yt2sa`

## Routes

| Route | Description | Authentication |
|-------|-------------|---------------|
| `/u` | User profile view (read-only) | Required |
| `/u/profile` | Profile edit page | Required |
| `/u/profile/ajax/<ltoken>` | AJAX form for profile editing | Required |

**Security note:** All routes require authentication. The user ID is obtained from the request user context (`USER.id`), never from URL parameters.

## Functionality

### User Profile
- **Username**: Optional public identifier used by the public profile-image route
- **Alias**: User display name
- **Profile image**: Stores the selected image id for the profile avatar
- **Locale**: Preferred language (e.g., es, en, fr)
- **Region**: Geographic region (optional)
- **Properties**: Additional properties in JSON format (optional)

## Structure

```
cmp_5000_user_local/
├── manifest.json              # Component configuration
├── schema.json                # Menus and inheritance configuration
├── README.md                  # This file
├── route/
│   ├── __init__.py           # Blueprint initialization
│   ├── routes.py             # Flask route definitions
│   ├── user_handler.py       # Business logic
│   └── schema.json           # Form validation
├── neutral/route/
│   ├── index-snippets.ntpl   # Auto-loaded snippets
│   ├── form-snippets.ntpl    # Form definitions
│   └── root/
│       ├── data.json         # Metadata for /u
│       ├── content-snippets.ntpl
│       └── profile/
│           ├── data.json
│           ├── content-snippets.ntpl
│           └── ajax/
│               └── content-snippets.ntpl
└── tests/
    └── test_routes.py        # Component tests
```

## Usage

### Access profile
```
GET /u
```
Displays the authenticated user's profile information.

### Edit profile
```
GET /u/profile
```
Page with form to edit profile data.

**Form fields:**
- `username` (optional): Public username with restricted format
- `alias` (required): Display name (2-50 characters)
- `locale` (required): Language code (2-10 characters)
- `region` (optional): Geographic region (max 20 characters)
- `properties` (optional): JSON with additional properties

## Dependencies

- `forms_0yt2sa`: Forms component (includes utilities and snippets)

## Implementation Notes

1. **Security**: All routes use `"/": true` in `routes_auth`, applying to all sub-routes.

2. **AJAX**: Forms use `{:fetch; ... :}` to load and send data via AJAX with the `LTOKEN` token.

3. **Data Loading**: User data is loaded from the database using the `userId` from the request context.

4. **Public Image Cache Invalidation**: When the profile form changes the username, the handler invalidates the cached public profile-image responses for the old and new `username` values. This targets the public image route `<image manifest.route>/p/<username>` through the shared image helper cache invalidation API.

## Testing

```bash
# Run component tests
python -m pytest src/component/cmp_5000_user_local/tests/ -v
```

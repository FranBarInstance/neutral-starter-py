# Component: album_image_0yt2sa

## Executive Summary

Album image management component providing image upload, browse, select, move, and delete functionality organized by albums. Exposes reusable NTPL snippets for embedding image selectors in other components, AJAX JSON endpoints for dynamic image management, and a batch action interface for bulk operations. Integrates with the image delivery component (`image_0yt2sa`) for public variant URL generation.

## Identity

- **UUID**: `album_image_0yt2sa`
- **Base Route**: `/album-image`
- **Version**: `0.0.0`

## Security (SDD Contract)

- **Authentication required**: {
  "/": true
}
- **Allowed roles**: {
  "/": ["*"]
}

**Critical security properties:**
- All routes require authentication
- All operations scoped to current user's `profile_id` from request context
- Batch actions require valid LTOKEN (CSRF protection via `FormRequestHandler`)
- AJAX endpoints require `Requested-With-Ajax` header
- Profile ownership verified before any image operation (delete, move)

## Architecture

### Component Type
**Feature** component with reusable snippets. Provides:
- Image upload, list, delete by album
- Reusable image field snippet for other components
- Batch action form (move, delete multiple images)
- AJAX JSON API for dynamic image management
- Static assets (CSS, JS) for image field functionality
- Menu integration for authenticated users
- Load order dependency: must load after `image_0yt2sa` (requires `current.site.image_link_variant`)

### Directory Structure

```
src/component/cmp_NNNN_album_image/
├── manifest.json                          # Identity and security
├── schema.json                            # Menu entries
├── README.md                              # Operational documentation
├── __init__.py                            # Component init (if needed)
├── route/
│   ├── __init__.py                        # Blueprint initialization
│   ├── routes.py                          # Route definitions (7 handlers)
│   ├── batch_action_handler.py            # Form handler for batch actions
│   └── schema.json                        # Form validation rules
├── neutral/
│   ├── component-init.ntpl              # Snippet inclusion
│   ├── snippets.ntpl                      # Reusable image-field snippet
│   └── route/
│       └── root/
│           ├── data.json                  # Route metadata
│           ├── content-snippets.ntpl      # Batch action UI
│           └── field/batch-action/ajax/
│               └── content-snippets.ntpl  # AJAX form response
└── static/
    ├── album-image.css / .min.css         # Stylesheet
    ├── album-image-field.js / .min.js     # Image field widget
    └── album-image-edit.js / .min.js      # Batch edit functionality
```

### Routes (`route/routes.py`)

| Route | Method | Handler | Auth | Purpose |
|-------|--------|---------|------|---------|
| `/` | GET | `album_image_pages()` | Yes | Root page (batch management UI) |
| `/static/<path>` | GET | `serve_static()` | No | Static assets (rate limited) |
| `/field/list` | GET | `field_list()` | Yes | List images by album (AJAX) |
| `/field/albums` | GET | `field_albums()` | Yes | List album codes (AJAX) |
| `/field/upload` | POST | `field_upload()` | Yes | Upload images (AJAX) |
| `/field/delete` | POST | `field_delete()` | Yes | Delete image (AJAX) |
| `/field/batch-action/ajax/<ltoken>` | GET/POST | `field_batch_action_*()` | Yes | Batch action form |

### Route Handlers

**`field_list()`**
- Query params: `album_code` (default: "gallery"), `limit` (default: 50), `offset` (default: 0)
- Returns JSON: `{"success": true, "items": [...]}`
- Items include `thumbUrl`, `mediumUrl`, `fullUrl` (built from `image_link_variant`)

**`field_albums()`**
- Returns JSON: `{"success": true, "items": ["album1", "album2", ...]}`
- Lists distinct album codes for current profile

**`field_upload()`**
- Accepts multipart/form-data with `images` or `image` file field
- Form field: `album_code` (default: "gallery")
- Returns JSON with uploaded items including variant URLs
- Handles `ValueError` (validation) → HTTP 422, `RuntimeError` → HTTP 500

**`field_delete()`**
- Form field: `image_id`
- Verifies image belongs to current profile before deletion
- Returns JSON: `{"success": true}` or error

**`AlbumImageBatchActionFormHandler` (`batch_action_handler.py`)**
- Extends `FormRequestHandler`
- Handles batch operations: "move" or "delete"
- Form fields: `action`, `target_album`, `confirm`, `album-image-edit-image-id`
- Validates profile ownership for each image in batch
- Move operation: updates `albumCode` in database
- Delete operation: removes images permanently

### Reusable Snippets (`neutral/snippets.ntpl`)

| Snippet | Purpose | Parameters |
|---------|---------|------------|
| `album_image_0yt2sa:image-field-required` | CSS/JS injection | None |
| `album_image_0yt2sa:image-field` | Complete image field widget | `max-images`, `list-limit`, `upload-delay-ms`, `force-album`, `fields-to-fill`, `url-to-fill` |

**Snippet Parameters:**
- `max-images` — Max files per upload (default: 1)
- `list-limit` — Images per page in grid (default: 21)
- `upload-delay-ms` — Delay between uploads (default: 100)
- `force-album` — Fixed album code (disables album input)
- `fields-to-fill` — Selector for field to populate with selected image IDs
- `url-to-fill` — Selector for field to populate with image URLs

### Form Validation (`route/schema.json`)

**`album_image_batch_action` form:**
| Field | Required | Purpose |
|-------|----------|---------|
| `action` | Yes | "move" or "delete" |
| `target_album` | No | Destination album (required for move) |
| `confirm` | Yes | Checkbox confirmation |
| `album-image-edit-image-id` | Yes | Comma-separated image IDs |

### Dependencies

- **Depends on**: Core `Image` (upload, list, delete, move), core `FormRequestHandler`, `image_0yt2sa` (for `current.site.image_link_variant`)
- **Used by**: Other components embedding image field snippet (e.g., user profile)

### Load Order Requirement

Must load **after** `image_0yt2sa` because it relies on `current.site.image_link_variant` being set in schema data.

## Data and Models

### Schema Data Publication (`schema.json`)

Menu integration for authenticated users:

**Session menu:**
| Entry | Text | Link | Icon |
|-------|------|------|------|
| album-image | Album Images | `[:;data->album_image_0yt2sa->manifest->route:]` | `x-icon-images` |

**Drawer menu:**
| Entry | Name | Tabs | Icon |
|-------|------|------|------|
| user | User | user | `x-icon-user` |

### Image URL Serialization

Routes serialize image items with public URLs:

```python
data["thumbUrl"] = f"{base}/{image_id}/thumb"
data["mediumUrl"] = f"{base}/{image_id}/medium"
data["fullUrl"] = f"{base}/{image_id}/full"
```

Where `base` is retrieved from `current.site.image_link_variant`.

## Technical Rationale

- **Reusable snippet pattern**: Other components can embed image selection without implementing upload logic
- **AJAX-first API**: All operations return JSON for dynamic frontend updates
- **Album organization**: Flexible `album_code` allows same component for profiles, galleries, documents
- **Batch operations**: Bulk move/delete via form with confirmation checkbox
- **Profile isolation**: All database queries scoped to `profile_id` from context
- **URL serialization**: Frontend receives complete URLs without hardcoding routes
- **CSP compliance**: Inline scripts use `{:;CSP_NONCE:}`

## Known Limitations

- Requires `image_0yt2sa` to be loaded first (for `image_link_variant`)
- Batch action form requires JavaScript for album population
- No built-in image editing (crop, rotate) — upload only

---

## Acceptance Criteria (SDD)

### Functional
- [x] `/` renders batch management page with image grid
- [x] `/field/list` returns paginated image list by album (AJAX)
- [x] `/field/albums` returns album codes for current profile (AJAX)
- [x] `/field/upload` handles single/multiple file upload (AJAX)
- [x] `/field/delete` removes image with profile ownership check (AJAX)
- [x] Batch action form supports move and delete operations
- [x] Image items include `thumbUrl`, `mediumUrl`, `fullUrl`

### Technical
- [x] All routes require authentication (`routes_auth: {"/": true}`)
- [x] All operations scoped to current `profile_id`
- [x] AJAX endpoints require `Requested-With-Ajax` header
- [x] Batch form uses `FormRequestHandler` with LTOKEN validation
- [x] Static assets served with rate limiting
- [x] CSP nonces on all inline scripts

### Reusable Snippets
- [x] `album_image_0yt2sa:image-field-required` loads CSS/JS
- [x] `album_image_0yt2sa:image-field` provides complete widget
- [x] Snippet accepts parameters: `max-images`, `list-limit`, `force-album`, etc.

### Integration
- [x] Session menu entry for authenticated users
- [x] Drawer menu entry under "user" tab
- [x] Depends on `image_0yt2sa` for `image_link_variant`
- [x] URL serialization uses `current.site.image_link_variant`

### Security
- [x] Profile ownership verified before delete/move
- [x] Batch actions require confirmation checkbox
- [x] LTOKEN validation on batch form
- [x] All image queries filtered by `profile_id`

---

*Last updated: 2026-05-04*

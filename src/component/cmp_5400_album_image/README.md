# Album Image Component

Upload, list, select, move, and delete images organized by albums.

## Overview

Provides AJAX endpoints for image management and reusable NTPL snippets for embedding image selectors in other components. Includes batch action interface for bulk operations.

## Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | Yes | Root page (batch management UI) |
| `/static/<path>` | GET | No | Static assets |
| `/field/list` | GET | Yes | List images by album (AJAX) |
| `/field/albums` | GET | Yes | List album codes (AJAX) |
| `/field/upload` | POST | Yes | Upload images (AJAX) |
| `/field/delete` | POST | Yes | Delete image (AJAX) |
| `/field/batch-action/ajax/<ltoken>` | GET/POST | Yes | Batch action form |

## Structure

```
├── manifest.json              # UUID: album_image_0yt2sa, route: /album-image
├── schema.json                # Menu entries
├── route/
│   ├── __init__.py            # Blueprint init
│   ├── routes.py              # 7 route handlers
│   ├── batch_action_handler.py # Form handler for batch ops
│   └── schema.json            # Form validation
├── neutral/
│   ├── component-init.ntpl    # Snippet inclusion
│   ├── snippets.ntpl          # Reusable image-field
│   └── route/root/
│       ├── data.json          # Route metadata
│       ├── content-snippets.ntpl # Batch UI
│       └── field/batch-action/ajax/
│           └── content-snippets.ntpl
└── static/
    ├── album-image.css/.js    # Field widget styles/scripts
    └── album-image-edit.js    # Batch edit functionality
```

## Reusable Snippets

| Snippet | Purpose |
|---------|---------|
| `album_image_0yt2sa:image-field-required` | Load CSS/JS assets |
| `album_image_0yt2sa:image-field` | Complete image field widget |

**Snippet parameters:** `max-images`, `list-limit`, `upload-delay-ms`, `force-album`, `fields-to-fill`, `url-to-fill`

## AJAX Endpoints

All require `Requested-With-Ajax` header and return JSON:

- `GET /field/list?album_code=gallery&limit=50&offset=0` — Returns images with `thumbUrl`, `mediumUrl`, `fullUrl`
- `GET /field/albums` — Returns album codes for current profile
- `POST /field/upload` — Upload files (field: `images` or `image`)
- `POST /field/delete` — Delete image (field: `image_id`)

## Batch Actions

Form-based batch operations (move/delete) via `/field/batch-action/ajax/<ltoken>`:
- Fields: `action`, `target_album`, `confirm`, `album-image-edit-image-id`
- Ownership verified for each image before operation

## Dependencies

- Core `Image` class (upload, list, delete, move)
- Core `FormRequestHandler`
- **Must load after** `image_0yt2sa` (requires `current.site.image_link_variant`)

## Menu Integration

- **Session menu**: "Album Images" entry with `x-icon-images`
- **Drawer menu**: "User" tab entry with `x-icon-user`

## Security

- All routes require authentication
- All operations scoped to current `profile_id`
- Profile ownership verified before delete/move
- LTOKEN validation on batch form
- CSP nonces on inline scripts

# 005 - Image and File Management System

## Executive Summary

This specification defines the image storage, processing, and delivery system
for Neutral Starter Py. The system is built around immutable image records,
automatically generated WebP variants (`thumb`, `medium`, `full`), logical
album grouping, and a soft-delete-before-physical-delete lifecycle.

Images are stored in a dedicated `DB_IMAGE` database, separate from user data,
with public delivery handled through the `cmp_5300_image` component.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/000-core-system/spec.md` - core architecture and data model.
- `specs/001-component-standard/spec.md` - component structure.
- `src/core/image.py` - image helper implementation.
- `src/model/image.json` - image model SQL definitions.
- `docs/image-database.md` - technical documentation for the image subsystem.
- `src/component/cmp_5300_image/` - public image delivery component.

---

## 1. Goals

### 1.1 What this system must achieve

- **Immutable storage:** Once inserted, image records are not modified.
  Changes produce new records.
- **Automatic variants:** Generate square thumbnails plus proportional medium
  and full WebP variants.
- **Album management:** Organize images logically by album without a separate
  relational album entity.
- **Staged deletion:** Perform soft deletion first and defer physical deletion
  to a later cleanup task.
- **Visibility control:** Apply clear public-vs-admin visibility rules based on
  disabled states.

### 1.2 Non-goals

- It does not manage non-image file storage such as PDFs or videos.
- It does not implement its own CDN.
- It does not perform image editing beyond resizing and variant generation.

---

## 2. Technical Contracts

### 2.1 Data architecture

#### Main tables

| Table | Purpose | Mutability |
|-------|---------|------------|
| `image` | Immutable image assets and generated variants | Immutable |
| `image_disabled` | Visibility and moderation states | Mutable |

#### `image` structure

| Field | Type | Description |
|-------|------|-------------|
| `imageId` | VARCHAR(64) | Asset UUID (PK) |
| `profileId` | VARCHAR(64) | Logical owner reference |
| `albumCode` | VARCHAR(64) | Album code (`gallery`, `profile`, or custom) |
| `thumbImg/mediumImg/fullImg` | BLOB | WebP binaries for each variant |
| `thumbWidth/Height` | INT | Real thumbnail dimensions |
| `mediumWidth/Height` | INT | Real medium dimensions |
| `fullWidth/Height` | INT | Real full dimensions |
| `thumbBytes/mediumBytes/fullBytes` | INT | Size in bytes |
| `created` | INT(11) | Creation timestamp |

#### `image_disabled` structure

| Field | Type | Description |
|-------|------|-------------|
| `reason` | INT | Reason code (`deleted`, `moderated`, `spam`, and so on) |
| `imageId` | VARCHAR(64) | FK-like reference to `image.imageId` |
| `description` | VARCHAR(256) | Optional explanation |
| `modified` | BIGINT | Last change |
| `created` | BIGINT | State creation time |

**Composite PK:** `(reason, imageId)` so a single image may hold multiple
disabled reasons.

### 2.2 Image processing

#### Runtime variant configuration

```env
IMAGE_THUMB_SIZE=100
IMAGE_MEDIUM_WIDTH=420
IMAGE_FULL_WIDTH=1920
IMAGE_WEBP_QUALITY=85
IMAGE_MAX_PIXELS=25000000
IMAGE_MAX_FILE_BYTES=10485760
IMAGE_MAX_UPLOAD_BYTES=52428800
IMAGE_MAX_PER_ALBUM=50
IMAGE_MAX_ALBUMS=10
IMAGE_ALLOWED_MIME="image/jpeg,image/png,image/gif,image/webp"
```

#### Variant generation rules

| Variant | Rule | Aspect ratio |
|---------|------|--------------|
| `thumb` | Crop-fit to configured square size | 1:1 |
| `medium` | Proportional resize to max width | Original |
| `full` | Proportional resize only if wider than max width | Original |

### 2.3 Albums and codes

#### Default album codes

| Code | Usage |
|------|-------|
| `gallery` | Default album for user images |
| `profile` | User profile/avatar image |

#### Album normalization

- convert to lowercase;
- replace spaces with hyphens (`-`);
- validate against `^[a-z0-9][a-z0-9_-]{0,63}$`.

### 2.4 Visibility and states

#### Deletion lifecycle

```text
[Active] --(delete)--> [Soft Deleted] --(cleanup)--> [Physically Deleted]
   ^                                               |
   +--------------------(restore)------------------+
```

#### Public visibility rules

An image is publicly visible only if:

1. it has no rows in `image_disabled`;
2. its owner profile is not disabled in `profile_disabled`;
3. its owner user is not disabled in `user_disabled`.

#### Disabled reason codes

| Code | Meaning | Recoverable |
|------|---------|-------------|
| 1 | `deleted` | Yes |
| 2 | `moderated` | Yes |
| 3 | `spam` | Yes |

### 2.5 `Image` helper API

| Method | Purpose |
|--------|---------|
| `upload_images(files, profile_id, album_code)` | Validate, process, and store images |
| `list_by_profile(profile_id, album_code)` | List visible images with metadata and URLs |
| `list_album_codes(profile_id)` | Return existing albums plus defaults |
| `get_meta(image_id)` | Metadata for a visible image |
| `get_variant(image_id, variant)` | Binary data for a visible variant |
| `get_public_variant(image_id, variant)` | Variant only if owner is publicly visible |
| `delete_image(image_id, reason, description)` | Soft delete |
| `delete_by_profile(profile_id, reason)` | Bulk soft delete |
| `restore_image(image_id)` | Restore from trash |
| `set_image_disabled(image_id, reason, description)` | Add disabled reason |
| `delete_image_disabled(image_id, reason)` | Remove disabled reason |
| `admin_list_images(...)` | Administrative listing |
| `invalidate_public_username_cache(username)` | Invalidate profile-image cache |
| `invalidate_all_public_profile_images_cache(profile_id)` | Invalidate all public profile images cache |

---

## 3. Behavior

### 3.1 Successful upload flow

1. validate MIME type, individual size, and total size;
2. validate album limits and custom album count;
3. process with PIL, apply EXIF transpose, normalize mode, and generate
   variants;
4. validate against the configured pixel limit;
5. insert into `image` with generated UUID, WebP binaries, and dimensions;
6. return metadata including public URLs for variants.

### 3.2 Deletion flow

1. mark the image logically by inserting or updating `image_disabled` with
   `reason=deleted`;
2. hide it from public queries while keeping it recoverable;
3. restore by removing the `deleted` row;
4. perform physical deletion later through scheduled cleanup.

### 3.3 Error handling

| Error | Behavior | Code |
|-------|----------|------|
| Invalid MIME type | `ValueError` with rejected type | `INVALID_MIME` |
| File too large | `ValueError` with actual size and limit | `FILE_TOO_LARGE` |
| Excessive dimensions | `ValueError` with pixel count | `DIMENSIONS_EXCEEDED` |
| Album full | `ValueError` with configured limit | `ALBUM_FULL` |
| Corrupt image | `ValueError` with PIL error message | `INVALID_IMAGE` |

---

## 4. Security

### 4.1 Security controls

- [x] input validation through MIME whitelists and configurable size limits;
- [x] rate limiting on upload routes;
- [x] authentication required for uploads;
- [x] authorization based on image ownership;
- [x] no direct filename trust, storage uses generated UUIDs;
- [x] DoS prevention through limits on size, pixels, and per-album count.

### 4.2 Risks and mitigations

| Risk | Mitigation | Level |
|------|------------|-------|
| Malicious uploads | MIME whitelist plus PIL validation | High |
| DoS via oversized images | Size, pixel, and quantity limits | High |
| Information leakage | Visibility checks across image/profile/user states | Medium |
| Unlimited storage growth | Album limits plus configurable retention | Medium |

---

## 5. Implementation and Deployment

### 5.1 Dependencies

- `PIL/Pillow` for image processing
- `SQLAlchemy` for image database access
- `cmp_5300_image` for public delivery

### 5.2 Required configuration

```python
DB_IMAGE = os.getenv("DB_IMAGE", DB_PWA)
DB_IMAGE_TYPE = os.getenv("DB_IMAGE_TYPE", DB_PWA_TYPE)

IMAGE_THUMB_SIZE = int(os.getenv("IMAGE_THUMB_SIZE", "100"))
IMAGE_MEDIUM_WIDTH = int(os.getenv("IMAGE_MEDIUM_WIDTH", "420"))
IMAGE_FULL_WIDTH = int(os.getenv("IMAGE_FULL_WIDTH", "1920"))
IMAGE_WEBP_QUALITY = int(os.getenv("IMAGE_WEBP_QUALITY", "85"))
IMAGE_MAX_PIXELS = int(os.getenv("IMAGE_MAX_PIXELS", "25000000"))
IMAGE_MAX_FILE_BYTES = int(os.getenv("IMAGE_MAX_FILE_BYTES", "10485760"))
IMAGE_MAX_UPLOAD_BYTES = int(os.getenv("IMAGE_MAX_UPLOAD_BYTES", "52428800"))
IMAGE_MAX_PER_ALBUM = int(os.getenv("IMAGE_MAX_PER_ALBUM", "50"))
IMAGE_MAX_ALBUMS = int(os.getenv("IMAGE_MAX_ALBUMS", "10"))
IMAGE_ALLOWED_MIME = os.getenv(
    "IMAGE_ALLOWED_MIME",
    "image/jpeg,image/png,image/gif,image/webp"
)
```

### 5.3 Public delivery URLs

| Route | Description |
|-------|-------------|
| `<manifest.route>/p/<username>` | Public profile image by username |
| `<manifest.route>/v/<image_id>/<variant>` | Specific variant by image ID |

The actual URLs must be read from `current.site.image_link*` schema data and
must never be hardcoded in templates.

---

## 6. Testing

### 6.1 Strategy

| Type | Coverage |
|------|----------|
| Unit | `Image._process_image()`, `_validate_file()`, `_normalize_album_code()` |
| Integration | `upload_images()`, `list_by_profile()`, delete/restore flows |
| E2E | Real upload, display, and delete through the UI |

### 6.2 Required test cases

- [ ] a valid upload generates all three WebP variants;
- [ ] images that exceed limits are rejected with the correct error;
- [ ] soft deletion hides the image from public listings;
- [ ] restoring from trash makes the image visible again;
- [ ] a user cannot access another user's images without authorization;
- [ ] cache invalidation works when profile visibility changes.

---

## 7. Acceptance Criteria

- [x] uploads generate WebP variants automatically;
- [x] size, dimension, and quantity limits are enforced;
- [x] soft deletion behaves like a recoverable trash state;
- [x] public visibility respects image, profile, and user disabled states;
- [x] public delivery uses configurable schema URLs;
- [x] public image caches are invalidated correctly;
- [x] all relevant operations use rate limiting.

---

## 8. Impact and Dependencies

### 8.1 Components that depend on this system

| Component | Usage |
|-----------|-------|
| `cmp_5000_user` | Profile image management |
| `cmp_5100_sign` | Avatar during registration |
| `cmp_5300_image` | Public variant delivery |

### 8.2 Data migrations

- not applicable for new installations;
- migrating from systems without variants requires bulk regeneration.

---

## 9. Decisions and Risks

### 9.1 Architectural decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| Image immutability | Better cacheability and traceability | Storage grows monotonically until cleanup |
| WebP as the only format | Smaller size with acceptable quality | Very old browsers are unsupported |
| No DB-level FK from profile to image | Better cross-engine portability | Referential integrity stays in application logic |

### 9.2 Technical debt

- physical cleanup task is still pending implementation;
- support for additional formats is deferred.

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **Variant** | A processed version of an image (`thumb`, `medium`, `full`) |
| **Album** | Logical grouping by code, not a relational table |
| **Soft delete** | Marking an image in `image_disabled` without removing binaries |
| **Trash** | Recoverable state for soft-deleted images |

# Image Storage And Delivery Reference

This document describes the image subsystem built on top of [`src/model/image.json`](../src/model/image.json), [`src/core/image.py`](../src/core/image.py), and the public delivery component in [`src/component/cmp_5300_image/README.md`](../src/component/cmp_5300_image/README.md).

It started as a database-model note, but it now documents the broader contract that the rest of the application relies on.

## Scope

This document covers:

- database schema and queries
- image variant generation
- album semantics
- disabled and deleted image workflow
- public visibility rules
- admin visibility rules
- future physical cleanup expectations

## Overview

Images are stored in the `image` table as generated WebP variants:

- `thumbImg`
- `mediumImg`
- `fullImg`

The subsystem also uses a second table, `image_disabled`, to track logical image state such as:

- `deleted`
- `moderated`
- `spam`

The general rule is:

- `image` stores the immutable asset payload
- `image_disabled` stores mutable state about whether that image should be visible or blocked

## Design Principles

### Immutable image records

Images are immutable by design. The `image` table does not include a `modified` column.

If the content of an image changes, the application should create a new `imageId` and keep caches tied to the old immutable asset id.

### Logical relationship to profiles

`profileId` is a logical reference to the owning profile, but it is not enforced as a foreign key to the profile table.

This is intentional:

- profile data and image data may live in different databases
- cross-database foreign keys are not portable across all supported engines
- deletion and referential cleanup must therefore be handled in application logic

Important distinction:

- there is no database-level foreign key from `image.profileId` to the profile table
- there is a local foreign key from `image_disabled.imageId` to `image.imageId`

### Logical delete before physical delete

The subsystem is designed around logical deletion first.

When a user or admin deletes an image, the first step is not physical removal from `image`. Instead, the image is marked in `image_disabled` with reason `deleted`.

That gives the system a trash/paper-bin stage:

- deleted images stop being visible to normal users
- deleted images can still exist in storage for a retention period
- a future recovery flow can restore them by removing the `deleted` reason

Physical deletion is expected to happen later in a separate cleanup task.

## Runtime Image Processing

Target sizes are controlled by runtime configuration, not by database schema.

Typical settings:

```env
IMAGE_THUMB_SIZE=100
IMAGE_MEDIUM_WIDTH=420
IMAGE_FULL_WIDTH=1920
```

Generation rules:

- `thumb` is square and generated with crop-fit semantics
- `medium` is resized proportionally to a configured max width
- `full` is resized proportionally only when wider than the configured max width

The database stores:

- the generated binary for each variant
- the actual width and height of each variant
- the byte size of each variant

## Stored Tables

### `image`

The immutable image asset table.

| Field | Portable type | Description |
| --- | --- | --- |
| `imageId` | `VARCHAR(64)` | Primary key for the immutable asset. |
| `profileId` | `VARCHAR(64)` | Logical owner profile id. No FK to profile storage. |
| `albumCode` | `VARCHAR(64)` | Album/group code inside the profile scope. |
| `thumbImg` | `BLOB` | Square thumbnail WebP binary. |
| `mediumImg` | `BLOB` | Medium WebP binary. |
| `fullImg` | `BLOB` | Full WebP binary. |
| `thumbWidth` | `INT` | Thumbnail width. |
| `thumbHeight` | `INT` | Thumbnail height. |
| `mediumWidth` | `INT` | Medium width. |
| `mediumHeight` | `INT` | Medium height. |
| `fullWidth` | `INT` | Full width. |
| `fullHeight` | `INT` | Full height. |
| `thumbBytes` | `INT` | Thumbnail byte size. |
| `mediumBytes` | `INT` | Medium byte size. |
| `fullBytes` | `INT` | Full byte size. |
| `created` | `INT(11)` | Creation timestamp. |

### `image_disabled`

Mutable state table for hidden, moderated, spam, or deleted images.

| Field | Portable type | Description |
| --- | --- | --- |
| `reason` | `INT` | Disabled reason code from configuration. |
| `imageId` | `VARCHAR(64)` | FK to `image.imageId`. |
| `description` | `VARCHAR(256)` | Optional explanation. |
| `modified` | `BIGINT` | Last change timestamp. |
| `created` | `BIGINT` | First creation timestamp for that reason. |

Primary key:

- `(reason, imageId)`

This means one image can accumulate multiple state flags over time.

## Engine Notes

| Aspect | SQLite | MySQL / MariaDB | PostgreSQL |
| --- | --- | --- | --- |
| Image binary type | `BLOB` | `LONGBLOB` | `BYTEA` |
| Integer dimensions | `INT` | `INT UNSIGNED` | `INT` |
| Created timestamp | `INT(11)` or equivalent | `INT(11)` | `INT` |
| Profile FK | Not used | Not used | Not used |
| `image_disabled.imageId -> image.imageId` | Local FK | Local FK | Local FK |

## Indexes

### `image`

| Index | Column | Purpose |
| --- | --- | --- |
| `idx_image_profileId` | `profileId` | List images for one profile. |
| `idx_image_profile_album` | `profileId, albumCode` | List images by profile and album. |
| `idx_image_created` | `created` | Order recent uploads efficiently. |

### `image_disabled`

| Index | Column | Purpose |
| --- | --- | --- |
| `idx_image_disabled_imageId` | `imageId` | Resolve state for one image efficiently. |
| `idx_image_disabled_modified` | `modified` | Support state-based reviews and future cleanup tasks. |

## Album Semantics

`albumCode` is application data, not a separate relational entity.

Current rules in application code:

- normalized to lowercase
- spaces are converted to `-`
- must match a restricted pattern
- current defaults are `gallery` and `profile`

The helper currently treats album codes as part of the application contract, not user-arbitrary raw text.

The subsystem also enforces runtime limits such as:

- maximum images per album
- maximum custom albums per profile

## Visibility Rules

### Public and user-facing visibility

Any query or endpoint that exposes images to end users must exclude images that appear in `image_disabled`, regardless of reason.

That includes reasons such as:

- `deleted`
- `moderated`
- `spam`
- any future hidden state

Practical rule:

- user-facing `SELECT` operations must treat any row in `image_disabled` as not publicly visible

This is why the public lookup queries in the model use `NOT EXISTS (...)` against `image_disabled`.

Public delivery now applies one more rule on top of that:

- an image is not publicly visible if its owning profile is not publicly visible

In current code that means public delivery must also fail when either of these is true:

- the owner profile has any row in `profile_disabled`
- the owner user has any row in `user_disabled`

So the effective public rule is:

- image must not be disabled in `image_disabled`
- owner profile must not be disabled in `profile_disabled`
- owner user must not be disabled in `user_disabled`

The username-based profile image route and the image-variant route both follow that stricter public visibility rule.

### Admin visibility

Admin views are different:

- admin list queries may include disabled images
- admin logic can inspect `image_disabled`
- current admin list behavior hides images marked `deleted` from the active moderation list
- exact moderation flows can still work with disabled-state information

This is an operational choice, not a public-visibility rule.

## Delete Lifecycle

### 1. Active image

The image exists in `image` and has no row in `image_disabled`.

### 2. Logically deleted

The image still exists in `image`, but a row exists in `image_disabled` with reason `deleted`.

Expected behavior:

- hidden from public queries
- hidden from normal user lists
- recoverable by removing the `deleted` reason

This stage is the intended trash/paper-bin behavior.

### 3. Physically deleted

The image row is eventually removed from `image` by a separate cleanup task.

This cleanup task is not implemented yet, but it should be documented as the intended design:

- inspect `image_disabled`
- find images marked with reason `deleted`
- keep them for a configured retention period
- physically delete rows older than the retention threshold

Because `image_disabled.imageId` has a local FK to `image.imageId` with cascade, removing the `image` row will also remove matching rows in `image_disabled`.

## Future Cleanup Task

Planned, not implemented yet.

Suggested behavior:

1. select `imageId` rows from `image_disabled` where reason is `deleted`
2. compare `created` or `modified` against a retention threshold
3. physically delete from `image`
4. let the local cascade clean corresponding `image_disabled` rows

This gives the system:

- soft delete first
- recoverability window
- later permanent cleanup

## Query Reference

### Base schema

| Operation | Purpose |
| --- | --- |
| `setup-base` | Creates `image`, `image_disabled`, and related indexes. |

### Public and user-facing reads

| Operation | Purpose |
| --- | --- |
| `get-by-imageid` | Full row lookup, excluding disabled images. |
| `get-thumb-by-imageid` | Returns `thumbImg`, excluding disabled images. |
| `get-medium-by-imageid` | Returns `mediumImg`, excluding disabled images. |
| `get-full-by-imageid` | Returns `fullImg`, excluding disabled images. |
| `get-meta-by-imageid` | Metadata only, excluding disabled images. |
| `list-by-profileid` | Visible images for one profile, ordered by `created DESC`. |
| `list-by-profileid-albumcode` | Visible images for one profile and album. |
| `list-distinct-albumcodes-by-profileid` | Distinct visible albums for one profile. |
| `count-by-profileid-albumcode` | Count visible images in one album. |

### Internal and maintenance reads

| Operation | Purpose |
| --- | --- |
| `list-by-profileid-all` | Lists all profile images, including disabled ones. |
| `admin-get-image-disabled-by-imageid` | Returns all disabled rows for one image. |
| `admin-get-image-disabled-by-profileid` | Returns disabled rows for a profile's images. |
| `admin-list-images-created` | Admin list ordered by upload date. |
| `admin-list-images-disabled-created-date` | Admin list ordered by disabled created date. |
| `admin-list-images-disabled-modified-date` | Admin list ordered by disabled modified date. |

### Write operations

| Operation | Purpose |
| --- | --- |
| `insert` | Inserts a new immutable image record. |
| `update-album` | Moves an image to another album code. |
| `upsert-image-disabled` | Adds or updates one disabled reason row. |
| `delete-image-disabled` | Removes one disabled reason row. |
| `delete` | Physically deletes one image row. |
| `delete-by-profileid` | Physically deletes all image rows for one profile. |

## Helper Responsibilities

The Python helper in [`src/core/image.py`](../src/core/image.py) adds higher-level rules on top of raw queries.

Important helpers include:

- `upload_images()`
  validates upload MIME, file sizes, album limits, and generates variants
- `list_by_profile()`
  returns visible image metadata and public variant URLs when configured
- `list_album_codes()`
  returns known album codes plus defaults
- `get_meta()`
  returns visible metadata only
- `get_variant()`
  returns a visible stored variant
- `get_public_variant()`
  returns a publicly visible stored variant only when the owner profile is publicly visible
- `delete_image()`
  logical delete using `image_disabled`
- `delete_by_profile()`
  logical delete of all images belonging to a profile
- `admin_list_images()`
  admin-oriented image listing with disabled-state inspection
- `set_image_disabled()`
  sets moderated/spam/deleted state
- `delete_image_disabled()`
  removes one disabled reason
- `restore_image()`
  restores logically deleted images by clearing deleted reasons
- `invalidate_public_username_cache()`
  invalidates one cached public profile-image response for `/p/<username>`
- `invalidate_all_public_profile_images_cache()`
  invalidates all cached public image responses for one profile, including `/p/<username>` and `/v/<image_id>/<variant>`

## Public Delivery Contract

The delivery component publishes two practical route families:

- profile image route:
  `<manifest.route>/p/<username>`
- image variant route:
  `<manifest.route>/v/<image_id>/<variant>`

Other components should not hardcode those routes. They should use schema data:

- `current.site.image_link`
- `current.site.image_link_profile`
- `current.site.image_link_variant`

Current public delivery behavior is:

- `<manifest.route>/p/<username>` resolves only when that username belongs to a public profile
- `<manifest.route>/v/<image_id>/<variant>` resolves only when that image is visible and its owner profile is public
- when the owner user or profile is disabled, public delivery must stop even if the image row itself is still active

## Cache Invalidation

Public image delivery uses route-level response caching.

Because image ids are immutable but profile visibility and usernames can change, public cache invalidation is handled in application logic.

Current invalidation helpers are:

- `invalidate_public_username_cache()`
- `invalidate_all_public_profile_images_cache()`

Current expected usage:

- profile updates that change username should invalidate `/p/<old-username>` and `/p/<new-username>`
- user or profile disable/enable actions should invalidate all public cached images for the affected profile
- deleting a user should invalidate all public cached images for all affected profiles before or together with the delete flow

This keeps cache behavior aligned with the public visibility rules described above.

This document does not replace the delivery component documentation, but the storage model and those public routes are part of the same subsystem and should stay aligned.

## Operational Rules Summary

- image binaries are immutable once inserted
- mutable visibility state lives in `image_disabled`
- there is no FK from images to profiles
- there is a local FK from `image_disabled` to `image`
- public queries must exclude any image that has any disabled row
- public delivery must also exclude images whose owner user or profile is disabled
- delete is logical first, physical later
- physical cleanup should be a separate scheduled task

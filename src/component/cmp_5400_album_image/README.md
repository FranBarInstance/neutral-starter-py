# Album Image Component (`album_image_0yt2sa`)

Reusable component for uploading, listing, selecting, moving, and deleting images from user albums.

## What It Does

- Exposes AJAX endpoints for album image management.
- Provides the reusable Neutral snippet `{:snip; album_image_0yt2sa:image-field :}` for use in other components.
- Lets authenticated users upload images to albums and select existing ones.
- Returns image items with public variant URLs (`thumbUrl`, `mediumUrl`, `fullUrl`) for frontend use.
- Includes its own root page for batch actions such as move and delete.

## Reusable Snippets

This component exposes reusable Neutral snippets from `/neutral/snippets.ntpl`.

Main reusable snippet:

- `{:snip; album_image_0yt2sa:image-field :}`

That snippet is designed to be embedded in other components, for example profile editing flows, custom forms, or image-selection interfaces.

Required assets are loaded through:

- `{:snip; album_image_0yt2sa:image-field-required :}`

## Routes

- `<manifest.route>` is the route defined in `manifest.json`.
- `GET <manifest.route>/`
  - Renders the component root page through `RequestHandler`.
  - The root page provides batch management UI for selected images.
- `GET <manifest.route>/field/list`
  - Lists images for the current profile and one album.
  - Requires header `Requested-With-Ajax`.
- `GET <manifest.route>/field/albums`
  - Lists album codes for the current profile.
  - Requires header `Requested-With-Ajax`.
- `POST <manifest.route>/field/upload`
  - Uploads one or many images for the current profile.
  - Requires header `Requested-With-Ajax`.
- `POST <manifest.route>/field/delete`
  - Deletes one image for the current profile.
  - Requires header `Requested-With-Ajax`.
- `GET <manifest.route>/field/batch-action/ajax/<ltoken>`
  - Renders the batch action form used by the root page.
- `POST <manifest.route>/field/batch-action/ajax/<ltoken>`
  - Applies the batch action form submission for move or delete.

## Dependency on the Image Delivery Component

This component does not decide the public image variant base URL by itself.

Public variant URLs are built from the runtime value:

- `current.site.image_link_variant`

That value must be defined by the component that serves the images, currently the image delivery component (`image_0yt2sa`).

## Load Order Requirement

Because this component depends on `current.site.image_link_variant`, the image delivery component must be loaded first so that value is already present in schema data.

In practice:

- the component that serves images must set `current.site.image_link_variant`
- this component must load after that component

## Optional Integration

This component can coexist with other UI utilities that consume the image URLs it provides.

For example:

- a zoom/lightbox utility may use `thumbUrl` and `fullUrl`
- another component may use the snippet only for image selection without using the root page

Those integrations are external to this component and are not required for its core upload/list/select behavior.

## Key Files

- `/manifest.json`
- `/schema.json`
- `/route/routes.py`
- `/route/batch_action_handler.py`
- `/neutral/snippets.ntpl`
- `/neutral/route/root/content-snippets.ntpl`
- `/static/album-image-field.js`
- `/static/album-image-edit.js`

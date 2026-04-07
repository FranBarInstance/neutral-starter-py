# Universal Image Zoom Component (`img_zoom_0yt2sa`)

Generic utility component that opens an image in a full-screen overlay when the user clicks an element marked as zoomable.

## What It Does

- Loads a reusable CSS and JavaScript pair globally through `neutral/component-init.ntpl`.
- Uses delegated click handling, so it also works with content inserted later through AJAX or Neutral fetch flows.
- Creates a lightweight overlay on demand instead of modifying the original DOM node.
- Supports thumbnails that open a higher-resolution image through `data-zoom-src`.
- Locks body scrolling while the zoom overlay is visible.

## Integration

This component is designed as a utility layer.

It does not render its own page UI. Instead, it provides app-wide behavior after its assets are loaded.

The assets are injected through:

- `/neutral/component-init.ntpl`

That file includes:

- `/img-zoom.css`
- `/img-zoom.js`

## How It Works

- Any click on an element matching `.img-zoomable` is intercepted by the component script.
- If the element has `data-zoom-src`, that URL is used for the overlay image.
- Otherwise, if the clicked element is an `<img>`, its `src` is used.
- The component creates and reuses:
  - one backdrop element: `.img-zoom-backdrop`
  - one overlay image element: `.img-zoom-overlay-img`
- Clicking outside the trigger closes the current zoom overlay.

## Usage

### Basic Image Usage

For normal images, add the `img-zoomable` class.

```html
<img src="/path/to/thumb.jpg" class="img-zoomable">
```

### Thumbnail Plus Full Image

If you have a thumbnail and a larger public variant, use `data-zoom-src`.

```html
<img
    src="{:;current->site->image_link_variant:}/123/thumb"
    class="img-zoomable"
    data-zoom-src="{:;current->site->image_link_variant:}/123/full"
>
```

### Non-Image Trigger

For buttons, links, or other elements, provide `data-zoom-src`.

```html
<button class="img-zoomable btn btn-link" data-zoom-src="{:;current->site->image_link_variant:}/123/full">
    View large photo
</button>
```

## Typical Use Cases

- Enlarging gallery thumbnails.
- Opening full-size album images from selection grids.
- Reusing the same zoom behavior in profile, album, or content components without duplicating modal logic.

## Limits

- The component depends on click interaction.
- It does not manage captions, galleries, image preloading, or navigation between multiple images.
- It does not fetch image metadata; it only displays the URL provided by the clicked element.

## Routes

- `<manifest.route>` is defined in `manifest.json`.
- `GET <manifest.route>/img-zoom.css`
  - Serves the zoom stylesheet.
- `GET <manifest.route>/img-zoom.js`
  - Serves the zoom script.

## Key Files

- `/manifest.json`
- `/schema.json`
- `/neutral/component-init.ntpl`
- `/route/routes.py`
- `/static/img-zoom.css`
- `/static/img-zoom.js`

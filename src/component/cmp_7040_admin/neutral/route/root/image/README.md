# Admin Image Route

This route uses a snippet-first structure so the page is easier to maintain and AJAX rendering stays consistent with the first static render.

## Files

- `/neutral/route/root/image/content-snippets.ntpl`
  Main page template. It should stay small and mostly compose snippets.
- `/neutral/route/root/image/ajax/content-snippets.ntpl`
  AJAX route template. It renders the same image-list snippet logic used by the main page.
- `/neutral/route/image-snippets.ntpl`
  Shared snippets for the image admin route.

## Design Goal

The important rule is to avoid duplicating the grid markup between:

- the first server render
- the AJAX "load more" render
- any manual JavaScript DOM builder

Instead of generating cards in JavaScript, the server always renders the HTML through NTPL snippets.

## Snippet Responsibilities

The route is split into small snippets with one responsibility each:

- `admin_0yt2sa:image-feedback`
  Renders success and error alerts.
- `admin_0yt2sa:image-filters`
  Renders the search and filter form.
- `admin_0yt2sa:image-moderation-form`
  Renders the moderation form only.
- `admin_0yt2sa:image-moderation`
  Renders the exact-image moderation layout.
- `admin_0yt2sa:image-grid-items`
  Renders only the image cards.
- `admin_0yt2sa:image-grid-next`
  Renders the next AJAX load target and the `Load more` button.
- `admin_0yt2sa:image-grid-batch`
  Combines `image-grid-items` and `image-grid-next`.
- `admin_0yt2sa:image-main`
  Chooses between moderation view and grid view.

## Main Page Structure

The main page template only assembles the route:

1. Feedback
2. Filters
3. Main content

This keeps `/root/image/content-snippets.ntpl` readable and prevents it from turning into a long mixed template.

## AJAX Pattern

The AJAX implementation follows the same idea used in other Neutral TS components such as the RSS component:

- there is a dedicated AJAX route
- the AJAX route renders NTPL, not JSON
- the HTML comes from shared snippets
- the button uses Neutral TS declarative AJAX instead of custom `fetch()` card builders

The `Load more` button uses:

- `class="neutral-fetch-click"`
- `data-url=".../image/ajax?..."`
- `data-wrap="admin-image-grid-next-<offset>"`

When clicked, Neutral TS replaces the `data-wrap` target with the server-rendered fragment for the next batch.

## Why The Grid Is Split

The grid is intentionally split into:

- `image-grid-items`
- `image-grid-next`

This matters because the AJAX response must append only:

- new columns
- the next placeholder/button block

If the AJAX route returned a full wrapper row each time, the layout would break and new items could appear outside the existing grid.

## Maintenance Rule

If the card markup changes, update it in `/neutral/route/image-snippets.ntpl`, not in JavaScript.

For this route:

- avoid custom DOM builders in JS
- prefer reusable NTPL snippets
- keep page templates small
- keep AJAX templates as thin wrappers around shared snippets

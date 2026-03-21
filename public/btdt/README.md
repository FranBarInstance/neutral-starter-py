# Bootstrap 5 Dynamic Themes (BTDT)

A professional, real-time theme customizer and modular engine for Bootstrap 5. An alternative to **Bootswatch**.

[**🚀 Live Demo & Visual Designer**](https://franbarinstance.github.io/bootstrap-dynamic-themes/btdt/editor/)

**This is a production-ready theme system.** Use the included visual designer to create your look, and drop the self-contained module into your project.

## Project Structure

This project is organized as a standalone module (`btdt/`) that can be easily dropped into any project.

```text
.
├── btdt/
│   ├── css/              # Bootstrap base CSS and shared theme rules
│   ├── docs/             # Internal design docs
│   ├── editor/           # Visual theme editor
│   ├── img/              # Demo assets
│   ├── js/               # Runtime loader, editor engine and config catalogs
│   ├── scripts/          # Maintenance utilities
│   ├── themes/
│   │   ├── colors/       # Color palettes
│   │   ├── fonts/        # Typography modules
│   │   ├── modes/        # Dark mode overrides
│   │   ├── preset/       # Ready-to-use combined themes
│   │   └── styles/       # UI style modules (spacing, shadows, borders, etc.)
│   └── index.html        # Showcase / demo page
├── .agent/skills/        # Optional AI workflows for extending the catalog
├── .gitignore.example
└── README.md
```

## Workflow: Design to Production

1.  **Open the Editor**: Launch `btdt/editor/index.html` in your browser (or use the [Live Demo](https://franbarinstance.github.io/bootstrap-dynamic-themes/btdt/editor/)).
2.  **Design**: Use the panel to experiment with 50+ palettes, 50+ fonts, 50+ presets and multiple structural styles.
3.  **Export**: Click **"Copy CSS Preset"** to get your `@import` code.
4.  **Save & Link**: Save your design in `btdt/themes/preset/my-theme.css` and link it in your HTML.

### Editor Bundled Export

The visual editor also includes a browser-side helper at [`btdt/js/minify.js`](btdt/js/minify.js) for generating a **single bundled and minified preset CSS** from the current configuration.

It is designed to mirror the preset flow from [`btdt/scripts/minify/minify.py`](btdt/scripts/minify/minify.py):

- Resolves local `@import` rules recursively
- Leaves external or media-qualified `@import` rules untouched
- Hoists remaining `@import` rules to the top
- Minifies the final combined stylesheet

This feature is only available when the editor is served over `http://` or `https://`, because it relies on `fetch()` to read the imported CSS files. When the editor is opened via `file://`, the bundled export UI is disabled and shows a "not available on file://" message.

## BTDT vs. Bootswatch

While **Bootswatch** is an industry standard for static themes, **BTDT** takes it to the next level by being a dynamic engine:

- **100% Editable**: Don't just pick a theme; design it. Tweak every variable (colors, fonts, borders, rounding) in real-time.
- **Dynamic Runtime**: Change the entire look and feel or toggle dark mode on-the-fly via the Javascript API without a page reload.
- **Modular Design**: Mix and match components. Use the palette from one theme and the typography from another.
- **Custom Presets**: Create and save your own theme combinations using the preset system, making your designs reusable and easy to share.
- **No Compilation Required**: Unlike standard Bootstrap customization, you don't need SCSS, Ruby, or Node modules to tweak your look. Just standard CSS.
- **AI-Ready**: Extend the library easily using an AI assistant (see below).

## How it Works

The application uses a **Modular CSS Injection** strategy managed by the `ThemeManager` class.

1.  **Namespaced Engine**: Everything lives inside the `btdt/` folder to avoid filename collisions (like `js/` or `css/`) in your project.
2.  **Base Path Awareness**: The `ThemeManager` supports a `basePath` configuration, allowing it to find its theme modules regardless of where your HTML file is located.
3.  **Zero-CORS Metadata**: Presets include invisible CSS variables that the engine reads via computed styles, enabling full editor sync even in local environments (`file://`).

### Theme Personalities

BTDT can also apply **theme personalities**: final finish layers that add a distinctive character to a theme without fundamentally changing its identity.

In practice, a personality is not a new palette or a new typography system. It is a surface treatment applied on top of the current theme, usually through contour, shadow, texture, glow, filter, or other finish effects.

Current examples include:

- `none`: no additional finish layer
- `sketch`: irregular contours and rough-draft energy
- `asymmetric`: a more off-balance contour treatment that gives components a distinctive silhouette

The idea is simple: the theme defines what the interface is, and the personality defines how that same interface feels at the final visual layer.

## Pure CSS - No Compilation

Unlike many Bootstrap customization workflows that require complex SCSS/SASS setups, BTDT is built on **Pure CSS** using modern CSS custom properties (variables).

### Advantages:
- **Zero Build Steps**: No `npm install`, no Webpack, no Vite, and no precompilation required. Edit a CSS file and see the result instantly.
- **Runtime Hot-Swapping**: Change the entire look and feel of your app at runtime without reloading or rebuilding.
- **Portability**: The entire module works perfectly even when opened directly from the file system (`file:///`), making it ideal for prototyping.
- **Zero Learning Curve**: You don't need to know CSS or SASS. Use the visual customizer to design your theme and simply copy-paste the code.
- **Lightweight**: Zero toolchain overhead. You only ship the CSS you actually use.

## AI-Assisted Development

This project includes a set of **AI Skills** located in `.agent/skills/`. These allow an AI assistant to extend the project while maintaining professional standards.

You can ask your AI assistant to:
- **Create a new color theme**: "Create a premium dark theme inspired by Cyberpunk visuals."
- **Add new fonts**: "Integrate the 'Montserrat' font from Google Fonts."
- **Design structural styles**: "Create a style module with extra large shadows and glassmorphism."
- **Compose presets**: "Create a 'Minimalist' preset using the Inter font and White palette."

The AI will follow the established architecture, ensuring link legibility and Zero-CORS metadata compatibility.

## Implementation in Production

### 1. Integration
Copy the `btdt/` folder to your project root.

> [!IMPORTANT]
> **Production Safety**: Add `btdt/editor/` to your `.gitignore` to keep the customizer out of your public environment.

### 2. Choose Implementation Method

#### Option A: Native CSS (Maximum Performance)
Best for static sites where speed is the only priority. Zero JS dependency for initial load.

```html
<head>
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">
    <link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.css">
    <link id="theme-preset-dark" rel="stylesheet" href="btdt/themes/modes/dark.min.css" media="not all">
</head>

<body>
    ...
    <!-- API access -->
    <script src="btdt/js/btdt.min.js?v=x.x.x"></script>
</body>
```

This loads the initial preset directly from HTML. `btdt.js` does not need to load anything on startup in this setup. It only exposes the API so you can switch presets later if needed.

You can also start with a minified preset directly in the `<link>`:

```html
<link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.min.css">
```

#### Option B: All-in-One Loader (Saves a step)
The simplest way. One single line in the `<head>` handles both CSS injection and API initialization.

```html
<head>
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">
    <script data-preset="studio" data-minified="true" src="btdt/js/btdt.min.js"></script>
</head>
```

> [!NOTE]
> Using the JS loader (**Option B**) may cause a slight flash of unstyled content (FOUC) during page load as the CSS is injected via JavaScript. For a perfectly smooth experience, use **Option A**.

For production, prefer `btdt.min.js`. Adding a version to the script URL, for example `btdt/js/btdt.min.js?v=x.x.x`, is a simple way to invalidate browser cache after publishing changes.

The BTDT loader (`btdt.js` / `btdt.min.js`) is **CSP compliant**: it does not require inline styles, `eval`, or a nonce.

### About `theme-preset`

When using the JS loader, BTDT manages the active preset through a standard stylesheet tag:

```html
<link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.css">
```

This `id` is the fixed hook used by `btdt.js` to detect, reuse, or replace the current preset stylesheet. If it already exists, `btdt.load('aurora')` updates that same `<link>` instead of creating duplicates. If it does not exist, `btdt.js` creates it automatically.

For dark mode, the loader also manages a separate `<link id="theme-preset-dark">` pointing to `btdt/themes/modes/dark.min.css`, enabling it through the `media` attribute when needed.

Supported forms:

```html
<link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.css">
<link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.min.css">
<link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.min.css?v=x.x.x">
```

If you want full manual control, you can disable automatic initialization and keep the initial preset entirely in HTML:

```html
<head>
    <link rel="stylesheet" href="btdt/css/bootstrap.min.css">
    <link id="theme-preset" rel="stylesheet" href="btdt/themes/preset/studio.min.css">
    <script data-auto-init="false" src="btdt/js/btdt.min.js"></script>
</head>
```

In that configuration, `btdt.js` does not load any preset on startup. It only becomes available for later calls such as `btdt.load(...)`.

### 3. API Usage

Regardless of the option chosen (unless you skipped JS), you can use the global `btdt` object:

```javascript
btdt.load('aurora'); // Switch preset dynamically
btdt.toggleMode();   // Toggle Dark/Light mode
```

Available methods:

- `btdt.load(name)`
Loads a preset stylesheet dynamically. You can pass a preset name such as `studio` or `aurora`, or a direct CSS path.

```javascript
btdt.load('studio');
btdt.load('aurora');
btdt.load('aurora', { minified: true });
btdt.load('/assets/themes/custom-theme.css');
btdt.load('/assets/themes/custom-theme.min.css');
```

If `data-minified="true"` is present on the loader script, `btdt.load(name)` uses `*.min.css` by default for preset names. You can also request it per call with:

```javascript
btdt.load('aurora', { minified: true });
```

Common loading patterns:

- Load a named preset source file:

```javascript
btdt.load('studio'); // -> btdt/themes/preset/studio.css
```

- Load a named minified preset:

```javascript
btdt.load('studio', { minified: true }); // -> btdt/themes/preset/studio.min.css
```

- Load by direct path:

```javascript
btdt.load('btdt/themes/preset/studio.css');
btdt.load('btdt/themes/preset/studio.min.css');
```

- Use `data-minified="true"` as the default for later named preset loads:

```html
<script data-minified="true" src="btdt/js/btdt.min.js"></script>
```

```javascript
btdt.load('studio'); // -> btdt/themes/preset/studio.min.css
```

`data-minified="true"` does not load any preset by itself. It only changes the default target used later by `btdt.load(name)`.

If you only want to expose the API and decide later what to load, this is enough:

```html
<script src="btdt/js/btdt.min.js"></script>
```

- `btdt.setMode(mode)`
Sets the active mode explicitly. Accepted values are `light` and `dark`.

```javascript
btdt.setMode('dark');
btdt.setMode('light');
```

- `btdt.toggleMode()`
Switches between `light` and `dark`.

```javascript
btdt.toggleMode();
```

- `btdt.getMode()`
Returns the current mode as a string: `light` or `dark`.

```javascript
const mode = btdt.getMode();
```

Notes:

- `btdt.js` is a production loader. It only handles preset loading and dark/light mode.
- It does not depend on the editor or on `theme-manager.js`.
- It does not need to know which presets exist in advance. It simply updates the active preset stylesheet.
- Full loader documentation, attributes, dark-mode behavior and detailed examples: [btdt/docs/btdt.md](btdt/docs/btdt.md).

## Dynamic Contrast & Theming

A common challenge in Bootstrap 5+ is handling accessibility and contrast dynamically without bloating the HTML with `data-bs-theme` attributes.

### The Standard (Static) Approach
In standard Bootstrap (and static themes like Bootswatch), developers must explicitly define the contrast mode for each container. If you have a dark background, you add `data-bs-theme="dark"` (or old-school `navbar-dark`) to make the child elements (text, links, buttons) visible.

```html
<!-- You must know IN ADVANCE that bg-primary is dark -->
<header class="bg-primary" data-bs-theme="dark">
    <a class="nav-link" href="#">Static Link</a>
</header>
```
**The limitation**: This approach is hardcoded into your HTML. If you change your theme to a light version at runtime, the `data-bs-theme="dark"` attribute will remain, making the text unreadable (white text on a light background).

### The BTDT (Dynamic) Approach
BTDT handles contrast at the **CSS variable level**. Each theme module calculates its own contrast colors (`--bs-primary-contrast`, etc.), and the engine applies them automatically to components inside background utilities.

```html
<!-- Clean, Agnostic HTML -->
<header class="bg-primary">
    <a class="nav-link" href="#">Automatic Dynamic Link</a>
</header>
```
In some cases you may need to use `text-reset`.

```html
<!-- Clean, Agnostic HTML -->
<a class="nav-link text-reset" href="#">Automatic Dynamic Link</a>
```

- **Zero HTML Changes**: Switch from a dark professional theme to a light pastel style, and your menus, cards, and links **automatically adapt** their colors instantly.
- **Smart Icons**: The navbar toggler and other SVG icons automatically flip their filters to remain visible.
- **Harmonized Accents**: Themes include a synchronized `--accent-color` (automatically derived from your primary color) for decorative elements, ensuring a premium, integrated look across all 50+ palettes.

---
Built with ❤️ and Bootstrap 5.

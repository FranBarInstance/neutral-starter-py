/**
 * BTDT production loader — CSP compliant.
 * No inline styles, no eval, no nonce required.
 *
 * @file        btdt-loader.js
 * @description Production loader for BTDT. Handles color mode (light/dark) detection and application,
 *              loads the active preset's stylesheet, synchronizes UI elements based on the active mode,
 *              persists the mode preference to a cookie, and automatically binds toggle button listeners.
 *              Content Security Policy (CSP) compliant: no inline styles, eval, or nonce required.
 *
 * @usage
 *   <script src="path/to/btdt-loader.js"
 *           data-preset="preset-name"
 *           data-minified="true"
 *           data-auto-init="true"
 *           data-dark-value="dark"
 *           data-dark-cookie="dark_mode"
 *           data-cookie-expire="30"
 *           data-dark-system="true">
 *   </script>
 *
 * @attributes
 *   data-base-path    {string}   Base path for assets. Automatically detected from the script URL by default.
 *   data-preset       {string}   Name of the CSS preset to load (e.g. "default", "corporate").
 *                                Can be a short name or a complete path/URL to a .css file.
 *   data-minified     {boolean}  If "true", loads .min.css files. Default: false.
 *   data-auto-init    {boolean}  If "false", disables automatic initialization. Default: true.
 *   data-dark-value   {string}   A literal value indicating the initial dark mode state.
 *                                Dark values:  "1" | "true" | "yes" | "dark" | "on"
 *                                Light values: "0" | "false" | "no" | "light" | "off"
 *                                Useful for injecting a server-side preference directly into the attribute.
 *   data-dark-cookie  {string}   Name of the cookie that stores dark mode preference.
 *                                Dark values:  "1" | "true" | "yes" | "dark" | "on"
 *                                Light values: "0" | "false" | "no" | "light" | "off"
 *                                When set, the cookie is automatically updated on every mode change.
 *                                If not set, no cookie is read or written at any point.
 *   data-cookie-expire {number}  Cookie expiry in days (e.g. "30" = 30 days). "0" (default) creates
 *                                a session cookie that expires when the browser is closed. Any positive
 *                                integer sets a persistent cookie lasting that many days.
 *                                Ignored if data-dark-cookie is not set.
 *   data-dark-system  {boolean}  If "true", uses the operating system's prefers-color-scheme as mode preference.
 *
 * @priority    Color mode source resolution order:
 *              1. data-dark-value (literal attribute value)
 *              2. data-dark-cookie (browser cookie)
 *              3. data-dark-system (operating system preference)
 *              4. "light" (default value)
 *
 * @api         Exposes window.btdt with the following methods:
 *   btdt.load(name, options)  Loads a CSS preset by name or options.
 *   btdt.setMode(mode)        Sets the color mode ("light" | "dark").
 *   btdt.toggleMode()         Toggles between light and dark mode.
 *   btdt.getMode()            Returns the active color mode.
 *
 * @events
 *   btdt:modechange  Fired on <html> when color mode changes.
 *                    detail: { mode: "light" | "dark" }
 *
 * @dom
 *   .theme-light-dark-toggle  Buttons or links that trigger a mode toggle on click.
 *                             Listeners are registered automatically via event delegation on DOMContentLoaded,
 *                             so dynamically inserted elements are also supported.
 *   .dark-mode-enabled        Elements shown only in dark mode (display-none class toggled automatically).
 *   .dark-mode-disabled       Elements shown only in light mode (display-none class toggled automatically).
 */
(function() {
    if (window.btdt && window.btdt._initialized) return;

    const VERSION = '1.0.0';

    const script = document.currentScript;
    if (!script) return;

    const detectedBase    = script.src.split('/').slice(0, -2).join('/') + '/';
    const basePath        = (script.getAttribute('data-base-path') || detectedBase).replace(/\/?$/, '/');
    const autoInit        = script.getAttribute('data-auto-init') !== 'false';
    const initialPreset   = script.getAttribute('data-preset') || null;
    const defaultMinified = script.getAttribute('data-minified') === 'true';
    const darkValue       = script.getAttribute('data-dark-value') || null;
    const darkCookieName  = script.getAttribute('data-dark-cookie') || null;
    const cookieExpire    = parseInt(script.getAttribute('data-cookie-expire') || '0', 10);
    const useSystemDark   = script.getAttribute('data-dark-system') === 'true';

    const DARK_VALUES  = new Set(['1', 'true', 'yes', 'dark', 'on']);
    const LIGHT_VALUES = new Set(['0', 'false', 'no', 'light', 'off']);

    /**
     * Classifies a raw value as "dark", "light", or null if unrecognized.
     * Comparison is case-insensitive and trims surrounding whitespace.
     *
     * @param  {*}              value  The value to classify.
     * @return {"dark"|"light"|null}
     */
    function classifyValue(value) {
        if (value == null) return null;
        const n = String(value).trim().toLowerCase();
        if (DARK_VALUES.has(n))  return 'dark';
        if (LIGHT_VALUES.has(n)) return 'light';
        return null;
    }

    /**
     * Reads a cookie value by name.
     * The name is safely escaped before use in the RegExp.
     *
     * @param  {string}      name  Cookie name.
     * @return {string|null}       Decoded cookie value, or null if not found.
     */
    function getCookie(name) {
        const match = document.cookie.match(
            new RegExp('(?:^|; )' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '=([^;]*)')
        );
        return match ? decodeURIComponent(match[1]) : null;
    }

    /**
     * Determines the target color mode by evaluating all configured sources
     * in priority order:
     *   1. data-dark-value (literal attribute value)
     *   2. data-dark-cookie (browser cookie)
     *   3. data-dark-system (OS prefers-color-scheme)
     *   4. "light" (built-in default)
     *
     * @return {"dark"|"light"}
     */
    function resolveTargetMode() {
        if (darkValue)      { const r = classifyValue(darkValue);                 if (r) return r; }
        if (darkCookieName) { const r = classifyValue(getCookie(darkCookieName)); if (r) return r; }
        if (useSystemDark && window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return 'light';
    }

    const targetMode = resolveTargetMode();
    const html       = document.documentElement;

    // Apply the resolved mode to <html> immediately to avoid a flash of unstyled content (FOUC).
    html.setAttribute('data-bs-theme', targetMode);
    if (targetMode === 'dark') {
        html.setAttribute('data-mode', 'dark');
    } else {
        html.removeAttribute('data-mode');
    }

    /**
     * Finds an existing stylesheet <link> in <head> whose href pathname
     * contains the given filename fragment.
     *
     * @param  {string}          filename  Partial pathname to match (e.g. "themes/preset/").
     * @return {HTMLLinkElement|null}
     */
    function findLinkByFilename(filename) {
        const links = document.head.querySelectorAll('link[rel="stylesheet"]');
        for (let i = 0; i < links.length; i++) {
            const url = new URL(links[i].href);
            if (url.pathname.includes(filename)) return links[i];
        }
        return null;
    }

    /**
     * Locates the active preset <link> element by its id ("theme-preset")
     * or by matching its href against the preset path convention.
     *
     * @return {HTMLLinkElement|null}
     */
    function findPresetLink() {
        return document.getElementById('theme-preset') ||
               findLinkByFilename('themes/preset/') ||
               null;
    }

    /**
     * Resolves the full href for a preset stylesheet.
     * If name ends with ".css" or contains a "/" it is treated as a literal URL/path.
     * Otherwise it is expanded to: {basePath}themes/preset/{name}[.min].css
     *
     * @param  {string}      name     Preset name or path.
     * @param  {Object}      options  Optional overrides. options.minified {boolean}.
     * @return {string|null}          Resolved href, or null if name is falsy.
     */
    function resolvePresetHref(name, options) {
        if (!name) return null;
        if (name.endsWith('.css') || name.includes('/')) return name;
        const min = (options && options.minified != null) ? options.minified : defaultMinified;
        return `${basePath}themes/preset/${name}${min ? '.min' : ''}.css`;
    }

    /**
     * Returns the preset <link> element, creating and appending it to <head> if absent.
     * Reuses an existing element if one is already present (identified via findPresetLink).
     *
     * @return {HTMLLinkElement}
     */
    function ensurePresetLink() {
        const existing = findPresetLink();
        if (existing) { existing.id = 'theme-preset'; return existing; }
        const link = document.createElement('link');
        link.id  = 'theme-preset';
        link.rel = 'stylesheet';
        document.head.appendChild(link);
        return link;
    }

    /**
     * Returns the dark-mode overlay <link> element (id="theme-preset-dark"),
     * creating and appending it to <head> if absent.
     * The element's media attribute is set to "all" for dark mode and "not all"
     * for light mode so the stylesheet is loaded but only applied when needed,
     * preventing any layout shift when toggling.
     *
     * @return {HTMLLinkElement}
     */
    function ensureModeLink() {
        let link = document.getElementById('theme-preset-dark');
        if (!link) {
            link = document.createElement('link');
            link.id   = 'theme-preset-dark';
            link.rel  = 'stylesheet';
            link.href = `${basePath}themes/modes/dark.min.css?v=${VERSION}`;
            document.head.appendChild(link);
        }

        link.media = targetMode === 'dark' ? 'all' : 'not all';
        return link;
    }

    /**
     * Synchronizes DOM elements and the dark-mode cookie with the given mode.
     * Called on every mode change (including the initial state on DOMContentLoaded).
     *
     * Behavior:
     *   - Writes the mode value to the cookie configured via data-dark-cookie (if any).
     *   - Adds the "display-none" class to .dark-mode-enabled elements in light mode,
     *     and removes it in dark mode.
     *   - Adds the "display-none" class to .dark-mode-disabled elements in dark mode,
     *     and removes it in light mode.
     *
     * @param {"dark"|"light"} mode  The active color mode.
     */
    function syncModeUI(mode) {
        const isDark = mode === 'dark';

        // Persist mode preference to cookie so it survives page reloads.
        // Only written if data-dark-cookie is set and data-dark-value is not,
        // since data-dark-value takes priority and would override the cookie on next load.
        if (darkCookieName && !darkValue) {
            let cookieStr = `${darkCookieName}=${mode}; path=/`;
            if (cookieExpire > 0) {
                const date = new Date();
                date.setDate(date.getDate() + cookieExpire);
                cookieStr += `; expires=${date.toUTCString()}`;
            }
            // cookieExpire === 0: no expires attribute → session cookie.
            document.cookie = cookieStr;
        }

        // Show/hide elements designated for a specific mode.
        document.querySelectorAll('.dark-mode-enabled').forEach((el) => {
            el.classList.toggle('display-none', !isDark);
        });
        document.querySelectorAll('.dark-mode-disabled').forEach((el) => {
            el.classList.toggle('display-none', isDark);
        });
    }

    /**
     * Applies a color mode change to the document.
     * Updates data-bs-theme / data-mode attributes on <html>, toggles the
     * dark-mode stylesheet's media attribute, synchronizes UI elements and
     * the cookie via syncModeUI(), and dispatches the "btdt:modechange" event.
     *
     * @param  {"dark"|"light"} mode  The desired color mode.
     * @return {"dark"|"light"}       The normalized mode that was applied.
     */
    function applyMode(mode) {
        const normalized = mode === 'dark' ? 'dark' : 'light';
        const modeLink   = ensureModeLink();

        html.setAttribute('data-bs-theme', normalized);
        if (normalized === 'dark') {
            html.setAttribute('data-mode', 'dark');
            modeLink.media = 'all';
        } else {
            html.removeAttribute('data-mode');
            modeLink.media = 'not all';
        }

        // Synchronize cookie and mode-specific DOM elements.
        syncModeUI(normalized);

        html.dispatchEvent(new CustomEvent('btdt:modechange', {
            bubbles: true,
            detail: { mode: normalized }
        }));

        return normalized;
    }

    /**
     * Public API exposed on window.btdt.
     */
    window.btdt = {
        _initialized: true,
        _mode: targetMode,

        /**
         * Loads a CSS preset stylesheet.
         * If a <link id="theme-preset"> already exists its href is updated in place;
         * otherwise a new <link> is created and appended to <head>.
         *
         * @param  {string} name     Preset name (e.g. "corporate") or a full path/URL ending in ".css".
         * @param  {Object} options  Optional overrides.
         * @param  {boolean} [options.minified]  Load the .min.css variant. Defaults to data-minified.
         * @return {this}            Chainable.
         */
        load: function(name, options) {
            const href = resolvePresetHref(name, options);
            if (!href) return this;
            const link = ensurePresetLink();
            if (link.href !== href) link.href = href;
            return this;
        },

        /**
         * Sets the active color mode.
         * Internally delegates to applyMode(), which updates the DOM, the cookie,
         * and dispatches the btdt:modechange event.
         *
         * @param  {"dark"|"light"} mode  The desired color mode.
         * @return {this}                 Chainable.
         */
        setMode: function(mode) {
            this._mode = applyMode(mode);
            return this;
        },

        /**
         * Toggles between "dark" and "light" mode.
         * Equivalent to calling setMode() with the opposite of the current mode.
         *
         * @return {this}  Chainable.
         */
        toggleMode: function() {
            return this.setMode(this._mode === 'dark' ? 'light' : 'dark');
        },

        /**
         * Returns the currently active color mode.
         *
         * @return {"dark"|"light"}
         */
        getMode: function() {
            return this._mode;
        }
    };

    if (autoInit) {
        const existingPreset = findPresetLink();

        if (existingPreset) {
            // Adopt any preset <link> already present in the markup.
            existingPreset.id = 'theme-preset';
        } else if (initialPreset) {
            window.btdt.load(initialPreset);
        }

        ensureModeLink();

        // When relying solely on the OS preference, listen for system-level changes
        // and update the mode in real time (only if no other source takes priority).
        if (useSystemDark && !darkValue && !darkCookieName && window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', function(e) {
                    window.btdt.setMode(e.matches ? 'dark' : 'light');
                });
        }

        // Wait for the DOM to be ready before binding UI-related behaviour.
        document.addEventListener('DOMContentLoaded', function () {
            // Bring mode-specific elements into sync with the resolved initial mode.
            syncModeUI(targetMode);

            // Register a single delegated click listener for all toggle buttons.
            // Using event delegation on document ensures dynamically inserted
            // .theme-light-dark-toggle elements are also handled without re-binding.
            document.addEventListener('click', function (ev) {
                const btn = ev.target.closest('.theme-light-dark-toggle');
                if (!btn) return;
                ev.preventDefault();
                window.btdt.toggleMode();
            });
        });
    }
})();

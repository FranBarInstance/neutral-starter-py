/**
 * BTDT (Bootstrap Dynamic Themes) - Smart Loader
 * Provides an easy entry point for production integration.
 */
(function() {
    // Prevent double execution
    if (window.btdt && window.btdt._initialized) return;

    const script = document.currentScript;
    if (!script) return;

    // 1. Config & Path detection
    const initialPreset = script.getAttribute('data-preset');
    const autoInit = script.getAttribute('data-auto-init') !== 'false';
    const detectedBase = script.src.split('/').slice(0, -2).join('/') + '/';
    const basePath = script.getAttribute('data-base-path') || detectedBase;

    // 2. CSS Injection or Detection
    const linkId = 'theme-preset';
    let existingLink = document.getElementById(linkId);

    // If no ID exists, try to find a link that looks like a BTDT preset
    if (!existingLink) {
        existingLink = Array.from(document.querySelectorAll('link[rel="stylesheet"]'))
            .find(link => link.href.includes('themes/preset/'));
        if (existingLink) existingLink.id = linkId; // Link it to the API
    }

    if (initialPreset && !existingLink) {
        const link = document.createElement('link');
        link.id = linkId;
        link.rel = 'stylesheet';
        link.href = initialPreset.endsWith('.css')
            ? initialPreset
            : `${basePath}themes/preset/${initialPreset}.css`;
        document.head.appendChild(link);
    }

    // 3. Global API Object
    window.btdt = {
        _initialized: true,
        _manager: null,
        _loading: null,

        /**
         * Returns the full ThemeManager instance. Low-level access.
         */
        getManager: function() {
            if (this._manager) return Promise.resolve(this._manager);
            if (this._loading) return this._loading;

            this._loading = new Promise((resolve) => {
                const s = document.createElement('script');
                s.src = `${basePath}js/theme-manager.js`;
                s.onload = () => {
                    this._manager = new ThemeManager({ basePath });
                    resolve(this._manager);
                };
                document.head.appendChild(s);
            });
            return this._loading;
        },

        /**
         * Loads a preset by name.
         * @param {string} name - Preset name (e.g., 'studio', 'aurora')
         */
        load: async function(name) {
            const m = await this.getManager();
            return m.applyPreset(name);
        },

        /**
         * Toggles between light and dark mode.
         */
        toggleMode: async function() {
            const m = await this.getManager();
            return m.toggleMode();
        },

        /**
         * Set specific mode ('light' or 'dark').
         */
        setMode: async function(mode) {
            const m = await this.getManager();
            return m.setMode(mode);
        }
    };

    // 4. Background initialization
    if (autoInit) {
        window.btdt.getManager();
    }
})();

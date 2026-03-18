// js/theme-manager.js

class ThemeManager {
  constructor(options = {}) {
    // Base path for theme files (e.g., 'btdt/' or '../')
    this.basePath = options.basePath || '';
    // Ensure basePath ends with a slash if not empty
    if (this.basePath && !this.basePath.endsWith('/')) {
      this.basePath += '/';
    }

    // Configuration from external files or defaults
    const colors = window.BTDT_COLORS || {};
    const fonts = window.BTDT_FONTS || {};
    const ui = window.BTDT_UI || {};

    // Available theme categories
    this.categories = {
      colors: Object.keys(colors).length ? Object.keys(colors) : [
        'ocean', 'sunset', 'forest', 'lavender', 'corporate', 'candy',
        'white', 'gray-light', 'black', 'teal', 'rose', 'amber', 'mint', 'peach', 'sky'
      ],
      fonts: Object.keys(fonts).length ? Object.keys(fonts) : [
        'inter', 'merriweather', 'nunito', 'jetbrains-mono'
      ],
      background: Object.keys(ui.background || {}).length ? Object.keys(ui.background) : [
        'none',
        'primary-low', 'primary-medium', 'primary-high',
        'secondary-low', 'secondary-medium', 'secondary-high',
        'gray-low', 'gray-medium', 'gray-high'
      ],
      borders: Object.keys(ui.borders || {}).length ? Object.keys(ui.borders) : ['normal', 'minimal', 'extra', 'none'],
      rounding: Object.keys(ui.rounding || {}).length ? Object.keys(ui.rounding) : ['normal', 'extra', 'none'],
      shadows: Object.keys(ui.shadows || {}).length ? Object.keys(ui.shadows) : ['normal', 'extra', 'none'],
      spacing: Object.keys(ui.spacing || {}).length ? Object.keys(ui.spacing) : ['normal', 'large', 'small'],
      gradients: Object.keys(ui.gradients || {}).length ? Object.keys(ui.gradients) : ['on', 'off'],
      accent: Object.keys(ui.accent || {}).length ? Object.keys(ui.accent) : ['none', 'left', 'right', 'top', 'bottom'],
      accentSize: Object.keys(ui.accentSize || {}).length ? Object.keys(ui.accentSize) : ['1', '2', '3', '4', '5'],
      accentColor: Object.keys(ui.accentColor || {}).length ? Object.keys(ui.accentColor) : ['primary', 'secondary', 'gray']
    };

    // Available modes
    this.modes = ['light', 'dark'];

    // Current mode ('light' | 'dark')
    this._mode = 'light';

    // Current active theme
    this.activeTheme = {
      colors: null, fonts: null, background: null, borders: null, rounding: null,
      shadows: null, spacing: null, gradients: null, accent: null, accentSize: null, accentColor: null
    };

    // Predefined presets
    const presetData = window.BTDT_PRESETS || {};
    this.presets = Object.keys(presetData).length ? Object.keys(presetData) : ['default'];

    // Cache buster for theme CSS. Helps when iterating on theme files.
    this._cacheBust = String(Date.now());

    this._initContainer();
    this._initModeLink();
    this.loadFromStorage();
  }

  _withCacheBust(path) {
    if (!path) return path;
    const sep = path.includes('?') ? '&' : '?';
    return `${path}${sep}v=${this._cacheBust}`;
  }

  _getCascadeOrder() {
    return ['colors', 'fonts', 'background', 'borders', 'rounding', 'shadows', 'spacing', 'gradients', 'accent', 'accentSize', 'accentColor'];
  }

  _reorderThemeLinks() {
    this._getCascadeOrder().forEach((category) => {
      const link = document.getElementById(`theme-${category}`);
      if (link) {
        this.container.appendChild(link);
      }
    });

    if (this._modeLink) {
      document.head.appendChild(this._modeLink);
    }
  }

  // Creates a container for theme CSS
  _initContainer() {
    // Use <head> directly so <link rel="stylesheet"> is always applied.
    // (Some browsers may ignore <link> nested inside a <div> in <head>.)
    const legacy = document.getElementById('theme-styles');
    if (legacy) legacy.remove();
    this.container = document.head;
  }

  // Creates the <link> placeholder for the dark mode CSS
  _initModeLink() {
    let link = document.getElementById('theme-mode');
    if (!link) {
      link = document.createElement('link');
      link.rel = 'stylesheet';
      link.id = 'theme-mode';
      link.setAttribute('data-theme-category', 'mode');
      // Disabled by default (light mode)
      link.disabled = true;
      link.href = this._withCacheBust(`${this.basePath}themes/modes/dark.css`);
      // Always last in <head> so it overrides
      document.head.appendChild(link);
    }
    this._modeLink = link;
  }

  // Helper to ensure path uses the correct base
  _resolvePath(relativePath) {
    return `${this.basePath}${relativePath}`;
  }

  // Category to file path mapping
  _getPath(category, value) {
    if (!value) return null;

    const pathMap = {
      colors:   `themes/colors/${value}.css`,
      fonts:    `themes/fonts/${value}.css`,
      background:`themes/styles/background-${value}.css`,
      borders:  `themes/styles/borders-${value}.css`,
      rounding: `themes/styles/rounding-${value}.css`,
      shadows:  `themes/styles/shadows-${value}.css`,
      spacing:  `themes/styles/spacing-${value}.css`,
      gradients:`themes/styles/gradients-${value}.css`,
      accent:   `themes/styles/accent-${value}.css`,
      accentSize:`themes/styles/accent-${value}.css`,
      accentColor:`themes/styles/accent-${value}.css`
    };

    return pathMap[category] ? this._resolvePath(pathMap[category]) : null;
  }

  // Load individual CSS by category
  _loadCSS(category, value) {
    // Remove previous of this category
    const existingLink = document.getElementById(`theme-${category}`);
    if (existingLink) {
      existingLink.remove();
    }

    if (!value) {
      this.activeTheme[category] = null;
      return;
    }

    const path = this._getPath(category, value);
    if (!path) return;

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = this._withCacheBust(path);
    link.id = `theme-${category}`;
    link.setAttribute('data-theme-category', category);
    link.setAttribute('data-theme-value', value);

    this.container.appendChild(link);
    this.activeTheme[category] = value;
    this._reorderThemeLinks();
  }

  // ===== MODE API =====

  /**
   * Set the display mode.
   * @param {'light'|'dark'} mode
   */
  setMode(mode) {
    if (!this.modes.includes(mode)) {
      console.warn(`Mode "${mode}" is not valid. Use 'light' or 'dark'.`);
      return this;
    }
    this._mode = mode;

    if (mode === 'dark') {
      document.documentElement.setAttribute('data-mode', 'dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      this._modeLink.disabled = false;
    } else {
      document.documentElement.removeAttribute('data-mode');
      document.documentElement.setAttribute('data-bs-theme', 'light');
      this._modeLink.disabled = true;
    }
    // Ensure mode CSS stays last in the cascade.
    if (this._modeLink) {
      document.head.appendChild(this._modeLink);
    }

    this._saveModeToStorage();
    this._dispatchEvent('mode', mode);
    return this;
  }

  /** Toggle between light and dark. */
  toggleMode() {
    return this.setMode(this._mode === 'dark' ? 'light' : 'dark');
  }

  /** Returns current mode string ('light' | 'dark'). */
  getMode() {
    return this._mode;
  }

  /** Load saved mode from localStorage. */
  loadModeFromStorage() {
    try {
      const saved = localStorage.getItem('bs-theme-mode');
      if (saved && this.modes.includes(saved)) {
        this.setMode(saved);
      }
    } catch (e) { /* silent */ }
    return this;
  }

  _saveModeToStorage() {
    try {
      localStorage.setItem('bs-theme-mode', this._mode);
    } catch (e) { /* silent */ }
  }

  // ===== PUBLIC API =====

  // Change single category
  set(category, value) {
    if (!this.categories[category]) {
      console.warn(`Category "${category}" does not exist`);
      return this;
    }
    if (value && !this.categories[category].includes(value)) {
      console.warn(`Value "${value}" is not valid for "${category}"`);
      return this;
    }

    // If a preset is active, "materialize" its values
    if (this.activeTheme._preset) {
      // Robustness: Attempt one last sync just in case the CSS loaded 
      // but the event hasn't fired yet
      this._syncFromComputedStyles();

      const currentValues = { ...this.activeTheme };
      const presetName = currentValues._preset;

      // Check if we actually have data to materialize. 
      // If everything is null, the preset is likely still loading.
      const hasData = Object.keys(currentValues).some(cat => cat !== '_preset' && currentValues[cat] !== null);

      if (hasData) {
        this._removeActivePreset();
        Object.entries(currentValues).forEach(([cat, val]) => {
          if (cat !== '_preset' && cat !== category && val) {
            this._loadCSS(cat, val);
          }
        });
      } else {
        console.warn(`Cannot materialize preset "${presetName}" yet - still loading metadata.`);
        // We'll let the set proceed but keep the preset link for now to avoid total reset
      }
    }

    this._loadCSS(category, value);
    this._saveToStorage();
    this._dispatchEvent(category, value);
    return this; 
  }

  _removeActivePreset() {
    const link = document.getElementById('theme-preset');
    if (link) link.remove();
    this.activeTheme._preset = null;
  }

  /**
   * Apply complete preset via CSS file
   * High compatibility: uses computed styles to recover metadata (no CORS issues)
   */
  async applyPreset(presetName) {
    if (!this.presets.includes(presetName)) {
      console.warn(`Preset "${presetName}" does not exist`);
      return this;
    }

    const path = this._resolvePath(`themes/preset/${presetName}.css`);
    
    // 1. Clear individual styles
    Object.keys(this.activeTheme).forEach(cat => {
      if (cat !== '_preset') {
        const link = document.getElementById(`theme-${cat}`);
        if (link) link.remove();
        this.activeTheme[cat] = null;
      }
    });

    // 2. Load the preset CSS file
    let link = document.getElementById('theme-preset');
    if (!link) {
      link = document.createElement('link');
      link.id = 'theme-preset';
      link.rel = 'stylesheet';
      this.container.appendChild(link);
    }
    
    this.activeTheme._preset = presetName;
    
    return new Promise((resolve) => {
      let settled = false;

      const finalizeSuccess = () => {
        if (settled) return;
        settled = true;
        // Double check: give the browser a tiny moment to parse the root variables
        setTimeout(() => {
          this._syncFromComputedStyles();
          this._saveToStorage();
          this._dispatchEvent('preset', presetName);
          if (this._modeLink) document.head.appendChild(this._modeLink);
          link.onload = null;
          link.onerror = null;
          resolve(this);
        }, 50);
      };

      const finalizeError = () => {
        if (settled) return;
        settled = true;
        console.error(`Failed to load preset: ${presetName}`);
        this.activeTheme._preset = null;
        this._saveToStorage();
        link.onload = null;
        link.onerror = null;
        resolve(this);
      };

      link.onload = finalizeSuccess;
      link.onerror = finalizeError;
      
      link.href = this._withCacheBust(path);

      // Security fallback for very slow connections or cached files where onload might be tricky
      setTimeout(() => {
        if (!settled && !this.activeTheme.colors) finalizeSuccess();
      }, 1500);
    });
  }

  /**
   * Reads metadata from CSS variables defined in :root by the preset
   * Example: --preset-colors: "ocean";
   */
  _syncFromComputedStyles() {
    console.log("Syncing config from computed styles...");
    const styles = getComputedStyle(document.documentElement);
    
    Object.keys(this.activeTheme).forEach(cat => {
      if (cat === '_preset') return;
      
      const varName = `--preset-${cat}`;
      const value = styles.getPropertyValue(varName).trim().replace(/"/g, '').replace(/'/g, '');
      
      if (value && value !== 'initial' && value !== '') {
        this.activeTheme[cat] = value;
        console.log(`-> Recovered ${cat}: ${value}`);
      }
    });
  }

  // Apply complete custom config
  async applyConfig(config) {
    if (config._preset) {
      return await this.applyPreset(config._preset);
    }

    Object.entries(config).forEach(([category, value]) => {
      if (this.categories[category]) {
        this._loadCSS(category, value);
      }
    });

    this._saveToStorage();
    this._dispatchEvent('config', config);
    return this;
  }

  // Reset to Bootstrap default
  reset() {
    this._removeActivePreset();
    Object.keys(this.activeTheme).forEach(category => {
      if (category !== '_preset') {
        const link = document.getElementById(`theme-${category}`);
        if (link) link.remove();
        this.activeTheme[category] = null;
      }
    });

    this._saveToStorage();
    this._dispatchEvent('reset', null);
    return this;
  }

  // Get current configuration
  getConfig() {
    return { ...this.activeTheme };
  }

  // Generates CSS @import statements for a preset file
  generatePresetCSS() {
    const config = this.getConfig();
    let css = "/* Theme Preset - Save as themes/preset/custom.css */\n";
    
    Object.entries(config).forEach(([cat, val]) => {
      if (!val || cat === '_preset') return;
      
      let path = "";
      if (cat === 'colors') path = `../colors/${val}.css`;
      else if (cat === 'fonts') path = `../fonts/${val}.css`;
      else if (cat === 'accentSize' || cat === 'accentColor') path = `../styles/accent-${val}.css`;
      else path = `../styles/${cat}-${val}.css`;
      
      css += `@import "${path}";\n`;
    });

    // Invisible metadata block for file:// compatibility
    css += `\n/* Metadata for the editor */\n`;
    css += `:root {\n`;
    Object.entries(config).forEach(([cat, val]) => {
      if (!val || cat === '_preset') return;
      css += `  --preset-${cat}: "${val}";\n`;
    });
    css += `}\n`;
    
    return css;
  }

  // Get list of presets
  getPresets() {
    return this.presets;
  }

  // Add custom preset
  addPreset(name) {
    if (!this.presets.includes(name)) {
      this.presets.push(name);
    }
    return this;
  }

  // Save to localStorage
  _saveToStorage() {
    try {
      localStorage.setItem(
        'bs-theme-config',
        JSON.stringify(this.activeTheme)
      );
    } catch (e) { /* silent */ }
  }

  // Load from localStorage
  loadFromStorage() {
    try {
      const saved = localStorage.getItem('bs-theme-config');
      if (saved) {
        const config = JSON.parse(saved);
        this.applyConfig(config);
      }
    } catch (e) { /* silent */ }
    this.loadModeFromStorage();
    return this;
  }

  // Custom event
  _dispatchEvent(category, value) {
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: {
        category,
        value,
        fullConfig: this.getConfig()
      }
    }));
  }
}

// Export for module systems or use as a global class
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
} else {
  window.ThemeManager = ThemeManager;
}

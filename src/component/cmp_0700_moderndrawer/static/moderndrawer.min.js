(() => {
    const STORAGE_KEY = 'theme-drawer-state';
    const drawer = document.getElementById('theme-drawer');
    const toggle = document.getElementById('theme-drawer-toggle');
    const tabsToggle = document.getElementById('theme-drawer-tabs-toggle-btn');
    const closeBtn = document.getElementById('theme-drawer-close');
    const overlay = document.getElementById('theme-drawer-overlay');
    const navbar = document.getElementById('main-navbar');
    const tabButtons = drawer ? drawer.querySelectorAll('#theme-drawer-tabs [data-bs-toggle="pill"]') : [];
    const closableLinks = drawer ? drawer.querySelectorAll('.theme-drawer-link-close') : [];
    const states = ['theme-drawer-state-full', 'theme-drawer-state-icons', 'theme-drawer-state-hidden'];
    let refreshToken = 0;

    if (!drawer || !toggle || !tabsToggle || !overlay || !navbar) {
        return;
    }

    const isMobile = () => window.innerWidth < 768;

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie
            .split(';')
            .map((item) => item.trim())
            .find((item) => item.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : '';
    }

    function setCookie(name, value, days = 30) {
        const expires = new Date(Date.now() + (days * 24 * 60 * 60 * 1000)).toUTCString();
        document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
    }

    function syncNavbarHeight() {
        document.documentElement.style.setProperty('--theme-navbar-h', `${navbar.offsetHeight || 56}px`);
    }

    function normalizeState(state) {
        if (isMobile()) {
            return state === 'theme-drawer-state-full' ? state : 'theme-drawer-state-hidden';
        }
        return states.includes(state) ? state : 'theme-drawer-state-hidden';
    }

    function recoverState(state) {
        if (isMobile()) {
            return 'theme-drawer-state-hidden';
        }
        const normalized = normalizeState(state);
        if (!isMobile() && normalized === 'theme-drawer-state-full') {
            return 'theme-drawer-state-icons';
        }
        return normalized;
    }

    function ensureActiveTab() {
        const activeButton = drawer.querySelector('#theme-drawer-tabs .active');
        const activePane = drawer.querySelector('#theme-drawer-tabs-content .tab-pane.active');
        if (activeButton && activePane) {
            return;
        }
        const firstButton = tabButtons[0];
        const firstPaneSelector = firstButton ? firstButton.getAttribute('data-bs-target') : '';
        const firstPane = firstPaneSelector ? drawer.querySelector(firstPaneSelector) : null;
        if (!firstButton) {
            return;
        }
        firstButton.classList.add('active');
        firstButton.setAttribute('aria-selected', 'true');
        if (firstPane) {
            firstPane.classList.add('active', 'show');
        }
    }

    function applyState(rawState) {
        const state = normalizeState(rawState);
        states.forEach((item) => drawer.classList.remove(item));
        drawer.classList.add(state);

        document.body.classList.remove('theme-drawer-layout-full', 'theme-drawer-layout-icons', 'theme-drawer-layout-hidden');
        if (state === 'theme-drawer-state-full') {
            document.body.classList.add('theme-drawer-layout-full');
        } else if (state === 'theme-drawer-state-icons') {
            document.body.classList.add('theme-drawer-layout-icons');
        } else {
            document.body.classList.add('theme-drawer-layout-hidden');
        }

        const expanded = state !== 'theme-drawer-state-hidden';
        toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        tabsToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        overlay.classList.toggle('show', isMobile() && expanded);
        setCookie(STORAGE_KEY, isMobile() ? 'theme-drawer-state-hidden' : state);
    }

    function nextState() {
        if (isMobile()) {
            return drawer.classList.contains('theme-drawer-state-full') ? 'theme-drawer-state-hidden' : 'theme-drawer-state-full';
        }
        if (drawer.classList.contains('theme-drawer-state-full')) {
            return 'theme-drawer-state-icons';
        }
        if (drawer.classList.contains('theme-drawer-state-icons')) {
            return 'theme-drawer-state-hidden';
        }
        return 'theme-drawer-state-full';
    }

    function getCurrentState() {
        return states.find((state) => drawer.classList.contains(state)) || 'theme-drawer-state-hidden';
    }

    function refreshLayout(useStoredState = false) {
        syncNavbarHeight();
        ensureActiveTab();
        const state = useStoredState
            ? recoverState(getCookie(STORAGE_KEY) || 'theme-drawer-state-hidden')
            : getCurrentState();
        applyState(state);
    }

    function scheduleRefresh(useStoredState = false) {
        refreshToken += 1;
        const currentToken = refreshToken;
        refreshLayout(useStoredState);
        requestAnimationFrame(() => {
            if (currentToken !== refreshToken) {
                return;
            }
            refreshLayout(useStoredState);
            requestAnimationFrame(() => {
                if (currentToken !== refreshToken) {
                    return;
                }
                refreshLayout(useStoredState);
            });
        });
    }

    toggle.addEventListener('click', () => {
        ensureActiveTab();
        applyState(nextState());
    });

    tabsToggle.addEventListener('click', () => {
        ensureActiveTab();
        applyState(nextState());
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => applyState('theme-drawer-state-hidden'));
    }

    overlay.addEventListener('click', () => applyState('theme-drawer-state-hidden'));

    tabButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!isMobile() && drawer.classList.contains('theme-drawer-state-icons')) {
                applyState('theme-drawer-state-full');
            }
        });
    });

    closableLinks.forEach((link) => {
        link.addEventListener('click', () => {
            if (isMobile()) {
                applyState('theme-drawer-state-hidden');
            }
        });
    });

    window.addEventListener('resize', () => {
        scheduleRefresh(false);
    });

    window.addEventListener('load', () => scheduleRefresh(true));
    window.addEventListener('pageshow', () => scheduleRefresh(true));
    window.addEventListener('neutralFetchCompleted', () => {
        if (isMobile()) {
            applyState('theme-drawer-state-hidden');
            return;
        }
        scheduleRefresh(false);
    });
    window.addEventListener('pagehide', () => {
        if (isMobile()) {
            setCookie(STORAGE_KEY, 'theme-drawer-state-hidden');
        }
    });

    if (typeof ResizeObserver !== 'undefined') {
        const navbarObserver = new ResizeObserver(() => {
            scheduleRefresh(false);
        });
        navbarObserver.observe(navbar);
    }

    scheduleRefresh(true);
})();

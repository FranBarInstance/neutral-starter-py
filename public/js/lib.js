/*! See: https://github.com/FranBarInstance/neutral-pwa-py */

(function () {
    'use strict';

    if (typeof lib_config !== 'object') {
        console.error("Error: lib_config is not defined.");
        return;
    }

    function getCookie(name) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return cookie.substring(name.length + 1);
            }
        }
        return '';
    }

    // Detect changes when opening a new tab.
    document.addEventListener('DOMContentLoaded', function () {
        let current_tab_status = getCookie(lib_config.cookie_tab);
        window.addEventListener('focus', () => {
            const new_tab_status = getCookie(lib_config.cookie_tab);
            if (current_tab_status != new_tab_status) {
                current_tab_status = new_tab_status
                const reload = confirm(lib_config.reload_msg);
                if (reload) self.location.href = self.location.href.split('#')[0];
            }
        });
    });
})();

(function () {
    'use strict';

    var resizeObserver = null;
    var observedNavbar = null;

    function syncHeight() {
        var navbar = document.getElementById('main-navbar');
        var spacer = document.getElementById('main-navbar-hidden');
        if (!navbar || !spacer) return;

        var position = window.getComputedStyle(navbar).position;
        var isFixed = /fixed|sticky/i.test(position);

        if (isFixed) {
            spacer.style.height = navbar.getBoundingClientRect().height + 'px';
            spacer.style.display = '';
        } else {
            spacer.style.height = '0px';
            spacer.style.display = 'none';
        }
    }

    function initNavbarSpacer() {
        var navbar = document.getElementById('main-navbar');
        var spacer = document.getElementById('main-navbar-hidden');
        if (!navbar || !spacer) return;

        if (resizeObserver && observedNavbar !== navbar) {
            resizeObserver.disconnect();
            observedNavbar = null;
        }

        if (typeof ResizeObserver !== 'undefined' && !observedNavbar) {
            resizeObserver = new ResizeObserver(syncHeight);
            resizeObserver.observe(navbar);
            observedNavbar = navbar;
        }

        syncHeight();
    }

    window.addEventListener('load', initNavbarSpacer);
    window.addEventListener('resize', syncHeight);
    window.addEventListener('neutralFetchCompleted', initNavbarSpacer);

    initNavbarSpacer();
})();


(function () {
    'use strict';

    // Icon page loading
    window.addEventListener('load', (ev) => {
        setTimeout(() => {
            document.querySelectorAll('.page-is-loading').forEach(element => {
                element.classList.add('d-none');
            });
            document.querySelectorAll('.page-has-loaded').forEach(element => {
                element.classList.remove('d-none');
            });
        }, 250);
    });
    window.addEventListener('pagehide', function () {
        document.querySelectorAll('.page-is-loading').forEach(element => {
            element.classList.add('d-none');
        });
        document.querySelectorAll('.page-has-loaded').forEach(element => {
            element.classList.remove('d-none');
        });
    });
    document.querySelectorAll('a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const thisSite = window.location.origin;
            const href = this.getAttribute('href');
            const target = this.getAttribute('target');
            if (href) {
                if (href.substring(0, 1) === "/" ||
                    href.substring(0, 1) === "?" ||
                    href.substring(0, thisSite.length) === thisSite) {
                    if (target !== "_blank") {
                        document.querySelectorAll('.page-has-loaded').forEach(el => {
                            el.classList.add('d-none');
                        });
                        document.querySelectorAll('.page-is-loading').forEach(el => {
                            el.classList.remove('d-none');
                        });
                        setTimeout(function () {
                            document.querySelectorAll('.page-is-loading').forEach(el => {
                                el.classList.add('d-none');
                            });
                            document.querySelectorAll('.page-has-loaded').forEach(el => {
                                el.classList.remove('d-none');
                            });
                        }, 12000);
                    }
                }
            }
        });
    });
})();

(function () {
    'use strict';

    function convertTimestampToDate() {
        document.querySelectorAll('.timestamp-to-date').forEach(function (element) {
            var dateUTC = element.textContent;
            if (dateUTC) {
                // Check if it's a numeric timestamp (seconds from Unix epoch)
                var timestamp = parseInt(dateUTC, 10);
                if (!isNaN(timestamp) && timestamp > 100000000) {
                    // Convert seconds to milliseconds
                    timestamp = timestamp * 1000;
                }
                var dateLocal = new Date(timestamp);
                if (!isNaN(dateLocal.getTime())) {
                    element.textContent = dateLocal.toLocaleString(undefined, {
                        year: '2-digit',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    }).replace(",", "");
                }
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        convertTimestampToDate();
    });

    document.addEventListener('neutralFetchCompleted', function () {
        convertTimestampToDate();
    });
})();

(function () {
    'use strict';

    function activeTab(retries = 10) {
        requestAnimationFrame(function () {
            const path = window.location.pathname;

            const allLinks = document.querySelectorAll(".tab-pane .list-group-item");
            if (!allLinks.length) {
                if (retries > 0) {
                    setTimeout(() => activeTab(retries - 1), 25);
                }
                return;
            }

            let bestMatch = null;
            let bestLength = 0;
            let homeLink = null;

            allLinks.forEach((link) => {
                const href = link.getAttribute("href");

                if (!href || href === "#" || href.startsWith("?") || href.startsWith("#")) return;

                if (href === "/") {
                    homeLink = link;
                    return;
                }

                const isMatch = path === href || path.startsWith(href + "/");

                if (isMatch && href.length > bestLength) {
                    bestLength = href.length;
                    bestMatch = link;
                }
            });

            if (!bestMatch) {
                bestMatch = path === "/" ? homeLink : homeLink;
            }

            if (!bestMatch) return;

            const pane = bestMatch.closest(".tab-pane");
            if (!pane) {
                if (retries > 0) activeTab(retries - 1);
                return;
            }

            const btn = document.querySelector(`[data-bs-target="#${pane.id}"]`);
            if (!btn) {
                if (retries > 0) activeTab(retries - 1);
                return;
            }

            if (typeof bootstrap !== "undefined") {
                bootstrap.Tab.getOrCreateInstance(btn).show();
            } else {
                document.querySelectorAll(".drawer-btn.nav-link")
                    .forEach((b) => b.classList.remove("active"));
                document.querySelectorAll(".tab-pane")
                    .forEach((p) => p.classList.remove("show", "active"));

                btn.classList.add("active");
                pane.classList.add("show", "active");
            }
        });
    }


    document.addEventListener('DOMContentLoaded', function () {
        activeTab();
    });

    document.addEventListener('neutralFetchCompleted', function () {
        activeTab();
    });
})();

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

    // Simulate height navigation bar spacing form main navbar
    function currentMainNavbarHeight() {
        var eleMainNavbar   = document.getElementById('main-navbar');
        var eleNavbarHidden = document.getElementById('main-navbar-hidden');
        if (window.getComputedStyle(eleMainNavbar).getPropertyValue('position').match(/fixed|sticky/i)) {
            var mainNavBarHeight = eleMainNavbar.offsetHeight;
            eleNavbarHidden.style.height = mainNavBarHeight + 'px';
            eleNavbarHidden.classList.remove('d-none');
        } else {
            eleNavbarHidden.style.height = '0px';
            eleNavbarHidden.classList.add('d-none');
        }
    }
    currentMainNavbarHeight();
    window.addEventListener('load', (event) => {
        setTimeout(function(){
            currentMainNavbarHeight();
        }, 50);
    });
    window.addEventListener('resize', (event) => {
        setTimeout(function(){
            currentMainNavbarHeight();
        }, 50);
    });
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
    window.addEventListener('pagehide', function() {
        document.querySelectorAll('.page-is-loading').forEach(element => {
            element.classList.add('d-none');
        });
        document.querySelectorAll('.page-has-loaded').forEach(element => {
            element.classList.remove('d-none');
        });
    });
    document.querySelectorAll('a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
                        setTimeout(function() {
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
        document.querySelectorAll('.timestamp-to-date').forEach(function(element) {
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

    document.addEventListener('DOMContentLoaded', function() {
        convertTimestampToDate();
    });

    document.addEventListener('neutralFetchCompleted', function() {
        convertTimestampToDate();
    });
})();

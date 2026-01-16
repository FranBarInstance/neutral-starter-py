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
            eleNavbarHidden.setAttribute('style', 'height:' + mainNavBarHeight + 'px' );
        } else {
            eleNavbarHidden.setAttribute('style', 'height:0px');
            eleNavbarHidden.style.display = 'none';
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
                element.style.display = 'none';
            });
            document.querySelectorAll('.page-has-loaded').forEach(element => {
                element.style.display = 'block';
            });
        }, 250);
    });
    window.addEventListener('pagehide', function() {
        document.querySelectorAll('.page-is-loading').forEach(element => {
            element.style.display = 'none';
        });
        document.querySelectorAll('.page-has-loaded').forEach(element => {
            element.style.display = 'block';
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
                            el.style.display = 'none';
                        });
                        document.querySelectorAll('.page-is-loading').forEach(el => {
                            el.style.display = 'block';
                        });
                        setTimeout(function() {
                            document.querySelectorAll('.page-is-loading').forEach(el => {
                                el.style.display = 'none';
                            });
                            document.querySelectorAll('.page-has-loaded').forEach(el => {
                                el.style.display = 'block';
                            });
                        }, 12000);
                    }
                }
            }
        });
    });
})();

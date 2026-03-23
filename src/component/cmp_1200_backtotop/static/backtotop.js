/* Copyright (C) 2025-2026 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE) */
/**
 * Navbar Scroll & BackToTop Utility
 *
 * This version automatically manages the navbar's "fixed" state.
 * Increased scrollUpThreshold to prevent immediate showing on slight up-scrolling.
 */

(function() {
    'use strict';

    function getGlobalConfig() {
        const config = window.backToTopConfig;
        return config && typeof config === 'object' ? config : {};
    }

    class ScrollUtility {
        constructor() {
            const globalConfig = getGlobalConfig();
            const defaultConfig = {
                navbarSelector: '#main-navbar',
                navbarHiddenSelector: '#main-navbar-hidden', // Spacer element
                backToTopSelector: '#back-to-top',

                // Sensitivity & Thresholds
                hideThreshold: 50,
                scrollUpThreshold: 50,   // Higher threshold to avoid immediate showing
                backToTopThreshold: 250,
                peekHeight: 5,
                scrollToBehavior: 'smooth',

                // Feature Toggles
                hideDown: true,
                showUp: true,

                // CSS Classes
                classes: {
                    navbar: 'navbar',
                    hidden: 'navbar--hidden',
                    scrolled: 'navbar--scrolled',
                    atTop: 'navbar--at-top',
                    fixed: 'fixed-top'
                },

                // Transitions
                transitions: {
                    navbar: 'transform 0.25s cubic-bezier(0.165, 0.84, 0.44, 1), opacity 0.2s ease, background-color 0.25s ease',
                    backToTop: 'opacity 0.2s ease, transform 0.2s ease'
                }
            };
            this.config = {
                ...defaultConfig,
                ...globalConfig,
                classes: {
                    ...defaultConfig.classes,
                    ...(globalConfig.classes || {})
                },
                transitions: {
                    ...defaultConfig.transitions,
                    ...(globalConfig.transitions || {})
                }
            };

            this.lastScrollTop = 0;
            this.upScrollDistance = 0;
            this.ticking = false;
            this.isNavbarHidden = false;
            this.isAtTop = true;
            this.wasFixedInitially = false;

            this.navbar = document.querySelector(this.config.navbarSelector);
            this.navbarSpacer = document.querySelector(this.config.navbarHiddenSelector);
            this.backToTop = document.querySelector(this.config.backToTopSelector);

            this.init();
        }

        init() {
            if (!this.navbar && !this.backToTop) return;

            this.loadDatasetConfig();
            this.setupInitialStyles();

            window.addEventListener('scroll', () => this.onScroll(), { passive: true });

            if (this.backToTop) {
                this.backToTop.addEventListener('click', (e) => {
                    e.preventDefault();
                    window.scrollTo({ top: 0, behavior: this.config.scrollToBehavior });
                });
            }

            // Hover and Click to show navbar sliver
            if (this.navbar) {
                this.navbar.addEventListener('mouseenter', () => this.showNavbar());
                this.navbar.addEventListener('mousedown', () => this.showNavbar());
                this.navbar.addEventListener('touchstart', () => this.showNavbar(), { passive: true });
            }

            window.addEventListener('resize', () => {
                this.updateSpacer();
                this.forceShowNavbar();
                this.update();
            }, { passive: true });

            // Run initial check
            this.update();
        }

        loadDatasetConfig() {
            if (!this.navbar) return;
            const ds = this.navbar.dataset;
            if (ds.hideThreshold) this.config.hideThreshold = parseInt(ds.hideThreshold);
            if (ds.scrollUpThreshold) this.config.scrollUpThreshold = parseInt(ds.scrollUpThreshold);
            if (ds.peekHeight) this.config.peekHeight = parseInt(ds.peekHeight);
            if (ds.backToTopThreshold) this.config.backToTopThreshold = parseInt(ds.backToTopThreshold);
        }

        setupInitialStyles() {
            if (this.navbar) {
                this.wasFixedInitially = this.navbar.classList.contains(this.config.classes.fixed);
                this.navbar.style.transition = this.config.transitions.navbar;
                this.navbar.classList.add(this.config.classes.atTop);
                // Pre-calculate spacer height if needed
                this.updateSpacer();
            }
            if (this.backToTop) {
                this.backToTop.style.transition = this.config.transitions.backToTop;
                this.backToTop.style.opacity = '0';
            }
        }

        updateSpacer() {
            if (this.navbar && this.navbarSpacer) {
                // If it's fixed, the spacer should match its height to prevent layout jump
                if (this.navbar.classList.contains(this.config.classes.fixed)) {
                    this.navbarSpacer.style.height = this.navbar.offsetHeight + 'px';
                    this.navbarSpacer.style.display = 'block';
                } else {
                    this.navbarSpacer.style.height = '0px';
                    this.navbarSpacer.style.display = 'none';
                }
            }
        }

        onScroll() {
            if (!this.ticking) {
                window.requestAnimationFrame(() => {
                    this.update();
                    this.ticking = false;
                });
                this.ticking = true;
            }
        }

        update() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const delta = scrollTop - this.lastScrollTop;

            this.updateBackToTop(scrollTop);
            this.updateNavbar(scrollTop, delta);

            this.lastScrollTop = Math.max(0, scrollTop);
        }

        updateBackToTop(scrollTop) {
            if (!this.backToTop) return;
            if (scrollTop > this.config.backToTopThreshold) {
                this.backToTop.style.opacity = '1';
                this.backToTop.style.pointerEvents = 'auto';
                this.backToTop.style.transform = 'translateY(0)';
            } else {
                this.backToTop.style.opacity = '0';
                this.backToTop.style.pointerEvents = 'none';
                this.backToTop.style.transform = 'translateY(20px)';
            }
        }

        updateNavbar(scrollTop, delta) {
            if (!this.navbar) return;

            // At-top vs Scrolled states
            if (scrollTop > 10) {
                if (this.isAtTop) {
                    this.navbar.classList.add(this.config.classes.scrolled);
                    this.navbar.classList.remove(this.config.classes.atTop);

                    // Smart Fix: ensure navbar is fixed so it can "stay" while hidden
                    if (!this.navbar.classList.contains(this.config.classes.fixed)) {
                        this.navbar.classList.add(this.config.classes.fixed);
                        this.updateSpacer();
                    }
                    this.isAtTop = false;
                }
            } else {
                if (!this.isAtTop) {
                    this.navbar.classList.remove(this.config.classes.scrolled);
                    this.navbar.classList.add(this.config.classes.atTop);

                    // Revert Smart Fix if it wasn't initially fixed
                    if (!this.wasFixedInitially) {
                        this.navbar.classList.remove(this.config.classes.fixed);
                        this.updateSpacer();
                    }
                    this.isAtTop = true;
                    this.showNavbar();
                }
            }

            // Hide/Show Logic
            if (scrollTop < this.config.hideThreshold) {
                this.showNavbar();
                this.upScrollDistance = 0;
            } else {
                if (delta > 0) {
                    // Scrolling DOWN
                    if (this.config.hideDown && !this.isNavbarHidden) {
                        this.hideNavbar();
                    }
                    this.upScrollDistance = 0; // Reset up distance while scrolling down
                } else if (delta < 0) {
                    // Scrolling UP
                    this.upScrollDistance += Math.abs(delta);
                    if (this.config.showUp && this.upScrollDistance > this.config.scrollUpThreshold) {
                        this.showNavbar();
                        this.upScrollDistance = 0;
                    }
                }
            }
        }

        hideNavbar() {
            if (!this.isNavbarHidden) {
                this.navbar.classList.add(this.config.classes.hidden);
                this.navbar.style.transform = `translateY(calc(-100% + ${this.config.peekHeight}px))`;
                this.navbar.style.opacity = '0.9';
                this.isNavbarHidden = true;
            }
        }

        showNavbar() {
            if (this.isNavbarHidden || this.isAtTop) {
                this.navbar.classList.remove(this.config.classes.hidden);
                this.navbar.style.transform = 'translateY(0)';
                this.navbar.style.opacity = '1';
                this.isNavbarHidden = false;
            }
        }

        forceShowNavbar() {
            if (this.navbar) {
                this.navbar.classList.remove(this.config.classes.hidden);
                this.navbar.style.transform = 'translateY(0)';
                this.navbar.style.opacity = '1';
                this.isNavbarHidden = false;
                this.upScrollDistance = 0;
            }
        }
    }

    const initUtility = () => {
        window.scrollUtility = new ScrollUtility();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUtility);
    } else {
        initUtility();
    }

    window.addEventListener('neutralFetchCompleted', initUtility);

})();

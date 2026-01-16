
document.addEventListener('DOMContentLoaded', function() {
    let lastScrollTop = 0;
    let upScrollTop = 0;
    let upScrollMax = 15 * window.devicePixelRatio;
    let setOpacity = true;
    let oldOpacity = 1;
    let newOpacity = 0.3;
    let selOpacity = '.navbar';
    let classToggle = 'reduce-nav';

    const element = document.querySelector(selOpacity);
    if (element) {
        oldOpacity = window.getComputedStyle(element).opacity;
    }

    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        backToTop.style.display = 'none';

        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 100) {
                backToTop.style.display = 'block';
                backToTop.style.transition = 'opacity 200ms';
                backToTop.style.opacity = '1';
            } else {
                backToTop.style.opacity = '0';
                setTimeout(() => {
                    backToTop.style.display = 'none';
                }, 200);
            }

            if (setOpacity) {
                const startScroll = window.pageYOffset;
                const elements = document.querySelectorAll(selOpacity);

                if (startScroll > lastScrollTop) {
                    // Scrolling down
                    if (startScroll > 50) {
                        elements.forEach(el => {
                            if (!el.matches(':hover')) {
                                el.style.opacity = newOpacity;
                                el.classList.add(classToggle);
                            }
                        });
                        upScrollTop = 0;
                    }
                } else {
                    // Scrolling up
                    if (upScrollTop > upScrollMax || startScroll < 10) {
                        elements.forEach(el => {
                            el.style.opacity = oldOpacity;
                            el.classList.remove(classToggle);
                        });
                        upScrollTop = 0;
                    }
                    upScrollTop++;
                }
                lastScrollTop = startScroll;
            }
        });

        backToTop.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    if (setOpacity) {
        const elements = document.querySelectorAll(selOpacity);
        elements.forEach(el => {
            el.addEventListener('mouseover', function() {
                el.style.opacity = oldOpacity;
                el.classList.remove(classToggle);
            });

            el.addEventListener('mousedown', function() {
                el.style.opacity = oldOpacity;
                el.classList.remove(classToggle);
            });
        });
    }

    const links = document.querySelectorAll('a');
    const thisSite = window.location.origin;
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            if (link.href) {
                const href = link.getAttribute('href');
                if (href.substring(0, 1) === '/' ||
                    href.substring(0, 1) === '?' ||
                    href.substring(0, thisSite.length) === thisSite) {
                    if (link.getAttribute('target') !== '_blank') {
                        const selectorElements = document.querySelectorAll('.navbar');
                        selectorElements.forEach(el => {
                            el.style.opacity = '1';
                            el.classList.remove('reduce-nav');
                        });
                    }
                }
            }
        });
    });

    window.addEventListener('resize', function() {
        const selectorElements = document.querySelectorAll('.navbar');
        selectorElements.forEach(el => {
            el.style.opacity = '1';
            el.classList.remove('reduce-nav');
        });
    });


    setTimeout(function(){
        window.dispatchEvent(new Event('resize'));
    }, 10);
});

(function () {
    "use strict";

    var backdrop = null;
    var overlayImg = null;

    function getBackdrop() {
        if (!backdrop) {
            backdrop = document.createElement("div");
            backdrop.className = "img-zoom-backdrop";
            backdrop.addEventListener("click", closeAll);
            document.body.appendChild(backdrop);
        }
        return backdrop;
    }

    function getOverlayImg() {
        if (!overlayImg) {
            overlayImg = document.createElement("img");
            overlayImg.className = "img-zoom-overlay-img";
            document.body.appendChild(overlayImg);
        }
        return overlayImg;
    }

    function closeAll() {
        if (backdrop) backdrop.style.display = "none";
        if (overlayImg) {
            overlayImg.style.display = "none";
            overlayImg.src = "";
        }
        document.body.classList.remove("img-zoom-active");
    }

    function toggleImageZoom(e) {
        var el = e.target.closest(".img-zoomable");
        
        if (el) {
            // Determine zoom source URL
            var zoomSrc = el.dataset.zoomSrc || el.src;
            
            if (zoomSrc) {
                // Ensure everything is clean
                closeAll();
                
                // Show dynamic overlay components
                var bd = getBackdrop();
                var img = getOverlayImg();
                
                bd.style.display = "block";
                img.src = zoomSrc;
                img.style.display = "block";
                
                document.body.classList.add("img-zoom-active");

                e.preventDefault();
                e.stopPropagation();
            }
        } else {
            // Clicked elsewhere
            closeAll();
        }
    }

    function initImgZoom() {
        if (window._imgZoomInitialized) return;
        window._imgZoomInitialized = true;
        document.addEventListener("click", toggleImageZoom, true);
    }

    initImgZoom();
    window.addEventListener("neutralFetchCompleted", initImgZoom);
})();

(function () {
    "use strict";

    function updatePreviewContainer() {
        var container = document.querySelector(".album-image-edit-preview-container");
        var fieldDiv = document.querySelector(".album-image-field");

        if (!container || !fieldDiv) return;

        var selectedIds = String(fieldDiv.dataset.selectedIds || "").split(",").map(i => i.trim()).filter(Boolean);

        // Update the hidden ID input with all IDs comma-separated
        var idInput = document.querySelector('input[name="album-image-edit-image-id"]');
        if (idInput && idInput.value !== fieldDiv.dataset.selectedIds) {
            idInput.value = fieldDiv.dataset.selectedIds;
        }

        // Clean up previous dynamically added previews instead of full innerHTML destruction
        var existingPreviews = container.querySelectorAll(".album-image-edit-preview-item");
        existingPreviews.forEach(function (e) { e.remove(); });

        var emptyMessage = container.querySelector(".album-image-edit-preview-empty");

        if (selectedIds.length > 0) {
            container.classList.add("mb-3", "d-flex", "flex-wrap", "gap-2");
            if (emptyMessage) emptyMessage.classList.add("d-none");
        } else {
            container.classList.remove("mb-3", "d-flex", "flex-wrap", "gap-2");
            if (emptyMessage) emptyMessage.classList.remove("d-none");
        }

        selectedIds.forEach(function (id) {
            var btn = fieldDiv.querySelector('.album-image-field-thumb[data-image-id="' + id + '"]');
            var url = btn ? (btn.dataset.thumbUrl || btn.dataset.mediumUrl || btn.dataset.fullUrl) : "";

            if (!url) return;

            var wrapper = document.createElement("div");
            wrapper.className = "album-image-edit-preview-item album-image-preview-thumb position-relative d-inline-block border rounded p-1 bg-light shadow-sm";

            var img = document.createElement("img");
            img.src = url;
            img.className = "img-thumbnail p-0 border-0 img-zoomable";
            img.setAttribute("tabindex", "0");

            // Derive full image URL from thumb URL for zooming
            if (url.includes("/thumb")) {
                img.dataset.zoomSrc = url.replace("/thumb", "/full");
            }

            var removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "album-image-preview-remove btn btn-danger btn-sm rounded-circle position-absolute d-flex align-items-center justify-content-center p-0 shadow";
            removeBtn.innerHTML = "&times;";
            removeBtn.title = "Remove";

            removeBtn.addEventListener("click", function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (btn) {
                    btn.click(); // Trigger native deselection logic
                }
            });

            wrapper.appendChild(img);
            wrapper.appendChild(removeBtn);
            container.appendChild(wrapper);
        });
    }

    function initAlbumImageEdit() {
        if (window._albumImageEditInit) return;
        window._albumImageEditInit = true;

        var fieldDiv = document.querySelector(".album-image-field");
        if (fieldDiv) {
            // Watch for changes on the selected IDs dataset
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.attributeName === "data-selected-ids") {
                        updatePreviewContainer();
                    }
                });
            });
            observer.observe(fieldDiv, { attributes: true });

            // Listen for click inside field to handle potential delayed states
            fieldDiv.addEventListener("click", function(e) {
                if (e.target.closest(".album-image-field-thumb") || e.target.closest(".album-image-reset-button")) {
                    setTimeout(updatePreviewContainer, 50);
                }
            });

            // Initial render
            setTimeout(updatePreviewContainer, 200);
        }
    }

    document.addEventListener("DOMContentLoaded", initAlbumImageEdit);
    window.addEventListener("neutralFetchCompleted", function() {
        window._albumImageEditInit = false;
        initAlbumImageEdit();
    });
})();

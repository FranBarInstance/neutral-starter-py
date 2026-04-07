(function () {
    "use strict";

    function splitCsv(value) {
        return String(value || "")
            .split(",")
            .map(item => item.trim())
            .filter(Boolean);
    }

    function setFieldValues(fieldsToFill, values) {
        fieldsToFill.forEach(function (fieldClass, index) {
            var value = values[index] || "";
            document.querySelectorAll("." + fieldClass).forEach(function (target) {
                target.value = value;
                target.dispatchEvent(new Event("change", { bubbles: true }));
                target.dispatchEvent(new Event("input", { bubbles: true }));
            });
        });
    }

    function setPreview(targetClass, url) {
        if (!targetClass) {
            return;
        }
        document.querySelectorAll("img." + targetClass).forEach(function (target) {
            target.src = url || "";
            target.classList.toggle("d-none", !url);
        });
    }

    function showError(container, message) {
        var errorBox = container.querySelector(".album-image-field-error");
        if (!errorBox) {
            return;
        }
        if (!message) {
            errorBox.classList.add("d-none");
            errorBox.textContent = "";
            return;
        }
        errorBox.textContent = message;
        errorBox.classList.remove("d-none");
    }

    function readFilePreview(file) {
        return new Promise(function (resolve) {
            if (!file || !String(file.type || "").startsWith("image/")) {
                resolve("");
                return;
            }

            var reader = new FileReader();
            reader.onload = function (event) {
                resolve(event && event.target ? String(event.target.result || "") : "");
            };
            reader.onerror = function () {
                resolve("");
            };
            reader.readAsDataURL(file);
        });
    }

    function extractClipboardImageFiles(event) {
        var clipboard = event && event.clipboardData;
        if (!clipboard) {
            return [];
        }

        var files = [];

        Array.from(clipboard.items || []).forEach(function (item) {
            if (!item || item.kind !== "file") {
                return;
            }

            var file = item.getAsFile ? item.getAsFile() : null;
            if (file && String(file.type || "").startsWith("image/")) {
                files.push(file);
            }
        });

        if (files.length) {
            return files;
        }

        return Array.from(clipboard.files || []).filter(function (file) {
            return String(file.type || "").startsWith("image/");
        });
    }

    function focusDropzone(container) {
        var dropzone = container.querySelector(".album-image-dropzone");
        if (!dropzone || typeof dropzone.focus !== "function") {
            return;
        }

        window.requestAnimationFrame(function () {
            if (!document.body.contains(dropzone)) {
                return;
            }
            if (dropzone.offsetParent === null) {
                return;
            }
            dropzone.focus();
        });
    }

    function focusDropzonesWithin(root) {
        if (!root || typeof root.querySelectorAll !== "function") {
            return;
        }

        root.querySelectorAll(".album-image-field").forEach(focusDropzone);
    }

    function showPending(container, files) {
        var pendingGrid = container.querySelector(".album-image-field-pending-grid");
        var uploadButton = container.querySelector(".album-image-upload-button");
        var resetButton = container.querySelector(".album-image-reset-button");
        var maxImages = parseInt(container.dataset.maxImages || "1", 10);
        var pendingFiles = Array.from(files || []).slice(0, Math.max(1, maxImages));
        container._albumImagePendingFiles = pendingFiles;

        if (uploadButton) {
            uploadButton.disabled = pendingFiles.length === 0;
        }
        if (resetButton) {
            resetButton.disabled = pendingFiles.length === 0;
        }

        if (!pendingFiles.length) {
            if (pendingGrid) {
                pendingGrid.innerHTML = "";
                pendingGrid.classList.add("d-none");
            }
            return;
        }

        if (pendingGrid) {
            pendingGrid.classList.remove("d-none");
            pendingGrid.innerHTML = "";
            pendingFiles.forEach(function (file, index) {
                var col = document.createElement("div");
                col.className = "album-image-field-grid-item";

                var wrapper = document.createElement("div");
                wrapper.className = "album-image-field-pending-thumb border rounded bg-white shadow-sm overflow-hidden d-flex flex-column h-100";

                var imageArea = document.createElement("div");
                imageArea.className = "position-relative flex-grow-1";

                var image = document.createElement("img");
                image.alt = file.name || ("pending-image-" + index);
                image.className = "album-image-field-pending-preview d-none w-100";

                var placeholder = document.createElement("div");
                placeholder.className = "album-image-field-pending-placeholder d-flex align-items-center justify-content-center h-100";
                placeholder.textContent = "";

                var removeIconTemplate = container.querySelector(".album-image-field-remove-icon-template");
                var removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.className = "album-image-field-pending-remove btn btn-danger rounded-circle p-0 d-flex align-items-center justify-content-center shadow-sm";
                removeBtn.style.position = "absolute";
                removeBtn.style.top = "6px";
                removeBtn.style.left = "6px";
                removeBtn.style.width = "34px";
                removeBtn.style.height = "34px";
                removeBtn.style.zIndex = "30";
                removeBtn.style.fontSize = "1.5rem";
                removeBtn.title = "";
                if (removeIconTemplate) {
                    removeBtn.innerHTML = removeIconTemplate.innerHTML;
                } else {
                    removeBtn.textContent = "×";
                }

                removeBtn.addEventListener("click", function (e) {
                    e.stopPropagation();
                    showError(container, "");
                    var updated = (container._albumImagePendingFiles || [])
                        .filter(function (_, i) { return i !== index; });
                    showPending(container, updated);
                });

                var spinnerTemplate = container.querySelector(".album-image-field-spinner-template");
                var spinner = document.createElement("div");
                spinner.className = "album-image-field-thumb-spinner d-none position-absolute top-0 start-0 w-100 h-100 align-items-center justify-content-center bg-white bg-opacity-75";
                spinner.style.zIndex = "40";
                if (spinnerTemplate) {
                    spinner.innerHTML = spinnerTemplate.innerHTML;
                }

                imageArea.appendChild(image);
                imageArea.appendChild(placeholder);
                imageArea.appendChild(removeBtn);
                imageArea.appendChild(spinner);

                var footerArea = document.createElement("div");
                footerArea.className = "p-2 border-top text-center w-100";
                footerArea.style.backgroundColor = "#f8f9fa"; // Explicit light gray

                var name = document.createElement("div");
                name.className = "album-image-field-pending-name small text-truncate text-muted";
                name.textContent = file.name || "";

                footerArea.appendChild(name);

                wrapper.appendChild(imageArea);
                wrapper.appendChild(footerArea);
                col.appendChild(wrapper);
                pendingGrid.appendChild(col);

                readFilePreview(file).then(function (previewUrl) {
                    if (!pendingGrid.contains(col)) {
                        return;
                    }
                    if (previewUrl) {
                        image.src = previewUrl;
                        image.classList.remove("d-none");
                        placeholder.classList.add("d-none");
                        return;
                    }
                    image.removeAttribute("src");
                    image.classList.add("d-none");
                    placeholder.classList.remove("d-none");
                });
            });
        }
    }

    function renderThumbs(container, items, selectedIds, append) {
        var grid = container.querySelector(".album-image-field-grid");
        if (!grid) {
            return;
        }
        if (!append) {
            grid.innerHTML = "";
        }
        items.forEach(function (item) {
            var col = document.createElement("div");
            col.className = "album-image-field-grid-item";

            var button = document.createElement("button");
            button.type = "button";
            button.className = "album-image-field-thumb btn btn-light w-100 p-0";
            button.dataset.imageId = item.imageId;
            button.dataset.thumbUrl = item.thumbUrl || "";
            button.dataset.mediumUrl = item.mediumUrl || "";
            button.dataset.fullUrl = item.fullUrl || "";
            if (selectedIds.indexOf(item.imageId) !== -1) {
                button.classList.add("is-selected");
            }

            var image = document.createElement("img");
            image.src = item.thumbUrl || "";
            image.alt = item.albumCode || "image";
            button.appendChild(image);

            // Zoom icon (styled in CSS)
            var zoomBtn = document.createElement("span");
            zoomBtn.className = "img-zoomable mdi mdi-magnify-plus btn btn-primary rounded-circle position-absolute d-flex align-items-center justify-content-center p-0 shadow";
            zoomBtn.title = "View Full Resolution";
            zoomBtn.dataset.zoomSrc = item.fullUrl || "";
            button.appendChild(zoomBtn);

            // Selection indicator (simplified, toggled via JS)
            var selectBtn = document.createElement("span");
            var isSelected = selectedIds.indexOf(item.imageId) !== -1;
            selectBtn.className = "album-image-selection-icon mdi mdi-check btn rounded-circle position-absolute d-flex align-items-center justify-content-center p-0 shadow-sm border " + (isSelected ? "btn-success" : "btn-light");
            selectBtn.style.pointerEvents = "none";
            button.appendChild(selectBtn);

            col.appendChild(button);
            grid.appendChild(col);
        });
    }

    function renderAlbumOptions(container, albumCodes) {
        var select = container.querySelector(".album-image-field-album-select");
        if (!select) {
            return;
        }

        var existingPlaceholder = select.querySelector("option[value='']");
        var placeholderText = existingPlaceholder ? existingPlaceholder.textContent : "...";

        var optionValues = [];
        var fragment = document.createDocumentFragment();

        var placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = placeholderText;
        fragment.appendChild(placeholder);

        albumCodes.forEach(function (albumCode) {
            var normalized = String(albumCode || "").trim();
            if (!normalized || optionValues.indexOf(normalized) !== -1) {
                return;
            }
            optionValues.push(normalized);

            var option = document.createElement("option");
            option.value = normalized;
            option.textContent = normalized;
            fragment.appendChild(option);
        });

        select.innerHTML = "";
        select.appendChild(fragment);
    }

    function currentAlbum(container) {
        var forced = container.dataset.forceAlbum || "";
        if (forced) {
            return forced;
        }
        var input = container.querySelector(".album-image-field-album");
        return input ? String(input.value || "gallery").trim() : "gallery";
    }

    function listAlbums(container) {
        if (container.dataset.forceAlbum) {
            return Promise.resolve();
        }

        return fetch(container.dataset.albumsUrl, {
            headers: {
                "Requested-With-Ajax": "true"
            }
        })
            .then(function (response) { return response.json(); })
            .then(function (payload) {
                if (!payload.success) {
                    showError(container, payload.error || "");
                    return;
                }
                showError(container, "");
                renderAlbumOptions(container, payload.items || []);
            })
            .catch(function () {
                showError(container, "");
            });
    }

    function listImages(container, append) {
        var limit = parseInt(container.dataset.listLimit || container.dataset.limit || "50", 10);
        var offset = append ? parseInt(container.dataset.offset || "0", 10) : 0;

        var url = new URL(container.dataset.listUrl, window.location.origin);
        url.searchParams.set("album_code", currentAlbum(container));
        url.searchParams.set("limit", limit);
        url.searchParams.set("offset", offset);

        fetch(url.toString(), {
            headers: {
                "Requested-With-Ajax": "true"
            }
        })
            .then(function (response) { return response.json(); })
            .then(function (payload) {
                if (!payload.success) {
                    showError(container, payload.error || "");
                    return;
                }
                showError(container, "");
                var items = payload.items || [];
                renderThumbs(container, items, splitCsv(container.dataset.selectedIds), append);

                // Update offset for next batch
                var newOffset = offset + items.length;
                container.dataset.offset = String(newOffset);

                // Show/hide pagination button
                var pagination = container.querySelector(".album-image-field-pagination");
                if (pagination) {
                    if (items.length >= limit) {
                        pagination.classList.remove("d-none");
                    } else {
                        pagination.classList.add("d-none");
                    }
                }
            })
            .catch(function () {
                showError(container, "");
            });
    }

    function syncSelection(container, items) {
        var ids = items.map(function (item) { return item.imageId; });
        container.dataset.selectedIds = ids.join(",");
        setFieldValues(splitCsv(container.dataset.fieldsToFill), ids);
        setPreview(container.dataset.urlToFill || "", items[0] ? items[0].thumbUrl : "");
        listImages(container);
    }

    function uploadFiles(container, files) {
        var pendingFiles = Array.from(files || []);
        var uploadDelayMs = parseInt(container.dataset.uploadDelayMs || "100", 10);
        if (!pendingFiles.length) return;

        var uploadButton = container.querySelector(".album-image-upload-button");
        var resetButton = container.querySelector(".album-image-reset-button");
        var buttonSpinner = uploadButton ? uploadButton.querySelector(".album-image-upload-spinner") : null;

        if (uploadButton) uploadButton.disabled = true;
        if (resetButton) resetButton.disabled = true;
        if (buttonSpinner) buttonSpinner.classList.remove("d-none");

        var albumCode = currentAlbum(container);
        var currentItems = [];
        var currentIndex = pendingFiles.length - 1; // Start from the end to match original pop logic

        var uploadNext = function () {
            if (currentIndex < 0) {
                // All done
                if (uploadButton) uploadButton.disabled = false;
                if (buttonSpinner) buttonSpinner.classList.add("d-none");
                if (resetButton) resetButton.disabled = false;

                listAlbums(container);
                syncSelection(container, currentItems);

                // Clear the queue visually and internally at the very end
                container._albumImagePendingFiles = [];
                var pendingGrid = container.querySelector(".album-image-field-pending-grid");
                if (pendingGrid) {
                    pendingGrid.classList.add("d-none");
                    pendingGrid.innerHTML = "";
                }
                return;
            }

            var file = pendingFiles[currentIndex];
            var formData = new FormData();
            formData.append("images", file); // Backend expects list, but we send 1
            formData.append("album_code", albumCode);

            // Show spinner on the current thumbnail
            var pendingGridItems = container.querySelectorAll(".album-image-field-pending-grid .album-image-field-grid-item");
            var currentItemGrid = pendingGridItems[currentIndex];
            var spinner = null;
            if (currentItemGrid) {
                spinner = currentItemGrid.querySelector(".album-image-field-thumb-spinner");
                if (spinner) spinner.classList.remove("d-none");
            }

            fetch(container.dataset.uploadUrl, {
                method: "POST",
                headers: { "Requested-With-Ajax": "true" },
                body: formData
            })
                .then(function (response) { return response.json(); })
                .then(function (payload) {
                    if (!payload.success) {
                        showError(container, payload.error || "");
                        // Stop sequence on error and hide spinners to allow interaction
                        if (uploadButton) uploadButton.disabled = false;
                        if (resetButton) resetButton.disabled = false;
                        if (buttonSpinner) buttonSpinner.classList.add("d-none");
                        if (spinner) spinner.classList.add("d-none");
                        return;
                    }

                    // Success for this file!
                    currentItems = currentItems.concat(payload.items || []);

                    // Remove from pending state array properly
                    pendingFiles.splice(currentIndex, 1);
                    container._albumImagePendingFiles = pendingFiles;

                    // Remove from DOM without repainting the entire grid
                    if (currentItemGrid) {
                        currentItemGrid.remove();
                    }

                    currentIndex--;
                    window.setTimeout(uploadNext, uploadDelayMs);
                })
                .catch(function () {
                    showError(container, "");
                    if (uploadButton) uploadButton.disabled = false;
                    if (resetButton) resetButton.disabled = false;
                    if (buttonSpinner) buttonSpinner.classList.add("d-none");
                    if (spinner) spinner.classList.add("d-none");
                });
        };

        uploadNext();
    }

    function initField(container) {
        if (container.dataset.initialized === "true") {
            return;
        }
        container.dataset.initialized = "true";

        var dropzone = container.querySelector(".album-image-dropzone");
        var fileInput = container.querySelector(".album-image-field-input");
        var maxImages = parseInt(container.dataset.maxImages || "1", 10);
        var serial = Math.random().toString(36).substr(2, 6);

        var albumInput = container.querySelector(".album-image-field-album");
        if (albumInput) {
            var inputId = "album-input-" + serial;
            albumInput.id = inputId;
            var label = albumInput.nextElementSibling;
            if (label && label.tagName === "LABEL") {
                label.setAttribute("for", inputId);
            }
        }

        var albumSelect = container.querySelector(".album-image-field-album-select");
        if (albumSelect) {
            var selectId = "album-select-" + serial;
            albumSelect.id = selectId;
            var label = albumSelect.nextElementSibling;
            if (label && label.tagName === "LABEL") {
                label.setAttribute("for", selectId);
            }
        }

        if (dropzone && fileInput) {
            if (maxImages > 1) {
                fileInput.multiple = true;
            }
            if (!dropzone.hasAttribute("tabindex")) {
                dropzone.setAttribute("tabindex", "0");
            }
            if (!dropzone.hasAttribute("role")) {
                dropzone.setAttribute("role", "button");
            }
            dropzone.addEventListener("click", function () {
                dropzone.focus();
                fileInput.click();
            });

            fileInput.addEventListener("change", function () {
                showError(container, "");
                showPending(container, fileInput.files);
                fileInput.value = "";
            });

            ["dragenter", "dragover"].forEach(function (eventName) {
                dropzone.addEventListener(eventName, function (event) {
                    event.preventDefault();
                    dropzone.classList.add("is-dragover");
                });
            });

            ["dragleave", "dragend", "drop"].forEach(function (eventName) {
                dropzone.addEventListener(eventName, function (event) {
                    event.preventDefault();
                    dropzone.classList.remove("is-dragover");
                });
            });

            dropzone.addEventListener("drop", function (event) {
                showError(container, "");
                showPending(container, event.dataTransfer.files);
            });

            dropzone.addEventListener("paste", function (event) {
                var clipboardFiles = extractClipboardImageFiles(event);
                if (!clipboardFiles.length) {
                    return;
                }

                event.preventDefault();
                showError(container, "");
                showPending(container, clipboardFiles);
            });
        }

        var uploadButton = container.querySelector(".album-image-upload-button");
        var resetButton = container.querySelector(".album-image-reset-button");

        if (uploadButton) {
            uploadButton.addEventListener("click", function () {
                uploadFiles(container, container._albumImagePendingFiles || []);
            });
        }
        if (resetButton) {
            resetButton.addEventListener("click", function () {
                showPending(container, []);
            });
        }

        if (albumInput) {
            albumInput.addEventListener("change", function () {
                container.dataset.selectedIds = "";
                container.dataset.offset = "0";
                setFieldValues(splitCsv(container.dataset.fieldsToFill), []);
                setPreview(container.dataset.urlToFill || "", "");
                showPending(container, []);
                listImages(container);
            });

            if (albumSelect) {
                albumSelect.addEventListener("change", function () {
                    if (albumSelect.value) {
                        albumInput.value = albumSelect.value;
                        albumInput.dispatchEvent(new Event("change", { bubbles: true }));
                        albumSelect.value = "";
                    }
                });
            }
        }

        var loadMoreBtn = container.querySelector(".album-image-load-more");
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener("click", function () {
                listImages(container, true);
            });
        }

        container.addEventListener("click", function (event) {
            var button = event.target.closest(".album-image-field-thumb");
            if (!button) {
                return;
            }
            var imageId = button.dataset.imageId || "";
            var maxImages = parseInt(container.dataset.maxImages || "1", 10);
            var selectedIds = splitCsv(container.dataset.selectedIds);

            if (maxImages > 1) {
                var index = selectedIds.indexOf(imageId);
                if (index === -1) {
                    if (selectedIds.length < maxImages) {
                        selectedIds.push(imageId);
                    }
                } else {
                    selectedIds.splice(index, 1);
                }
            } else {
                if (selectedIds.indexOf(imageId) !== -1) {
                    selectedIds = [];
                } else {
                    selectedIds = [imageId];
                }
            }

            container.dataset.selectedIds = selectedIds.join(",");
            setFieldValues(splitCsv(container.dataset.fieldsToFill), selectedIds);

            container.querySelectorAll(".album-image-field-thumb").forEach(function (btn) {
                var isSelected = selectedIds.indexOf(btn.dataset.imageId) !== -1;
                btn.classList.toggle("is-selected", isSelected);
                var icon = btn.querySelector(".album-image-selection-icon");
                if (icon) {
                    icon.classList.toggle("btn-light", !isSelected);
                    icon.classList.toggle("btn-success", isSelected);
                }
            });

            // Preview the first selected image or clear if none
            var firstSelectedButton = container.querySelector(".album-image-field-thumb.is-selected");
            setPreview(container.dataset.urlToFill || "", firstSelectedButton ? firstSelectedButton.dataset.thumbUrl : "");
        });

        listAlbums(container).finally(function () {
            listImages(container);
        });

        focusDropzone(container);
    }

    function initAlbumImageFields() {
        document.querySelectorAll(".album-image-field").forEach(initField);
    }

    function initAlbumImageFieldVisibilityEvents() {
        if (window.__albumImageFieldVisibilityEventsInitialized) {
            return;
        }
        window.__albumImageFieldVisibilityEventsInitialized = true;

        ["shown.bs.collapse", "shown.bs.modal", "shown.bs.offcanvas", "shown.bs.tab"].forEach(function (eventName) {
            document.addEventListener(eventName, function (event) {
                focusDropzonesWithin(event.target);
            });
        });
    }

    initAlbumImageFieldVisibilityEvents();
    document.addEventListener("DOMContentLoaded", initAlbumImageFields);
    window.addEventListener("neutralFetchCompleted", initAlbumImageFields);
})();

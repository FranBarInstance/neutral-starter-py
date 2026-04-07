"""Core image storage and retrieval helpers."""

from __future__ import annotations

import io
import re
import time
import uuid
from dataclasses import dataclass
from urllib.parse import urlsplit

from PIL import Image as PilImage
from PIL import ImageOps, UnidentifiedImageError
from app.config import Config
from app.extensions import cache
from constants import DELETED
from core.model import Model
from core.user import User


@dataclass
class ProcessedImage:
    """Processed image variants and metadata."""

    thumb_img: bytes
    medium_img: bytes
    full_img: bytes
    thumb_width: int
    thumb_height: int
    medium_width: int
    medium_height: int
    full_width: int
    full_height: int
    thumb_bytes: int
    medium_bytes: int
    full_bytes: int


@dataclass
class ImageVariant:
    """Stored image variant payload and pixel dimensions."""

    data: bytes
    width: int
    height: int


class Image:
    """Business logic wrapper for image storage."""

    _ALBUM_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
    DEFAULT_ALBUM_CODES = ("gallery", "profile")
    LEGACY_DELETED_REASON = 1

    def __init__(
        self,
        db_url=Config.DB_IMAGE,
        db_type=Config.DB_IMAGE_TYPE,
        public_variant_base_url: str = "",
    ):
        self.model = Model(db_url, db_type)
        self.public_variant_base_url = str(public_variant_base_url or "").rstrip("/")

    def _result_rows_to_dicts(self, result) -> list[dict]:
        """Convert model SELECT result rows to dictionaries."""
        if not result or result.get("operation") != "SELECT":
            return []
        columns = list(result.get("columns", []))
        rows = result.get("rows", [])
        return [dict(zip(columns, row)) for row in rows]

    def _normalize_album_code(self, album_code: str | None) -> str:
        """Normalize and validate album code."""
        normalized = (album_code or "gallery").strip().lower().replace(" ", "-")
        if not self._ALBUM_RE.fullmatch(normalized):
            raise ValueError("Album code is invalid.")
        return normalized

    def _allowed_mime(self) -> set[str]:
        """Return allowed MIME set from config."""
        return {
            item.strip().lower()
            for item in Config.IMAGE_ALLOWED_MIME.split(",")
            if item.strip()
        }

    def _file_size(self, file_item) -> int:
        """Get uploaded file size without consuming the stream."""
        file_item.stream.seek(0, 2)
        size = file_item.stream.tell()
        file_item.stream.seek(0)
        return size

    def _validate_file(self, file_item, total_size: int) -> int:
        """Validate MIME and size limits for one file."""
        if not getattr(file_item, "filename", ""):
            raise ValueError("No image file was provided.")

        mimetype = (getattr(file_item, "mimetype", "") or "").strip().lower()
        if mimetype not in self._allowed_mime():
            raise ValueError(f"File type not allowed: {mimetype}")

        size = self._file_size(file_item)
        if size > Config.IMAGE_MAX_FILE_BYTES:
            raise ValueError(f"File too large: {size} bytes")
        if total_size + size > Config.IMAGE_MAX_UPLOAD_BYTES:
            raise ValueError("Total upload size exceeds configured limit.")
        return size

    def _variant_urls(self, image_id: str) -> dict:
        """Build public variant URLs for one image."""
        base = self.public_variant_base_url
        if not base:
            return {}
        return {
            "thumbUrl": f"{base}/{image_id}/thumb",
            "mediumUrl": f"{base}/{image_id}/medium",
            "fullUrl": f"{base}/{image_id}/full",
        }

    @staticmethod
    def _cache_path(link_or_path: str) -> str:
        """Normalize one public image link into a cache path prefix."""
        return urlsplit(str(link_or_path or "").strip()).path.rstrip("/")

    @staticmethod
    def _normalize_mode(image: PilImage.Image) -> PilImage.Image:
        """Normalize image mode preserving alpha when available."""
        has_alpha = image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        )
        return image.convert("RGBA" if has_alpha else "RGB")

    @staticmethod
    def _to_webp(img: PilImage.Image, quality: int) -> bytes:
        """Serialize image to WebP bytes."""
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality, method=6)
        return buffer.getvalue()

    def _process_image(self, data: bytes) -> ProcessedImage:
        """Build thumb, medium and full variants from raw image bytes."""
        try:
            image = PilImage.open(io.BytesIO(data))
            image = ImageOps.exif_transpose(image)
            image.load()
            image = self._normalize_mode(image)
        except UnidentifiedImageError as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc
        except OSError as exc:
            raise ValueError("Uploaded file could not be processed as an image.") from exc

        if (image.width * image.height) > Config.IMAGE_MAX_PIXELS:
            raise ValueError("Image dimensions exceed configured limits.")

        quality = max(0, min(int(Config.IMAGE_WEBP_QUALITY), 100))

        thumb = ImageOps.fit(
            image.copy(),
            (Config.IMAGE_THUMB_SIZE, Config.IMAGE_THUMB_SIZE),
            method=PilImage.Resampling.LANCZOS,
        )

        medium = image.copy()
        medium.thumbnail(
            (Config.IMAGE_MEDIUM_WIDTH, 99999),
            PilImage.Resampling.LANCZOS,
        )

        full = image.copy()
        full.thumbnail(
            (Config.IMAGE_FULL_WIDTH, 99999),
            PilImage.Resampling.LANCZOS,
        )

        thumb_bytes = self._to_webp(thumb, quality)
        medium_bytes = self._to_webp(medium, quality)
        full_bytes = self._to_webp(full, quality)

        return ProcessedImage(
            thumb_img=thumb_bytes,
            medium_img=medium_bytes,
            full_img=full_bytes,
            thumb_width=thumb.width,
            thumb_height=thumb.height,
            medium_width=medium.width,
            medium_height=medium.height,
            full_width=full.width,
            full_height=full.height,
            thumb_bytes=len(thumb_bytes),
            medium_bytes=len(medium_bytes),
            full_bytes=len(full_bytes),
        )

    def upload_images(
        self,
        files,
        profile_id: str,
        album_code: str = "gallery",
    ) -> list[dict]:
        """Upload and store one or many images."""
        if not profile_id:
            raise ValueError("Profile id is required.")

        normalized_album = self._normalize_album_code(album_code)

        # Check album image count
        results = self.model.exec(
            "image",
            "count-by-profileid-albumcode",
            {"profileId": profile_id, "albumCode": normalized_album}
        )
        current_count = results['rows'][0][0] if results and results['rows'] else 0
        if current_count + len(files) > Config.IMAGE_MAX_PER_ALBUM:
            raise ValueError(f"Full album (Max: {Config.IMAGE_MAX_PER_ALBUM})")

        # Check total albums count (if this is a new album)
        if normalized_album not in self.DEFAULT_ALBUM_CODES:
            album_codes = self.list_album_codes(profile_id)
            if normalized_album not in album_codes and len(album_codes) >= Config.IMAGE_MAX_ALBUMS:
                raise ValueError(f"Limit of albums reached (Max: {Config.IMAGE_MAX_ALBUMS})")

        uploaded_items = []
        total_size = 0

        for file_item in files:
            size = self._validate_file(file_item, total_size)
            total_size += size

            data = file_item.read()
            file_item.stream.seek(0)
            processed = self._process_image(data)
            image_id = str(uuid.uuid4())
            now = int(time.time())

            result = self.model.exec(
                "image",
                "insert",
                {
                    "imageId": image_id,
                    "profileId": profile_id,
                    "albumCode": normalized_album,
                    "thumbImg": processed.thumb_img,
                    "mediumImg": processed.medium_img,
                    "fullImg": processed.full_img,
                    "thumbWidth": processed.thumb_width,
                    "thumbHeight": processed.thumb_height,
                    "mediumWidth": processed.medium_width,
                    "mediumHeight": processed.medium_height,
                    "fullWidth": processed.full_width,
                    "fullHeight": processed.full_height,
                    "thumbBytes": processed.thumb_bytes,
                    "mediumBytes": processed.medium_bytes,
                    "fullBytes": processed.full_bytes,
                    "created": now,
                },
            )
            if not result or self.model.has_error:
                raise RuntimeError(self.model.last_error or "Image insert failed.")

            item = {
                "imageId": image_id,
                "profileId": profile_id,
                "albumCode": normalized_album,
                "created": now,
            }
            item.update(self._variant_urls(image_id))
            uploaded_items.append(item)

        if not uploaded_items:
            raise ValueError("No valid images were uploaded.")

        return uploaded_items

    def list_by_profile(
        self,
        profile_id: str,
        album_code: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """List metadata rows for one profile."""
        query = "list-by-profileid"
        params = {
            "profileId": profile_id,
            "limit": max(1, int(limit)),
            "offset": max(0, int(offset)),
        }
        if album_code:
            query = "list-by-profileid-albumcode"
            params["albumCode"] = self._normalize_album_code(album_code)

        rows = self._result_rows_to_dicts(self.model.exec("image", query, params))
        for row in rows:
            row.update(self._variant_urls(row["imageId"]))
        return rows

    def list_album_codes(self, profile_id: str) -> list[str]:
        """Return known album codes for one profile plus defaults."""
        rows = self._result_rows_to_dicts(
            self.model.exec(
                "image",
                "list-distinct-albumcodes-by-profileid",
                {"profileId": profile_id},
            )
        )
        album_codes = set(self.DEFAULT_ALBUM_CODES)
        for row in rows:
            album_code = row.get("albumCode")
            if album_code:
                album_codes.add(str(album_code))
        return sorted(album_codes)

    def get_meta(self, image_id: str) -> dict | None:
        """Return metadata for one image."""
        rows = self._result_rows_to_dicts(
            self.model.exec("image", "get-meta-by-imageid", {"imageId": image_id})
        )
        if not rows:
            return None
        row = rows[0]
        row.update(self._variant_urls(image_id))
        return row

    def get_variant(self, image_id: str, variant: str) -> ImageVariant | None:
        """Return one stored image variant with pixel dimensions."""
        variant_map = {
            "thumb": {
                "query": "get-thumb-by-imageid",
                "width": "thumbWidth",
                "height": "thumbHeight",
            },
            "medium": {
                "query": "get-medium-by-imageid",
                "width": "mediumWidth",
                "height": "mediumHeight",
            },
            "full": {
                "query": "get-full-by-imageid",
                "width": "fullWidth",
                "height": "fullHeight",
            },
        }
        variant_info = variant_map.get(variant)
        if not variant_info:
            return None

        result = self.model.exec("image", variant_info["query"], {"imageId": image_id})
        rows = result.get("rows", []) if result else []
        if not rows:
            return None

        meta = self.get_meta(image_id)
        if not meta:
            return None

        return ImageVariant(
            data=rows[0][0],
            width=int(meta[variant_info["width"]]),
            height=int(meta[variant_info["height"]]),
        )

    def get_public_variant(self, image_id: str, variant: str) -> ImageVariant | None:
        """Return one public image variant only when the owner profile is public."""
        meta = self.get_meta(image_id)
        if not meta:
            return None

        profile_id = str(meta.get("profileId") or "").strip()
        if not profile_id:
            return None

        if not User(Config.DB_PWA, Config.DB_PWA_TYPE).get_public_profile_by_profileid(profile_id):
            return None

        return self.get_variant(image_id, variant)

    def invalidate_public_username_cache(self, username: str, profile_image_link: str = "") -> None:
        """Invalidate one cached public profile image response by username."""
        profile_path = self._cache_path(profile_image_link)
        normalized = str(username or "").strip()
        if not profile_path or not normalized:
            return
        try:
            cache.delete(f"view/{profile_path}/{normalized}")
        except Exception:  # pragma: no cover - cache backend errors should not block app flows
            return

    def invalidate_all_public_profile_images_cache(
        self,
        profile_id: str,
        username: str = "",
        profile_image_link: str = "",
        variant_image_link: str = "",
    ) -> None:
        """Invalidate all cached public image responses for one profile."""
        normalized_profile_id = str(profile_id or "").strip()
        if not normalized_profile_id:
            return

        self.invalidate_public_username_cache(username, profile_image_link)

        variant_path = self._cache_path(variant_image_link)
        if not variant_path:
            return

        result = self.model.exec(
            "image",
            "list-by-profileid-all",
            {"profileId": normalized_profile_id, "limit": 10000, "offset": 0},
        )
        rows = self._result_rows_to_dicts(result)
        for row in rows:
            image_id = str(row.get("imageId") or "").strip()
            if not image_id:
                continue
            for variant in ("thumb", "medium", "full"):
                try:
                    cache.delete(f"view/{variant_path}/{image_id}/{variant}")
                except Exception:  # pragma: no cover - cache backend errors should not block app flows
                    continue

    def delete_image(self, image_id: str, profile_id: str | None = None) -> bool:
        """Disable one image by adding entry to image_disabled table."""
        meta = self.get_meta(image_id)
        if not meta:
            return False
        if profile_id and meta.get("profileId") != profile_id:
            return False

        # Check if already disabled
        disabled_rows = self.model.exec(
            "image",
            "admin-get-image-disabled-by-imageid",
            {"imageId": image_id}
        )
        if disabled_rows and disabled_rows.get("rows"):
            # Already disabled, nothing to do
            return True

        now = int(time.time())
        result = self.model.exec(
            "image",
            "upsert-image-disabled",
            {
                "reason": int(Config.DISABLED[DELETED]),
                "imageId": image_id,
                "description": "Deleted by user",
                "created": now,
                "modified": now,
            },
        )
        return bool(result and result.get("success"))

    def delete_by_profile(self, profile_id: str) -> bool:
        """Disable all images associated with a profile."""
        if not profile_id:
            return False

        # Get all images for this profile (including disabled ones)
        result = self.model.exec(
            "image",
            "list-by-profileid-all",
            {"profileId": profile_id, "limit": 10000, "offset": 0}
        )
        rows = self._result_rows_to_dicts(result)
        if not rows:
            return True

        now = int(time.time())
        success = True
        for row in rows:
            image_id = row.get("imageId")
            if not image_id:
                continue

            # Check if already disabled
            disabled_rows = self.model.exec(
                "image",
                "admin-get-image-disabled-by-imageid",
                {"imageId": image_id}
            )
            if disabled_rows and disabled_rows.get("rows"):
                continue

            disable_result = self.model.exec(
                "image",
                "upsert-image-disabled",
                {
                    "reason": int(Config.DISABLED[DELETED]),
                    "imageId": image_id,
                    "description": "Deleted by profile",
                    "created": now,
                    "modified": now,
                },
            )
            if not disable_result or not disable_result.get("success"):
                success = False

        return success

    def is_image_disabled(self, image_id: str) -> bool:
        """Check if an image is disabled."""
        result = self.model.exec(
            "image",
            "admin-get-image-disabled-by-imageid",
            {"imageId": image_id}
        )
        return bool(result and result.get("rows"))

    def admin_list_images(
        self,
        order_by: str = "created",
        search: str = "",
        disabled_reason: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """List images for admin views including disabled entries."""
        query_map = {
            "created": "admin-list-images-created",
            "disabled_created_date": "admin-list-images-disabled-created-date",
            "disabled_modified_date": "admin-list-images-disabled-modified-date",
        }
        query = query_map.get(order_by, "admin-list-images-created")
        search = str(search or "").strip()
        disabled_reason = str(disabled_reason or "").strip()
        target_limit = max(1, int(limit))
        current_offset = max(0, int(offset))
        deleted_reasons = {
            int(Config.DISABLED[DELETED]),
            self.LEGACY_DELETED_REASON,
        }
        visible_rows = []

        while len(visible_rows) < target_limit:
            result = self.model.exec(
                "image",
                query,
                {
                    "search": search,
                    "disabled_reason": disabled_reason,
                    "limit": target_limit,
                    "offset": current_offset,
                },
            )
            rows = self._result_rows_to_dicts(result)
            if not rows:
                break

            current_offset += len(rows)
            for row in rows:
                disabled_rows = self.model.exec(
                    "image",
                    "admin-get-image-disabled-by-imageid",
                    {"imageId": row.get("imageId")},
                )
                row["disabled"] = self._result_rows_to_dicts(disabled_rows)
                if any(int(item.get("reason")) in deleted_reasons for item in row["disabled"] if item.get("reason") is not None):
                    continue
                visible_rows.append(row)
                if len(visible_rows) >= target_limit:
                    break

            if len(rows) < target_limit:
                break

        return visible_rows

    def set_image_disabled(self, image_id: str, reason: int, description: str = "") -> bool:
        """Set one disabled reason for an image."""
        meta = self.model.exec("image", "get-meta-by-imageid", {"imageId": image_id})
        if not meta or not meta.get("rows"):
            # allow updates for already-disabled images that are not returned by get-meta-by-imageid
            check = self.model.exec("image", "admin-get-image-disabled-by-imageid", {"imageId": image_id})
            if not check or not check.get("rows"):
                return False

        now = int(time.time())
        result = self.model.exec(
            "image",
            "upsert-image-disabled",
            {
                "reason": int(reason),
                "imageId": image_id,
                "description": description,
                "created": now,
                "modified": now,
            },
        )
        return bool(result and result.get("success"))

    def delete_image_disabled(self, image_id: str, reason: int) -> bool:
        """Remove one disabled reason from an image."""
        result = self.model.exec(
            "image",
            "delete-image-disabled",
            {"reason": int(reason), "imageId": image_id},
        )
        return bool(result and result.get("success"))

    def restore_image(self, image_id: str, profile_id: str | None = None) -> bool:
        """Restore a disabled image by removing its entry from image_disabled."""
        meta = self.get_meta(image_id)
        if not meta:
            return False
        if profile_id and meta.get("profileId") != profile_id:
            return False

        success = True
        for reason in (self.LEGACY_DELETED_REASON, int(Config.DISABLED[DELETED])):
            result = self.model.exec(
                "image",
                "delete-image-disabled",
                {"reason": reason, "imageId": image_id}
            )
            success = success and bool(result and result.get("success"))
        return success

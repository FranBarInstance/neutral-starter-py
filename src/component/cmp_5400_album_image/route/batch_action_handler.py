"""Handler for batch action AJAX form."""

from core.request_handler_form import FormRequestHandler
from core.image import Image


class AlbumImageBatchActionFormHandler(FormRequestHandler):
    """Handler for batch action form."""

    def __init__(self, prepared_request, comp_route="", neutral_route=None, ltoken=None, form_name="album_image_batch_action"):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_profile_id(self):
        """Get the current user profile ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("profile", {}).get("id")

    def get(self) -> bool:
        """Handle GET request (visual form render or fallback load)."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def post(self) -> bool:
        """Handle POST request."""
        if not self.valid_form_tokens_post():
            return False
        if not self.valid_form_validation():
            return False

        profile_id = self._get_current_profile_id()
        if not profile_id:
            self.schema_data["form_result"] = {
                "status": "fail",
                "message": "Authentication required."
            }
            return False

        action = (self.schema_data["CONTEXT"]["POST"].get("action") or "").strip()
        target_album = (self.schema_data["CONTEXT"]["POST"].get("target_album") or "").strip()
        image_ids_str = (self.schema_data["CONTEXT"]["POST"].get("album-image-edit-image-id") or "").strip()
        
        if not image_ids_str:
            self.schema_data["form_result"] = {
                "status": "fail",
                "message": "No images selected."
            }
            return False

        image_ids = [i.strip() for i in image_ids_str.split(",") if i.strip()]
        img_helper = Image()
        
        success_count = 0
        for image_id in image_ids:
            meta = img_helper.get_meta(image_id)
            if not meta or meta.get("profileId") != profile_id:
                continue

            if action == "delete":
                if img_helper.delete_image(image_id=image_id, profile_id=profile_id):
                    success_count += 1
            elif action == "move":
                if not target_album:
                    continue
                try:
                    normalized = img_helper._normalize_album_code(target_album)  # pylint: disable=protected-access
                    img_helper.model.exec(
                        "image", 
                        "update-album", 
                        {"imageId": image_id, "albumCode": normalized}
                    )
                    success_count += 1
                except ValueError: # Invalid album code
                    continue

        if success_count == 0:
            self.schema_data["form_result"] = {
                "status": "fail",
                "message": "No operations could be completed."
            }
            return False

        self.schema_data["form_result"] = {
            "status": "success",
            "message": "Action completed successfully."
        }
        return True

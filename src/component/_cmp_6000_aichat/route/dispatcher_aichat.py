"""AI Chat dispatcher module."""

from ai_backend_0yt2sa import AIManager
from core.dispatcher import Dispatcher

from . import bp  # pylint: disable=no-name-in-module


class DispatcherAichat(Dispatcher):
    """Dispatcher with AI Chat business logic."""

    def _component_manifest(self, comp_uuid: str) -> dict:
        """Get manifest from schema_data by component UUID."""
        return self.schema_data.get(comp_uuid, {}).get("manifest", {})

    def get_ai_manager(self) -> AIManager:
        """Get or create AIManager instance from app config."""
        if not hasattr(bp, "ai_manager"):
            ai_config = self._component_manifest("ai_backend_0yt2sa").get("config", {})
            bp.ai_manager = AIManager(ai_config)
        return bp.ai_manager

    def get_default_profile(self) -> str:
        """Get the default profile from component manifest config."""
        comp_uuid = self.schema_data.get("CURRENT_COMP_UUID", "")
        return self._component_manifest(comp_uuid).get(
            "config", {}
        ).get("default_profile", "ollama_local")

    @staticmethod
    def build_prompt(user_message: str, history: list[dict]) -> str:
        """Build prompt from conversation history and current user message."""
        prompt_parts = []

        for message in history:
            role = message.get("role", "")
            content = message.get("content", "")
            if role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    def prompt_chat(self, profile: str, user_message: str, history: list[dict]) -> str:
        """Generate a chat response for the current profile and message."""
        full_prompt = self.build_prompt(user_message, history)
        return self.get_ai_manager().prompt(profile, full_prompt)

    def get_profiles(self) -> list[str]:
        """Get available AI profiles."""
        return list(self.get_ai_manager().profiles.keys())

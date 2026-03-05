"""Coding Practice & AI Guidance module router entrypoint."""

from modules.coding_practice_ai_guidance.backend.routes.practice import router as practice_router
from modules.coding_practice_ai_guidance.backend.routes.ai_mentor import router as ai_router

__all__ = ["practice_router", "ai_router"]

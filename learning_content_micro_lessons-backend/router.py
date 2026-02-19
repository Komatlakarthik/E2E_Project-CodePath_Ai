"""Learning Content & Micro-Lessons module router entrypoint."""

from modules.learning_content_micro_lessons.backend.routes.lessons import router as lessons_router

__all__ = ["lessons_router"]

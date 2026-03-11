"""Progress Tracking & Recommendation module router entrypoint."""

from modules.progress_tracking_recommendation.backend.routes.progress import router as progress_router

__all__ = ["progress_router"]

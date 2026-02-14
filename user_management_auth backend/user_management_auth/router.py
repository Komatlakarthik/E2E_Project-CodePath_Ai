"""User Management & Authentication module router entrypoint."""

from modules.user_management_auth.backend.routes.auth import router as auth_router

__all__ = ["auth_router"]

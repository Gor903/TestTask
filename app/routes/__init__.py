from .user_routes import router as user_router
from .event_routes import router as event_router

__all__ = [
    "user_router",
    "event_router",
]

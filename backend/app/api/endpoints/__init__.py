from .auth import router as auth_router
from .disasters import router as disasters_router
from .emergency_numbers import router as emergency_numbers_router
from .departments import router as departments_router
from .places import router as places_router

__all__ = ["auth_router", "disasters_router", "emergency_numbers_router", "departments_router", "places_router"]

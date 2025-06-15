from .admin_menu import router as admin_router
from .vip_menu import router as vip_router
from .free_menu import router as free_router
from .config_menu import router as config_router
from .subscription_plans import router as subscription_plans_router

__all__ = [
    "admin_router",
    "vip_router",
    "free_router",
    "config_router",
    "subscription_plans_router",
]

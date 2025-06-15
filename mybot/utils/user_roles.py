from .config import ADMIN_IDS, VIP_IDS


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id in ADMIN_IDS


def is_vip(user_id: int) -> bool:
    """Check if the user is a VIP subscriber."""
    return user_id in VIP_IDS

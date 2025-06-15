from aiogram import Bot
from .config import ADMIN_IDS, VIP_IDS, VIP_CHANNEL_ID
import os

DEFAULT_VIP_MULTIPLIER = int(os.environ.get("VIP_POINTS_MULTIPLIER", "2"))


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id in ADMIN_IDS


async def is_vip_member(bot: Bot, user_id: int) -> bool:
    """Check if the user currently belongs to the VIP channel or list."""
    if user_id in VIP_IDS:
        return True
    if not VIP_CHANNEL_ID:
        return False
    try:
        member = await bot.get_chat_member(VIP_CHANNEL_ID, user_id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False


async def get_points_multiplier(bot: Bot, user_id: int) -> int:
    """Return VIP multiplier for the user."""
    if await is_vip_member(bot, user_id):
        return DEFAULT_VIP_MULTIPLIER
    return 1


# Backwards compatibility
is_vip = is_vip_member

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from .config import ADMIN_IDS, VIP_IDS, VIP_CHANNEL_ID
from services.config_service import ConfigService
import os

DEFAULT_VIP_MULTIPLIER = int(os.environ.get("VIP_POINTS_MULTIPLIER", "2"))


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id in ADMIN_IDS


async def is_vip_member(bot: Bot, user_id: int, session: AsyncSession | None = None) -> bool:
    """Check if the user currently belongs to the VIP channel or list."""
    if user_id in VIP_IDS:
        return True
    vip_channel_id = VIP_CHANNEL_ID
    if session:
        value = await ConfigService(session).get_vip_channel_id()
        if value is not None:
            vip_channel_id = value
    if not vip_channel_id:
        return False
    try:
        member = await bot.get_chat_member(vip_channel_id, user_id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False


async def get_points_multiplier(bot: Bot, user_id: int, session: AsyncSession | None = None) -> int:
    """Return VIP multiplier for the user."""
    if await is_vip_member(bot, user_id, session=session):
        return DEFAULT_VIP_MULTIPLIER
    return 1


# Backwards compatibility
is_vip = is_vip_member

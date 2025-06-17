from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .config import ADMIN_IDS, VIP_IDS, VIP_CHANNEL_ID
import os
from datetime import datetime

DEFAULT_VIP_MULTIPLIER = int(os.environ.get("VIP_POINTS_MULTIPLIER", "2"))


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id in ADMIN_IDS


async def is_vip_member(bot: Bot, user_id: int, session: AsyncSession | None = None) -> bool:
    """Check if the user should be considered a VIP."""
    from services.config_service import ConfigService
    from database.models import VipSubscription

    if user_id in VIP_IDS:
        return True

    has_subscription = False
    vip_channel_id = VIP_CHANNEL_ID

    if session:
        # Check stored VIP channel configuration
        value = await ConfigService(session).get_vip_channel_id()
        if value is not None:
            vip_channel_id = value

        # Verify the user has an active VIP subscription
        stmt = select(VipSubscription).where(VipSubscription.user_id == user_id)
        result = await session.execute(stmt)
        sub = result.scalar_one_or_none()
        if sub and (sub.expires_at is None or sub.expires_at > datetime.utcnow()):
            has_subscription = True

    if has_subscription:
        return True

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

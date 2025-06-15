from aiogram import Bot
from .config import ADMIN_IDS, VIP_CHANNEL_ID


def is_admin(user_id: int) -> bool:
    """Check if the user is an admin."""
    return user_id in ADMIN_IDS


async def is_vip(bot: Bot, user_id: int) -> bool:
    """Check if the user is subscribed to the VIP channel."""
    if not VIP_CHANNEL_ID:
        return False
    try:
        member = await bot.get_chat_member(VIP_CHANNEL_ID, user_id)
        return member.status in {"member", "administrator", "creator"}
    except Exception:
        return False

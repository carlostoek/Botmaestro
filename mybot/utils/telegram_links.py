from aiogram import Bot
from .config import VIP_CHANNEL_ID

async def create_invite_link(bot: Bot) -> str:
    """Generate a non-expiring invite link for the VIP channel."""
    return await bot.export_chat_invite_link(VIP_CHANNEL_ID)

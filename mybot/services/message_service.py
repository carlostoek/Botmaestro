from __future__ import annotations

from aiogram import Bot
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from .config_service import ConfigService
from database.models import ButtonReaction
from keyboards.common import get_interactive_post_kb


class MessageService:
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

    async def send_interactive_post(
        self,
        text: str,
        channel_type: str = "vip",
    ) -> Message | None:
        """Send a message with interactive buttons to the configured channel."""
        config = ConfigService(self.session)
        if channel_type.lower() == "vip":
            channel_id = await config.get_vip_channel_id()
        else:
            channel_id = await config.get_free_channel_id()
        if not channel_id:
            return None

        sent = await self.bot.send_message(
            channel_id, text, reply_markup=get_interactive_post_kb(0)
        )
        await self.bot.edit_message_reply_markup(
            channel_id, sent.message_id, reply_markup=get_interactive_post_kb(sent.message_id)
        )
        return sent

    async def register_reaction(
        self, user_id: int, message_id: int, reaction_type: str
    ) -> ButtonReaction:
        reaction = ButtonReaction(
            message_id=message_id,
            user_id=user_id,
            reaction_type=reaction_type,
        )
        self.session.add(reaction)
        await self.session.commit()
        await self.session.refresh(reaction)
        return reaction

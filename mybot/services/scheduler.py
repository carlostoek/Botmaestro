import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select

from database.models import PendingChannelRequest, BotConfig


async def channel_request_scheduler(bot: Bot, session_factory: async_sessionmaker[AsyncSession]):
    while True:
        async with session_factory() as session:
            config = await session.get(BotConfig, 1)
            wait_minutes = config.free_channel_wait_time_minutes if config else 0
            threshold = datetime.utcnow() - timedelta(minutes=wait_minutes)
            stmt = select(PendingChannelRequest).where(
                PendingChannelRequest.approved == False,
                PendingChannelRequest.request_timestamp <= threshold,
            )
            result = await session.execute(stmt)
            requests = result.scalars().all()
            for req in requests:
                try:
                    await bot.approve_chat_join_request(req.chat_id, req.user_id)
                    await bot.send_message(req.user_id, "Tu solicitud de acceso ha sido aprobada.")
                    await session.delete(req)
                except Exception:
                    pass
            await session.commit()
        await asyncio.sleep(30)

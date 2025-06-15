import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select

from database.models import PendingChannelRequest, BotConfig, User
from utils.config import VIP_CHANNEL_ID


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


async def vip_subscription_scheduler(bot: Bot, session_factory: async_sessionmaker[AsyncSession]):
    while True:
        async with session_factory() as session:
            now = datetime.utcnow()
            remind_threshold = now + timedelta(hours=24)
            stmt = select(User).where(
                User.role == "vip",
                User.vip_expires_at <= remind_threshold,
                User.vip_expires_at > now,
                (User.last_reminder_sent_at.is_(None))
                | (User.last_reminder_sent_at <= now - timedelta(hours=24)),
            )
            result = await session.execute(stmt)
            users = result.scalars().all()
            for user in users:
                try:
                    await bot.send_message(user.id, "Tu suscripción VIP expira pronto.")
                    user.last_reminder_sent_at = now
                except Exception:
                    pass

            stmt = select(User).where(
                User.role == "vip",
                User.vip_expires_at.is_not(None),
                User.vip_expires_at <= now,
            )
            result = await session.execute(stmt)
            expired_users = result.scalars().all()
            for user in expired_users:
                try:
                    if VIP_CHANNEL_ID:
                        await bot.kick_chat_member(VIP_CHANNEL_ID, user.id)
                except Exception:
                    pass
                user.role = "free"
                await bot.send_message(user.id, "Tu suscripción VIP ha expirado.")
            await session.commit()
        await asyncio.sleep(3600)

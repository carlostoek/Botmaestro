from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from services.token_service import validate_token
from services.subscription_service import SubscriptionService
from database.models import User
from utils.config import VIP_CHANNEL_ID as CONFIG_VIP_CHANNEL_ID
from services.achievement_service import AchievementService

router = Router()

# Placeholder channel ID. Replace with actual value if not provided via config
VIP_CHANNEL_ID = CONFIG_VIP_CHANNEL_ID


def _duration_to_timedelta(duration: int | str) -> timedelta:
    mapping = {
        "1_month": 30,
        "3_months": 90,
        "6_months": 180,
        "1_year": 365,
    }
    if isinstance(duration, int):
        return timedelta(days=duration)
    if duration in mapping:
        return timedelta(days=mapping[duration])
    if duration.endswith("_days") and duration[:-5].isdigit():
        return timedelta(days=int(duration[:-5]))
    return timedelta(days=30)


@router.message(CommandStart(deep_link=True))
async def activate_vip(message: Message, session: AsyncSession, bot: Bot):
    parts = message.text.split(maxsplit=1)
    token = parts[1] if len(parts) > 1 else None
    if not token:
        return

    subscription_duration = await validate_token(token, session)
    if not subscription_duration:
        await message.answer("Token inválido o ya utilizado.")
        return

    user = await session.get(User, message.from_user.id)
    if not user:
        user = User(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        session.add(user)
    user.role = "vip"

    delta = _duration_to_timedelta(subscription_duration)
    vip_expires_at = datetime.utcnow() + delta
    user.vip_expires_at = vip_expires_at

    sub_service = SubscriptionService(session)
    existing = await sub_service.get_subscription(user.id)
    if existing:
        existing.expires_at = vip_expires_at
    else:
        await sub_service.create_subscription(user.id, vip_expires_at)
    await session.commit()
    ach_service = AchievementService(session)
    await ach_service.check_vip_achievement(user.id, bot=bot)

    invite_link = None
    if VIP_CHANNEL_ID:
        try:
            link = await bot.create_chat_invite_link(VIP_CHANNEL_ID, member_limit=1)
            invite_link = link.invite_link
        except Exception:
            invite_link = None

    if invite_link:
        await message.answer(
            f"¡Tu suscripción VIP está activa! Únete aquí: {invite_link}"
        )
    else:
        await message.answer("¡Tu suscripción VIP está activa!")

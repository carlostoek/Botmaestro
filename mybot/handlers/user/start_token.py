from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters.command import CommandObject
from datetime import datetime, timedelta

from services import SubscriptionService, SubscriptionPlanService, TokenService

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_token(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    token = command.args
    if not token:
        return
    token_service = TokenService(session)
    plan_token = await token_service.redeem_subscription_token(token, message.from_user.id)
    if not plan_token:
        await message.answer("Token inválido o ya utilizado.")
        return

    plan_service = SubscriptionPlanService(session)
    plan = await plan_service.get_plan_by_id(plan_token.plan_id)
    if not plan:
        await message.answer("Plan no encontrado.")
        return

    sub_service = SubscriptionService(session)
    expires_at = datetime.utcnow() + timedelta(days=plan.duration_days)
    await sub_service.create_subscription(message.from_user.id, expires_at)
    await message.answer("Suscripción activada correctamente!")

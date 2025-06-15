from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.vip_kb import get_vip_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member
from services import SubscriptionService, SubscriptionPlanService

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    token = args[1] if len(args) > 1 else None

    if token:
        plan_service = SubscriptionPlanService(session)
        sub_service = SubscriptionService(session)
        plan = await plan_service.use_plan(token, user_id)
        if plan:
            expires_at = datetime.utcnow() + timedelta(days=plan.duration_days)
            await sub_service.create_subscription(user_id, expires_at)
            await message.answer("Suscripción activada correctamente!")
        else:
            await message.answer("Token inválido o ya utilizado.")

    if is_admin(user_id):
        await message.answer(
            "Bienvenido, administrador!",
            reply_markup=get_admin_main_kb(),
        )
    elif await is_vip_member(bot, user_id):
        await message.answer(
            "Bienvenido, suscriptor VIP!",
            reply_markup=get_vip_kb(),
        )
    else:
        await message.answer(
            "Bienvenido al canal free!",
            reply_markup=get_subscription_kb(),
        )

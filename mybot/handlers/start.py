from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_main_kb import get_admin_main_kb
from keyboards.vip_kb import get_vip_kb
from keyboards.subscription_kb import get_subscription_kb
from utils.user_roles import is_admin, is_vip_member
from services import TokenService, SubscriptionService
from utils.telegram_links import create_invite_link

router = Router()


@router.message(CommandStart(deep_link=True))
async def cmd_start(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    args = message.get_args()
    if args:
        service = TokenService(session)
        plan = await service.validate_token(args)
        if plan:
            sub_service = SubscriptionService(session)
            await sub_service.add_subscription(user_id, plan.duration_days)
            await service.mark_token_as_used(args)
            link = await create_invite_link(message.bot)
            await message.answer(
                f"Suscripción {plan.name} activada. Aquí tienes tu enlace: {link}"
            )
            return

    if is_admin(user_id):
        await message.answer(
            "Bienvenido, administrador!",
            reply_markup=get_admin_main_kb(),
        )
    elif await is_vip_member(message.bot, user_id):
        await message.answer(
            "Bienvenido, suscriptor VIP!",
            reply_markup=get_vip_kb(),
        )
    else:
        await message.answer(
            "Para acceder al canal VIP necesitas una suscripción.",
            reply_markup=get_subscription_kb(),
        )

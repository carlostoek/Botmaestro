from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from services import TokenService, SubscriptionService
from utils.telegram_links import create_invite_link

router = Router()

@router.message(CommandStart(deep_link=True))
async def start_with_token(message: Message, session: AsyncSession):
    args = message.get_args()
    if not args:
        return
    service = TokenService(session)
    plan = await service.validate_token(args)
    if not plan:
        return
    sub_service = SubscriptionService(session)
    await sub_service.add_subscription(message.from_user.id, plan.duration_days)
    await service.mark_token_as_used(args)
    link = await create_invite_link(message.bot)
    await message.answer(
        f"Suscripción {plan.name} activada. Aquí tienes tu enlace: {link}"
    )

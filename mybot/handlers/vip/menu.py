from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command

from datetime import datetime

from keyboards.vip_kb import get_vip_kb
from utils.user_roles import is_vip_member
from utils.keyboard_utils import get_back_keyboard, get_main_menu_keyboard
from utils.messages import BOT_MESSAGES
from utils.message_utils import get_profile_message
from services.subscription_service import SubscriptionService
from services.mission_service import MissionService
from database.models import User, set_user_menu_state
from utils.text_utils import sanitize_text

router = Router()


@router.message(Command("vip_menu"))
async def vip_menu(message: Message, session: AsyncSession):
    if not await is_vip_member(message.bot, message.from_user.id, session=session):
        return
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_subscription(message.from_user.id)
    status = "Activa" if sub else "Sin registro"
    await message.answer(
        f"Suscripción VIP: {status}", reply_markup=get_vip_kb()
    )


@router.callback_query(F.data == "vip_subscription")
async def vip_subscription(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id, session=session):
        return await callback.answer()
    sub_service = SubscriptionService(session)
    sub = await sub_service.get_subscription(callback.from_user.id)
    if not sub:
        text = "No registrada"
    elif sub.expires_at:
        text = f"Válida hasta {sub.expires_at:%d/%m/%Y}"
    else:
        text = "Válida sin fecha de expiración"
    await callback.message.edit_text(text, reply_markup=get_vip_kb())
    await callback.answer()


@router.callback_query(F.data == "vip_game")
async def vip_game(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id, session=session):
        return await callback.answer()
    await callback.message.edit_text(
        BOT_MESSAGES["start_welcome_returning_user"],
        reply_markup=get_main_menu_keyboard(),
    )
    await set_user_menu_state(session, callback.from_user.id, "root")
    await callback.answer()


@router.callback_query(F.data == "game_profile")
async def game_profile(callback: CallbackQuery, session: AsyncSession):
    if not await is_vip_member(callback.bot, callback.from_user.id, session=session):
        return await callback.answer()

    user_id = callback.from_user.id
    user: User | None = await session.get(User, user_id)
    if not user:
        user = User(
            id=user_id,
            username=sanitize_text(callback.from_user.username),
            first_name=sanitize_text(callback.from_user.first_name),
            last_name=sanitize_text(callback.from_user.last_name),
        )
        session.add(user)
        await session.commit()

    mission_service = MissionService(session)
    active_missions = await mission_service.get_active_missions(user_id=user_id)

    profile_message = await get_profile_message(user, active_missions, session)

    sub_service = SubscriptionService(session)
    sub = await sub_service.get_subscription(user_id)
    is_active = sub and (sub.expires_at is None or sub.expires_at > datetime.utcnow())
    vip_status = "Activo" if is_active else "Expirado"

    profile_message += f"\n\nVIP: {vip_status}"

    await callback.message.edit_text(
        profile_message, reply_markup=get_back_keyboard("vip_game")
    )
    await callback.answer()


@router.callback_query(F.data == "gain_points")
async def gain_points(callback: CallbackQuery, session: AsyncSession):
    """Show information on how to earn points in the game."""
    if not await is_vip_member(callback.bot, callback.from_user.id, session=session):
        return await callback.answer()

    await callback.message.edit_text(
        BOT_MESSAGES.get(
            "gain_points_instructions",
            "Participa en misiones y actividades para ganar puntos."
        ),
        reply_markup=get_back_keyboard("vip_game")
    )
    await callback.answer()


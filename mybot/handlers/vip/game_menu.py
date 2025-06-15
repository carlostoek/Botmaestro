from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from services.mission_service import MissionService
from utils.message_utils import get_profile_message
from keyboards.vip_game_kb import get_game_menu_kb, get_profile_kb
from utils.navigation import return_to_parent_menu

router = Router()

@router.callback_query(F.data == "game_menu")
async def show_game_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Elige una opción:",
        reply_markup=get_game_menu_kb(include_back=True),
    )
    await callback.answer()


@router.callback_query(F.data == "game_profile")
async def show_game_profile(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    user = await session.get(User, user_id)
    if not user:
        await callback.answer("Debes iniciar con /start", show_alert=True)
        return
    mission_service = MissionService(session)
    active_missions = await mission_service.get_active_missions(user_id=user_id)
    text = await get_profile_message(user, active_missions)
    await callback.message.edit_text(text, reply_markup=get_profile_kb())
    await callback.answer()


@router.callback_query(F.data == "game_back")
async def handle_game_back(callback: CallbackQuery):
    await return_to_parent_menu(callback.message, callback.bot, callback.from_user.id)
    await callback.answer()

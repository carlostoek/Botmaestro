from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.vip_game_kb import (
    get_vip_game_menu_kb,
    get_vip_profile_kb,
)
from utils.user_roles import is_vip
from services.point_service import add_points, get_user_points
from services.level_service import get_user_level, check_for_level_up

router = Router()

# Apply VIP filter at router level
router.message.filter(lambda m: is_vip(m.from_user.id))
router.callback_query.filter(lambda c: is_vip(c.from_user.id))


@router.message(Command("game_menu"))
async def game_menu(message: Message):
    await message.answer("\U0001F3AE Menú de juego VIP", reply_markup=get_vip_game_menu_kb())


@router.callback_query(F.data == "vip_game_menu")
async def callback_game_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "\U0001F3AE Menú de juego VIP",
        reply_markup=get_vip_game_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "vip_gain_points")
async def callback_gain_points(callback: CallbackQuery):
    user_id = callback.from_user.id
    points = add_points(user_id, 10)
    leveled_up, level = check_for_level_up(user_id)
    text = f"Sumaste 10 puntos. Total: {points}."
    if leveled_up:
        text += f"\n\n✨ ¡Felicidades! Nivel {level}."
    await callback.answer(text, show_alert=True)


@router.callback_query(F.data == "vip_profile")
async def callback_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    points = get_user_points(user_id)
    level = get_user_level(user_id)
    profile_text = (
        "\U0001F4C8 Perfil VIP\n\n"
        f"Puntos: {points}\nNivel: {level}"
    )
    await callback.message.edit_text(profile_text, reply_markup=get_vip_profile_kb())
    await callback.answer()

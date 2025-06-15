from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.vip_game_kb import get_game_menu_kb
from services.point_service import PointService
from services.level_service import LevelService
from services.achievement_service import AchievementService, ACHIEVEMENTS
from utils.user_roles import is_vip

router = Router()
# Apply VIP filter so only VIP subscribers trigger these handlers

async def _check_vip_message(message: Message) -> bool:
    return await is_vip(message.bot, message.from_user.id)

async def _check_vip_callback(callback: CallbackQuery) -> bool:
    return await is_vip(callback.bot, callback.from_user.id)

router.message.filter(_check_vip_message)
router.callback_query.filter(_check_vip_callback)

_points = PointService()
_levels = LevelService()
_achievements = AchievementService()


@router.message(Command("game_menu"))
async def show_game_menu(message: Message) -> None:
    await message.answer("Menú de gamificación", reply_markup=get_game_menu_kb())


@router.callback_query(F.data == "gain_points")
async def gain_points(callback: CallbackQuery) -> None:
    user = _points.add_points(callback.from_user.id, 10)
    leveled = _levels.check_for_level_up(user)
    if leveled and user["level"] == 2:
        _achievements.grant_achievement(callback.from_user.id, "first_points")
    text = f"Tienes {user['points']} puntos"
    if leveled:
        text += f"\n¡Subiste al nivel {user['level']}!"
    await callback.answer(text, show_alert=True)


@router.callback_query(F.data == "game_profile")
async def show_profile(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    points = _points.get_user_points(user_id)
    level = _levels.get_user_level(user_id)
    achievements = _achievements.get_user_achievements(user_id)
    ach_text = ", ".join(ACHIEVEMENTS[a]["name"] for a in achievements) if achievements else "Sin logros"
    text = f"Puntos: {points}\nNivel: {level}\nLogros: {ach_text}"
    await callback.message.answer(text)
    await callback.answer()

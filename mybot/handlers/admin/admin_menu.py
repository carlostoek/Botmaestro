from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_main_kb import get_admin_main_kb
from utils.user_roles import is_admin
from utils.keyboard_utils import get_main_menu_keyboard, get_admin_main_keyboard
from utils.messages import BOT_MESSAGES
from utils.menu_utils import send_menu, update_menu
from database.models import get_user_menu_state

from .vip_menu import router as vip_router
from .free_menu import router as free_router
from .config_menu import router as config_router
from .tarifas_menu import router as tarifas_router
from handlers.vip.gamification import router as game_router

router = Router()
router.include_router(vip_router)
router.include_router(free_router)
router.include_router(config_router)
router.include_router(tarifas_router)
router.include_router(game_router)


@router.message(CommandStart())
async def admin_start(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await send_menu(message, "Men\u00fa de administraci\u00f3n", get_admin_main_kb(), session, "admin_main")


@router.message(Command("admin_menu"))
async def admin_menu(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    await send_menu(message, "Men\u00fa de administraci\u00f3n", get_admin_main_kb(), session, "admin_main")


@router.callback_query(F.data == "admin_game")
async def admin_game_entry(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Bienvenido al panel de administración, Diana.",
        get_admin_main_keyboard(),
        session,
        "admin_main",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    # Only one level deep currently; go back to main menu
    await update_menu(callback, "Men\u00fa de administraci\u00f3n", get_admin_main_kb(), session, "admin_main")
    await callback.answer()

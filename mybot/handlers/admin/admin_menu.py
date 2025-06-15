from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.admin_main_kb import get_admin_main_kb
from utils.user_roles import is_admin
from utils.keyboard_utils import (
    get_main_menu_keyboard,
    get_admin_main_keyboard,
    get_admin_manage_users_keyboard,
    get_admin_manage_content_keyboard,
)
from keyboards.common import get_back_kb
from keyboards.admin_vip_config_kb import get_tariff_select_kb
from database.models import Tariff, Token
from uuid import uuid4
from sqlalchemy import select
from utils.messages import BOT_MESSAGES
from utils.menu_utils import send_menu, update_menu
from database.models import get_user_menu_state

from .vip_menu import router as vip_router
from .free_menu import router as free_router
from .config_menu import router as config_router
from .subscription_plans import router as subscription_plans_router
from handlers.vip.gamification import router as game_router

router = Router()
router.include_router(vip_router)
router.include_router(free_router)
router.include_router(config_router)
router.include_router(subscription_plans_router)
router.include_router(game_router)


@router.message(Command("admin_generate_token"))
async def admin_generate_token_cmd(message: Message, session: AsyncSession, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    result = await session.execute(select(Tariff))
    tariffs = result.scalars().all()
    await message.answer(
        "Elige la tarifa para generar token:",
        reply_markup=get_tariff_select_kb(tariffs),
    )


@router.callback_query(F.data.startswith("generate_token_"))
async def generate_token_callback(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    tariff_id = int(callback.data.split("_")[-1])
    token_string = str(uuid4())
    token = Token(token_string=token_string, tariff_id=tariff_id)
    session.add(token)
    await session.commit()
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={token_string}"
    await callback.message.edit_text(f"Enlace generado: {link}")
    await callback.answer()


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


@router.callback_query(F.data == "admin_manage_users")
async def admin_manage_users(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Gesti\u00f3n de usuarios",
        get_admin_manage_users_keyboard(),
        session,
        "admin_manage_users",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_manage_content")
async def admin_manage_content(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Gestionar Contenido / Juego",
        get_admin_manage_content_keyboard(),
        session,
        "admin_manage_content",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_manage_events_sorteos")
async def admin_manage_events(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Gesti\u00f3n de eventos y sorteos en desarrollo.",
        get_back_kb("admin_main_menu"),
        session,
        "admin_manage_events_sorteos",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_bot_config")
async def admin_bot_config(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Configuraci\u00f3n del bot en desarrollo.",
        get_back_kb("admin_main_menu"),
        session,
        "admin_bot_config",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_main_menu")
async def back_to_admin_main(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Bienvenido al panel de administraci\u00f3n, Diana.",
        get_admin_main_keyboard(),
        session,
        "admin_main",
    )
    await callback.answer()


IGNORED_CALLBACKS = {
    "admin_vip",
    "admin_free",
    "admin_game",
    "admin_config",
    "admin_back",
    "admin_manage_users",
    "admin_manage_content",
    "admin_manage_events_sorteos",
    "admin_bot_config",
    "admin_main_menu",
}


@router.callback_query(F.data.startswith("admin_"))
async def admin_placeholder(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    if callback.data in IGNORED_CALLBACKS:
        return await callback.answer()
    await callback.answer("Funcionalidad en desarrollo.", show_alert=True)

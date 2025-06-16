from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from keyboards.admin_config_kb import get_admin_config_kb, get_scheduler_config_kb
from utils.keyboard_utils import get_back_keyboard
from services.config_service import ConfigService
from services.scheduler import run_channel_request_check, run_vip_subscription_check
from database.setup import get_session
from utils.admin_state import AdminConfigStates
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(F.data == "admin_config")
async def config_menu(callback: CallbackQuery, session: AsyncSession):
    """Placeholder bot configuration menu."""
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Configuraci\u00f3n del bot",
        get_admin_config_kb(),
        session,
        "admin_config",
    )
    await callback.answer()


@router.callback_query(F.data == "config_reaction_buttons")
async def prompt_reaction_buttons(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Envía los textos para las reacciones separados por ';' (ejemplo: 👍;👎)",
        reply_markup=get_back_keyboard("admin_config"),
    )
    await state.set_state(AdminConfigStates.waiting_for_reaction_buttons)
    await callback.answer()


@router.message(AdminConfigStates.waiting_for_reaction_buttons)
async def set_reaction_buttons(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    texts = [t.strip() for t in message.text.split(";") if t.strip()]
    if len(texts) < 2:
        await message.answer("Debes proporcionar al menos dos textos separados por ';'")
        return
    service = ConfigService(session)
    await service.set_value("reaction_buttons", ";".join(texts))
    await message.answer("Botones de reacción actualizados.", reply_markup=get_admin_config_kb())
    await state.clear()


@router.callback_query(F.data == "config_scheduler")
async def scheduler_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = ConfigService(session)
    ch = await config.get_value("channel_scheduler_interval") or "30"
    vip = await config.get_value("vip_scheduler_interval") or "3600"
    text = f"Intervalos actuales:\nCanal: {ch}s\nVIP: {vip}s"
    await update_menu(callback, text, get_scheduler_config_kb(), session, "scheduler_config")
    await callback.answer()


@router.callback_query(F.data == "set_channel_interval")
async def prompt_channel_interval(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Ingresa el intervalo en segundos para revisar solicitudes de canal:",
        reply_markup=get_back_keyboard("config_scheduler"),
    )
    await state.set_state(AdminConfigStates.waiting_for_channel_interval)
    await callback.answer()


@router.callback_query(F.data == "set_vip_interval")
async def prompt_vip_interval(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Ingresa el intervalo en segundos para revisar suscripciones VIP:",
        reply_markup=get_back_keyboard("config_scheduler"),
    )
    await state.set_state(AdminConfigStates.waiting_for_vip_interval)
    await callback.answer()


@router.callback_query(F.data == "run_schedulers_now")
async def run_schedulers_now(callback: CallbackQuery, bot: Bot, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    Session = await get_session()
    await run_channel_request_check(bot, Session)
    await run_vip_subscription_check(bot, Session)
    await callback.answer("Schedulers ejecutados", show_alert=True)


@router.message(AdminConfigStates.waiting_for_channel_interval)
async def set_channel_interval(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    try:
        seconds = int(message.text.strip())
    except ValueError:
        await message.answer("Ingresa un número válido.")
        return
    await ConfigService(session).set_value("channel_scheduler_interval", str(seconds))
    await message.answer("Intervalo actualizado.", reply_markup=get_admin_config_kb())
    await state.clear()


@router.message(AdminConfigStates.waiting_for_vip_interval)
async def set_vip_interval(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    try:
        seconds = int(message.text.strip())
    except ValueError:
        await message.answer("Ingresa un número válido.")
        return
    await ConfigService(session).set_value("vip_scheduler_interval", str(seconds))
    await message.answer("Intervalo actualizado.", reply_markup=get_admin_config_kb())
    await state.clear()

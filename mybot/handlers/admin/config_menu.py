from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from keyboards.admin_config_kb import get_admin_config_kb
from utils.keyboard_utils import get_back_keyboard
from services.config_service import ConfigService
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

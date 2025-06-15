from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from keyboards.admin_channels_kb import get_admin_channels_kb, get_wait_time_kb
from keyboards.common import get_back_kb
from services.channel_service import ChannelService
from database.models import BotConfig

router = Router()


class ChannelStates(StatesGroup):
    waiting_for_id = State()


@router.callback_query(F.data == "admin_channels")
async def channels_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(
        callback,
        "Administrar canales",
        get_admin_channels_kb(),
        session,
        "admin_channels",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_channel")
async def prompt_add_channel(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text(
        "Reenvía un mensaje del canal o envía su ID numérico.",
        reply_markup=get_back_kb("admin_channels"),
    )
    await state.set_state(ChannelStates.waiting_for_id)
    await callback.answer()


@router.message(ChannelStates.waiting_for_id)
async def add_channel(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    chat_id = None
    title = None
    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        title = message.forward_from_chat.title
    else:
        try:
            chat_id = int(message.text.strip())
        except (TypeError, ValueError):
            await message.answer("No se pudo obtener el ID del canal. Intenta de nuevo.")
            return
    service = ChannelService(session)
    await service.add_channel(chat_id, title)
    await message.answer(
        f"Canal {chat_id} agregado.", reply_markup=get_admin_channels_kb()
    )
    await state.clear()


@router.callback_query(F.data == "admin_wait_time")
async def wait_time_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    config = await session.get(BotConfig, 1)
    current = config.free_channel_wait_time_minutes if config else 0
    await update_menu(
        callback,
        f"Tiempo actual: {current} minutos",
        get_wait_time_kb(),
        session,
        "admin_wait_time",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("wait_"))
async def set_wait_time(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    minutes = int(callback.data.split("_")[1])
    config = await session.get(BotConfig, 1)
    if not config:
        config = BotConfig(id=1)
        session.add(config)
    config.free_channel_wait_time_minutes = minutes
    await session.commit()
    await update_menu(
        callback,
        f"Tiempo actualizado a {minutes} minutos.",
        get_admin_channels_kb(),
        session,
        "admin_channels",
    )
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin
from utils.menu_utils import update_menu
from keyboards.tarifas_kb import get_tarifas_kb, get_duration_kb
from services.plan_service import SubscriptionPlanService

router = Router()


class PlanStates(StatesGroup):
    waiting_name = State()
    waiting_price = State()


@router.callback_query(F.data == "config_tarifas")
async def tarifas_menu(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(callback, "Gestión de Tarifas", get_tarifas_kb(), session, "config_tarifas")
    await callback.answer()


@router.callback_query(F.data == "tarifa_new")
async def tarifa_new(callback: CallbackQuery, session: AsyncSession):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await update_menu(callback, "Selecciona la duración", get_duration_kb(), session, "config_tarifas_duration")
    await callback.answer()


@router.callback_query(F.data.startswith("plan_dur_"))
async def select_duration(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    duration = int(callback.data.split("_")[-1])
    await state.update_data(duration_days=duration)
    await callback.message.edit_text("Introduce el nombre de la tarifa:")
    await state.set_state(PlanStates.waiting_name)
    await callback.answer()


@router.message(PlanStates.waiting_name)
async def plan_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text)
    await message.answer("Introduce el precio:")
    await state.set_state(PlanStates.waiting_price)


@router.message(PlanStates.waiting_price)
async def plan_price(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Precio inválido. Ingresa un número.")
        return
    service = SubscriptionPlanService(session)
    plan = await service.create_plan(message.from_user.id, data["name"], price, data["duration_days"])
    bot_username = (await bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={plan.token}"
    await message.answer(
        f"Tarifa creada:\nNombre: {plan.name}\nPrecio: {plan.price}\nDuración: {plan.duration_days} días\nEnlace: {link}"
    )
    await state.clear()

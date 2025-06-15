from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin
from utils.admin_state import AdminTariffStates
from keyboards.tarifas_kb import get_duration_kb
from keyboards.common import get_back_kb
from database.models import Tariff

router = Router()


@router.message(Command("admin_configure_tariffs"))
async def admin_configure_tariffs(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminTariffStates.waiting_for_tariff_duration)
    await message.answer("Selecciona la duración:", reply_markup=get_duration_kb())


@router.callback_query(AdminTariffStates.waiting_for_tariff_duration)
async def tariff_duration_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    duration = int(callback.data.split("_")[-1])
    await state.update_data(duration_days=duration)
    await state.set_state(AdminTariffStates.waiting_for_tariff_price)
    await callback.message.edit_text("Ingresa el precio de la tarifa:")
    await callback.answer()


@router.message(AdminTariffStates.waiting_for_tariff_price)
async def tariff_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        price = int(message.text)
    except ValueError:
        await message.answer("Precio inválido. Ingresa un número.")
        return
    await state.update_data(price=price)
    await state.set_state(AdminTariffStates.waiting_for_tariff_name)
    await message.answer("Ingresa el nombre de la tarifa:")


@router.message(AdminTariffStates.waiting_for_tariff_name)
async def tariff_name(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    tariff = Tariff(
        name=message.text,
        duration_days=data["duration_days"],
        price=data["price"],
    )
    session.add(tariff)
    await session.commit()
    await message.answer("Tarifa generada.", reply_markup=get_back_kb())
    await state.clear()

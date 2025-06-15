from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from utils.user_roles import is_admin
from services.token_service import TokenService

router = Router()

# Temporary storage for admin input steps
_waiting_name: dict[int, dict] = {}
_waiting_price: dict[int, dict] = {}


def get_pricing_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="1 Day", callback_data="plan_dur:1")
    builder.button(text="1 Week", callback_data="plan_dur:7")
    builder.button(text="2 Weeks", callback_data="plan_dur:14")
    builder.button(text="1 Month", callback_data="plan_dur:30")
    builder.button(text="🔙 Volver", callback_data="admin_config")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data == "config_plans")
async def config_plans(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await callback.message.edit_text("Elige la duración del plan", reply_markup=get_pricing_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("plan_dur:"))
async def plan_duration_selected(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    days = int(callback.data.split(":", 1)[1])
    _waiting_name[callback.from_user.id] = {"duration": days}
    await callback.message.edit_text("Ingresa el nombre del plan")
    await callback.answer()


@router.message(lambda m: m.from_user and m.from_user.id in _waiting_name)
async def plan_name_input(message: Message):
    data = _waiting_name.pop(message.from_user.id)
    data["name"] = message.text.strip()
    _waiting_price[message.from_user.id] = data
    await message.answer("Ingresa el precio del plan")


@router.message(lambda m: m.from_user and m.from_user.id in _waiting_price)
async def plan_price_input(message: Message, session: AsyncSession):
    data = _waiting_price.pop(message.from_user.id)
    try:
        price = int(message.text.strip())
    except ValueError:
        await message.answer("Ingresa solo números para el precio")
        return
    service = TokenService(session)
    plan = await service.create_plan(data["duration"], data["name"], price)
    bot_username = (await message.bot.me()).username
    link = f"https://t.me/{bot_username}?start={plan.token}"
    await message.answer(f"Plan creado: {plan.name} - {plan.price}\nEnlace: {link}")



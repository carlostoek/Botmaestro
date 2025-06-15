import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties

from handlers import start, admin, free_user
from handlers.vip import menu as vip, gamification
from utils.config import BOT_TOKEN


async def main() -> None:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(vip.router)
    dp.include_router(gamification.router)
    dp.include_router(free_user.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from database.setup import init_db, get_session

from handlers import start, free_user
from handlers.vip import menu as vip
from handlers.admin import admin_router
from utils.config import BOT_TOKEN


async def main() -> None:
    await init_db()
    Session = await get_session()

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    def session_middleware_factory(session_factory, bot_instance):
        async def middleware(handler, event, data):
            async with session_factory() as session:
                data["session"] = session
                data["bot"] = bot_instance
                return await handler(event, data)
        return middleware

    dp.message.outer_middleware(session_middleware_factory(Session, bot))
    dp.callback_query.outer_middleware(session_middleware_factory(Session, bot))

    dp.include_router(start.router)
    dp.include_router(admin_router)
    dp.include_router(vip.router)
    dp.include_router(free_user.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

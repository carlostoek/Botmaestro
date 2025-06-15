import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from database.setup import init_db, get_session

from handlers import start, free_user
from handlers.channel_access import router as channel_access_router
from handlers.user import start_token
from handlers.vip import menu as vip
from handlers.admin import admin_router
from utils.config import BOT_TOKEN
from services import channel_request_scheduler


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
    dp.chat_join_request.outer_middleware(session_middleware_factory(Session, bot))
    dp.chat_member.outer_middleware(session_middleware_factory(Session, bot))

    dp.include_router(start_token)
    dp.include_router(start.router)
    dp.include_router(admin_router)
    dp.include_router(vip.router)
    dp.include_router(free_user.router)
    dp.include_router(channel_access_router)

    pending_task = asyncio.create_task(channel_request_scheduler(bot, Session))

    await dp.start_polling(bot)
    pending_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())

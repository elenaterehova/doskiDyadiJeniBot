import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from bot.handlers.general import router
from bot.handlers.admin.admin_handlers import *
# from bot.handlers.General import router
# from bot.handlers import *
from dotenv import load_dotenv
#
# from bot.handlers.admin import Admin, AdminsManagement, AdminSupportChat
# from bot.handlers.user import User

load_dotenv()

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()


async def main():
    bot = Bot(os.getenv('BOT_TOKEN'), parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(router, admins_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    dp.message.middleware(ChatActionMiddleware())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

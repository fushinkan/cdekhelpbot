import asyncio
import logging

import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

#from api.setup_db import setup_db


from app.core.config import settings
from bot.handlers.invoice import router as invoice_router
from bot.handlers.command_start import router as welcoming_router
from bot.handlers.authorization import router as authorize_router


async def startup(dispatcher: Dispatcher):
    print("Starting up...")


async def shutdown(dispatcher: Dispatcher):
    print("Shutting down...")


async def start_bot():
    
    # Кеширование
    redis = await aioredis.from_url(settings.REDIS_URL)
    storage = RedisStorage(redis)
    
    # База для работы бота
    bot = Bot(token=settings.SECRET_TOKEN)
    dp = Dispatcher(storage=storage)
    
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    
    # Подключение обработчиков
    dp.include_routers(
        welcoming_router,
        authorize_router,
        invoice_router,
    )
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
    
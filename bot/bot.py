import asyncio
import logging

import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

#from api.setup_db import setup_db

from app.core.config import settings
from bot.handlers import router as handlers_router
from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.middlewares.work_hours_middleware import WorkHoursMiddleware


async def startup(dispatcher: Dispatcher):
    logging.info("🚀 Бот запущен и готов к работе")


async def shutdown(dispatcher: Dispatcher):
    logging.info("🛑 Бот остановлен")


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
    dp.include_router(handlers_router)
    
    # Подключение middlewares
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(WorkHoursMiddleware())
    
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
    
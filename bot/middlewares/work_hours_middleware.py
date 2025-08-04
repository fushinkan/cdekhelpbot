from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

import asyncio
from datetime import datetime, time
from typing import Callable, Dict, Any, Awaitable
from zoneinfo import ZoneInfo


class WorkHoursMiddleware(BaseMiddleware):
    """
    Middleware для проверки рабочих часов бота.

    Args:
        BaseMiddleware: Базовый класс от которого наследуются все Middlewares

    Returns:
        bool: True, если время рабочее
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        if not await self.is_work_time():
            return await handler(event, data)

        sent = await event.answer("График работы: ПН-ПТ с 9 до 18, СБ-ВС с 9:30 до 16:30")
        await asyncio.sleep(15)
        await sent.delete()
        
        return 
    
    
    @classmethod
    async def is_work_time(cls) -> bool:
        """
        Метод для проверки графика бота.

        Returns:
            bool: True, если время рабочее.
        """
        
        moscow_tz = ZoneInfo("Europe/Moscow")
        now = datetime.now(tz=moscow_tz)
        current_time = now.time()
        weekday = now.weekday()
        
        
        if 0 <= weekday <= 4:
            return time(9, 0) <= current_time <= time(18, 0)
        
        elif weekday in (5, 6):
            return time(9, 30) <= current_time <= time(16, 30)
        
        return False
            
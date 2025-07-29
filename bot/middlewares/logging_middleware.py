import httpx
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.config import settings
from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import AdminNotExistsException, UserNotExistsException

from typing import Dict, Any, Awaitable, Callable

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для проверки пользователя по Telegram ID через FastAPI.

    - Делает GET-запрос для получения данных пользователя.
    - Обновляет telegram_name в FastAPI (если реализовано в роуте).
    - Не меняет is_logged.
    - Кладет данные пользователя в data.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        tg_id = event.from_user.id
        telegram_name = event.from_user.full_name

        data["is_logged"] = False
        data["role"] = None
        data["obj"] = None

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.BASE_FASTAPI_URL}/user/telegram/{tg_id}"
                )
                response.raise_for_status()

                user_data = response.json()
                print(f"USER_DATA IN MIDDLEWARE: {user_data=}")

                data["is_logged"] = user_data.get("is_logged", False)
                data["role"] = user_data.get("role")
                data["obj"] = user_data

            except httpx.HTTPStatusError as e:
                pass

        return await handler(event, data)
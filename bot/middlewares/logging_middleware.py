import httpx
from jose.exceptions import ExpiredSignatureError
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Dict, Any, Awaitable, Callable

from app.core.config import settings
from app.api.utils.security import Security
# Можно настроить уровень и формат

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для проверки пользователя по Telegram ID и валидации JWT-токенов.
    Логирует ключевые шаги авторизации.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        # Получаем Telegram user безопасно
        user = getattr(event, "from_user", None) or getattr(getattr(event, "message", None), "from_user", None)
        tg_id = getattr(user, "id", None)

        data.update({
            "tg_id": tg_id,
            "is_logged": False,
            "role": None,
            "obj": None,
            "access_token": None,
            "refresh_token": None
        })

        if tg_id is None:
            return await handler(event, data)

        async with httpx.AsyncClient() as client:
            try:
                resp_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{tg_id}")
                resp_user.raise_for_status()
                user_data = resp_user.json()

                data["obj"] = user_data
                data["role"] = user_data.get("role")
                data["is_logged"] = user_data.get("is_logged", False)
                access_token = user_data.get("access_token")
                refresh_token = user_data.get("refresh_token")
                user_id = user_data.get("id")

                if access_token is None and refresh_token is None:
                    return await handler(event, data)

                if access_token:
                    try:
                        await Security.decode_jwt(access_token=access_token)
                        data["access_token"] = access_token
                        data["refresh_token"] = refresh_token
                        data["is_logged"] = True
                        return await handler(event, data)
                    except ExpiredSignatureError:
                        access_token = None

                if refresh_token:
                    try:
                        await Security.decode_jwt(access_token=refresh_token)
                        rr = await client.put(
                            f"{settings.BASE_FASTAPI_URL}/tokens/refresh",
                            json={"user_id": user_id, "refresh_token": refresh_token},
                        )
                        rr.raise_for_status()
                        new_access = rr.json().get("access_token")

                        data["access_token"] = new_access
                        data["refresh_token"] = refresh_token
                        data["is_logged"] = True
                        return await handler(event, data)
                    except ExpiredSignatureError:
                        data["is_logged"] = False

            except httpx.HTTPStatusError as e:
                data["is_logged"] = False
            except Exception as e:
                data["is_logged"] = False

        return await handler(event, data)
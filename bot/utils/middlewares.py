from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import AdminNotExistsException, UserNotExistsException

from typing import Dict, Any, Awaitable, Callable



class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для проверки авторизации пользователя Telegram.

    Получает telegram_id и telegram_name из события, 
    проверяет наличие пользователя или администратора в базе,
    обновляет их данные и передаёт информацию о состоянии авторизации
    через словарь 'data' в обработчики.

    В 'data' добавляются ключи:
        - is_logged (bool): флаг авторизации.
        - role (str | None): роль пользователя ('admin', 'user' или None).
        - obj (UserInDB | None): объект пользователя или администратора из базы.
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        telegram_id = event.from_user.id
        telegram_name = event.from_user.full_name
        
        async with async_session_factory() as session:
            admin = None
            user = None
            
            try:
                admin = await UserInDB.get_admin_by_telegram_id(telegram_id=telegram_id, session=session)
                
            except AdminNotExistsException as e:
                pass
            
            try:
                user = await UserInDB.get_client_by_telegram_id(telegram_id=telegram_id, session=session)
                
            except UserNotExistsException as e:
                pass
                
            data["is_logged"] = False
            data["role"] = None
            data["obj"] = None
            
            if admin:
                
                admin.telegram_id = telegram_id
                admin.telegram_name = telegram_name
                
                await session.commit()
                await session.refresh(admin)
                
                data["is_logged"] = admin.is_logged
                data["role"] = admin.role
                data["obj"] = admin
            
            if user:

                user.telegram_id = telegram_id
                user.telegram_name = telegram_name
                
                await session.commit()
                await session.refresh(user)
                
                data["is_logged"] = user.is_logged
                data["role"] = user.role
                data["obj"] = user
            
        return await handler(event, data)


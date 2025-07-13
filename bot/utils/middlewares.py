from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import update

from app.db.models.admins import Admins
from app.db.models.users import Users
from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB

from typing import Dict, Any, Awaitable, Callable




class LoggingMiddleware(BaseMiddleware):
    """
    Проверка, залогинен ли пользователь.
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
            admin = await UserInDB.get_admin_by_telegram_id(telegram_id=telegram_id, session=session)
            user = await UserInDB.get_client_by_telegram_id(telegram_id=telegram_id, session=session)
            
            
                
            data["is_logged"] = None
            data["role"] = None
            data["obj"] = None
            
            if admin:
                print(f"admin {admin.is_logged}")
                await session.execute(
                    update(Admins)
                    .where(Admins.telegram_id == telegram_id)
                    .values(telegram_name=telegram_name)
                )
                data["is_logged"] = admin.is_logged
                data["role"] = admin.role
                data["obj"] = admin
            
            elif user:
                print(f"user {user.is_logged}")
                await session.execute(
                    update(Users)
                    .where(Users.telegram_id == telegram_id)
                    .values(telegram_name=telegram_name)
                )
                data["is_logged"] = user.is_logged
                data["role"] = user.role
                data["obj"] = user
            
            await session.commit()
            
        return await handler(event, data)

            
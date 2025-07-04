from sqlalchemy.ext.asyncio import AsyncSession

from app.api.handlers.normalize import normalize_phone
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException


class AuthUtils:
    """
    Класс с утилитами для авторизации пользователей/админов в Telegram-боте.    
    """
    
    @classmethod
    async def process_role_in_db(cls, phone_number: str, session: AsyncSession):
        """
        Проверка роли пользователя в базе данных.
        
        Args:
            phone_number (str): Номер телефона, который вводит пользователь/админ.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).
            
        Returns:
            ORM-Модель: ORM Модель пользователя/админа.
        """
        
        phone_number = await normalize_phone(phone_number)
        
        
        # Поиск админа в БД
        try:
            admin = await UserInDB.get_admin_by_phone(phone_number=phone_number, session=session)
            return "admin", admin, phone_number
        except UserNotExistsException:
            pass
        
        
        # Поиск пользователя в БД
        try:
            user = await UserInDB.get_client_by_phone(phone_number=phone_number, session=session)
            return "user", user, phone_number
        except UserNotExistsException:
            pass
        
        
        return None, None, None
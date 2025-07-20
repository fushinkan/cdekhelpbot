from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.utils.exceptions import UserNotExistsException, AdminNotExistsException
from app.db.models.users import Users
from app.db.models.admins import Admins
from app.db.models.phone_numbers import PhoneNumbers


class UserInDB:
    """
    Класс с различными методами для проверки наличия пользователя/админа в базе данных.
    """
    
    @classmethod
    async def get_client_by_phone(cls, *, phone_number: str, session: AsyncSession):
        """
        Функция проверяет наличие пользователя по номеру телефона в БД.

        Args:
            phone_number (str): Номер телефона, который пользователь отправляет боту.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Users: ORM модель пользователя для дальнейшей работы с API.
        """
        
        user_res = await session.execute(
            select(Users)
            .join(Users.phones)
            .where(PhoneNumbers.number == phone_number)
            .options(selectinload(Users.phones))
        )

        users = user_res.scalars().all()
        
        if not users:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        return users

    @classmethod
    async def get_admin_by_phone(cls, *, phone_number: str, session: AsyncSession):
        """
        Функция проверяет наличие админа по номеру телефона в БД.

        Args:
            phone_number (str): Номер телефона, который админ отправляет боту
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек)

        Raises:
            AdminNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Admins: ORM модель админа для дальнейшей работы с API.
        """
        
        admin_res = await session.execute(
            select(Admins).where(Admins.phone_number == phone_number)
        )
        
        admin = admin_res.scalar_one_or_none()
        
        if not admin:
            raise AdminNotExistsException(AdminNotExistsException.__doc__)
        
        return admin
    
    @classmethod
    async def get_client_by_telegram_id(cls, *, telegram_id: int, session: AsyncSession):
        """
        Поиск пользователя по Telegram ID.

        Args:
            telegram_id (int): Telegram ID передающийся в метод.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).

        Returns:
            Users: ORM  модель пользователя для дальнейшей работы с API.
        """
        
        result = await session.execute(
            select(Users)
            .where(Users.telegram_id == telegram_id)
            .options(selectinload(Users.phones))
        )
        
        return result.scalar_one_or_none()

    
    @classmethod
    async def get_admin_by_telegram_id(cls, *, telegram_id: int, session: AsyncSession):
        """
        Поиск админа по Telegram ID.

        Args:
            telegram_id (int): Telegram ID передающийся в метод.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).

        Returns:
            Admins: ORM  модель админа для дальнейшей работы с API.
        """
        
        result = await session.execute(
            select(Admins)
            .where(Admins.telegram_id == telegram_id)
        )
        
        return result.scalar_one_or_none()
        
    
    
    @classmethod
    async def get_client_by_id(cls, *, id: int, session: AsyncSession):
        """
        Поиск пользователя по ID в базе данных.

        Args:
            id (int): ID пользователя в БД передающийся в метод.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).
            
        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Users: ORM  модель пользователя для дальнейшей работы с API.
        """
        
        user_res = await session.execute(
                select(Users)
                .join(Users.phones)
                .where(PhoneNumbers.user_id == id)
                .options(selectinload(Users.phones))
            )

        users = user_res.scalars().all()
             
        if not users:
            raise UserNotExistsException(UserNotExistsException.__doc__)
            
        return users
        
        
    @classmethod
    async def get_admin_by_id(cls, *, id: int, session: AsyncSession):
        """
        Поиск админа по ID в базе данных.

        Args:
            id (int): ID админа в БД передающийся в метод.
            session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).
            
        Raises:
            AdminNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Admins: ORM  модель админа для дальнейшей работы с API.
        """
        
        result = await session.execute(
            select(Admins)
            .where(Admins.id == id)
        )
        
        return result.scalar_one_or_none()
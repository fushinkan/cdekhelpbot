from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import Users
from app.db.models.admins import Admins
from app.db.models.phone_numbers import PhoneNumbers
from bot.utils.exceptions import UserNotExistsException


class UserInDB:
    """
    Класс для получения пользователя из БД разными способами.

    Returns:
        Users | Admins: ORM-модель в зависимости от роли по переданному айди.
    """

    @classmethod
    async def get_user_by_id(cls, *, id: int, session: AsyncSession):
        """
        Метод возвращающий ORM-модель найденного пользователя (Admins или Users) по переданному ID.

        Args:
            id (int): ID пользователя из БД.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Users | Admins: ORM-модель в зависимости от роли по переданному айди.
        """

        
        admin = await session.get(Admins, id)
        
        if admin:
            return admin
        
        user_result = await session.execute(
            select(Users)
            .where(Users.id == id)
            .options(selectinload(Users.phones))
        )
        
        users = user_result.scalars().all()
        
        if users:
            return users[0]

        raise UserNotExistsException(UserNotExistsException.__doc__)


    @classmethod
    async def get_user_by_phone(cls, *, phone_number: str, session: AsyncSession):
        """
        Метод возвращающий ORM-модель найденного пользователя (Admins или Users) по введенному номеру телефона.

        Args:
            phone_number (str): Номер телефона, введенный пользователем.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Users | Admins: ORM-модель в зависимости от роли по введенному номеру телефона.
        """

        admin_res = await session.execute(
            select(Admins)
            .where(Admins.phone_number == phone_number)
        )
        
        admin = admin_res.scalar_one_or_none()
        
        if admin:
            return admin
        
        # Подгрузка номеров телефона для пользователя
        users_res = await session.execute(
            select(Users)
            .join(PhoneNumbers)
            .where(PhoneNumbers.number == phone_number)
            .options(selectinload(Users.phones))
        )
        
        users = users_res.scalars().all()
        
        if users:
            return users[0]
        
        raise UserNotExistsException(UserNotExistsException.__doc__)


    @classmethod
    async def get_user_by_telegram_id(cls, *, telegram_id: int, session: AsyncSession):
        """
        Метод возвращающий ORM-модель найденного пользователя (Admins или Users) по переданному Telegram ID.

        Args:
            telegram_id (int): Telegram ID переданный из объекта Message.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.

        Returns:
            Users | Admins: ORM-модель в зависимости от роли по переданному Telegram ID.
        """
        
        admin_res= await session.execute(
            select(Admins)
            .where(Admins.telegram_id == telegram_id)
        )
        
        admin = admin_res.scalar_one_or_none()
        
        if admin:
            return admin
            
        users_res = await session.execute(
            select(Users)
            .where(Users.telegram_id == telegram_id)
            .options(selectinload(Users.phones))
        )
        
        users = users_res.scalars().all()
        
        if users:
            return users[0]
        
        raise UserNotExistsException(UserNotExistsException.__doc__)
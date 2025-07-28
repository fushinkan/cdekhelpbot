from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.utils.exceptions import UserNotExistsException
from app.db.models.users import Users
from app.db.models.admins import Admins
from app.db.models.phone_numbers import PhoneNumbers

class UserInDB:
    """_summary_

    Returns:
        _type_: _description_
    """

    @classmethod
    async def get_user_by_id(cls, *, id: int, session: AsyncSession):
        """
        Универсальный поиск пользователя (админ или клиент) по ID.

        Returns:
            ORM-Модель Admin или Users
        """

        
        admin = await session.get(Admins, id)
        
        if admin:
            return admin
        
        user = await session.get(Users, id)
        
        if user:
            return user

        raise UserNotExistsException(UserNotExistsException.__doc__)

    @classmethod
    async def get_user_by_phone(cls, *, phone_number: str, session: AsyncSession):
        """
        Универсальный поиск пользователя по номеру телефона.
        """

        admin_res = await session.execute(
            select(Admins)
            .where(Admins.phone_number == phone_number)
        )
        
        admin = admin_res.scalar_one_or_none()
        
        if admin:
            return admin
            
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
        Универсальный поиск пользователя по Telegram ID.
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
        )
        
        user = users_res.scalar_one_or_none()
        
        if user:
            return user
        
        raise UserNotExistsException(UserNotExistsException.__doc__)
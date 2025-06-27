from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UsersSchema
from bot.utils.exceptions import UserNotExistsException
from db.models.users import Users


async def get_user_by_phone(phone_number: str, session: AsyncSession):
    """
    Функция проверяет наличие пользователя в БД.

    Args:
        phone_number (str): Номер телефона, который пользователь отправляет боту
        session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек)

    Raises:
        UserNotExistsException: Кастомный класс с ошибкой.

    Returns:
        PydanticSchema: Pydantic-схема для дальнейшей работы API.
    """
    result = await session.execute(
        select(Users).where(Users.phone_number == phone_number)
    )
    
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise UserNotExistsException(UserNotExistsException.__doc__)
    
    return existing_user

from fastapi import (APIRouter,
                     Depends,
                     HTTPException,
                     status)

from sqlalchemy.ext.asyncio import AsyncSession

from api.handlers.normalize import normalize_phone
from bot.utils.exceptions import UserNotExistsException, IncorrectPhone
from api.handlers.get_user import get_user_by_phone
from db.base import get_session
from schemas.users import UsersSchema

router = APIRouter()


@router.post("/check_phone", response_model=UsersSchema, status_code=status.HTTP_200_OK)
async def check_phone_endpoint(phone_number: str, session: AsyncSession = Depends(get_session)) -> UsersSchema:
    """
    Эндпоинт для проверки наличия пользователя в базе данных.
    
    Если пользователь найден, то возвращает ответ в виде Pydantic-схемы UsersSchema.
    В противном случае выдает кастомное исключение UserNotExistsException.

    Args:
        phone_number (str): Номер телефона, который пользователь передает в бота.
        session (AsyncSession, optional): Сессия для подключения к БД (автоматически подставляется через Depends).

    Returns:
        UsersSchema: Pydantic-схема с данными пользователя. (id, номер телефона, номер договора, город)
    """
    try:
        phone = normalize_phone(phone_number)
        user = await get_user_by_phone(phone, session)
        return UsersSchema.model_validate(user)
    except (UserNotExistsException) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except IncorrectPhone as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
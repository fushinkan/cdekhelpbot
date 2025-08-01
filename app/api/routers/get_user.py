from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.normalize import Normalize
from app.db.base import get_session
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException


router = APIRouter(prefix="/user", tags=["Auth"])


@router.get("/phone/{phone_number}", status_code=status.HTTP_200_OK)
async def get_user_by_phone_endpoint(phone_number: str, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения пользователя (admin или user) по введенному номеру телефона.

    Args:
        phone_number (str): Номер телефона, введенный пользователем.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException: 404 - Not Found. Пользователь не найден.

    Returns:
        Users | Admins: ORM-модель в зависимости от введенного номера телефона.
    """
    
    # Приведение номера телефона к единому формату
    phone_number = await Normalize.normalize_phone(phone=phone_number)
    
    try:
        user = await UserInDB.get_user_by_phone(phone_number=phone_number, session=session)
        return user
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    

@router.get("/telegram/{tg_id}", status_code=status.HTTP_200_OK)
async def get_user_by_telegram_id_endpoint(tg_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения пользователя (admin или user) по переданному Telegram ID.

    Args:
        tg_id (int): Telegram ID, переданный из объекта Message.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException: 404 - Not Found. Пользователь не найден.

    Returns:
        Users | Admins: ORM-модель в зависимости от переданного Telegram ID.
    """
    
    try:
        user = await UserInDB.get_user_by_telegram_id(telegram_id=tg_id, session=session)
        return user

    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
        
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id_endpoint(user_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения пользователя (admin или user) по ID из БД.

    Args:
        user_id (int): ID пользователя из БД.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException: 404 - Not Found. Пользователь не найден.

    Returns:
        Users | Admins: ORM-модель в зависимости от переданного ID.
    """

    try:
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        return user
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
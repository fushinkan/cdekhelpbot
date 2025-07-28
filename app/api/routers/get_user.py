from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.normalize import normalize_phone
from app.db.base import get_session
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/phone/{phone_number}", status_code=status.HTTP_200_OK)
async def get_user_by_phone_endpoint(phone_number: str, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения пользователя по номеру телефона.

    Args:
        data (PhoneInputSchema): Pydantic-схема для ввода номера телефона.
        session (AsyncSession, optional): Асинхронная сессия. По умолчанию берется из настроек.
    """
    phone_number = await normalize_phone(phone=phone_number)
    print(f"AFTER NORMALIZE: {phone_number}")
    
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
    Эндпоинт для получения пользователя по Telegram ID.

    Args:
        data (PhoneInputSchema): Pydantic-схема для Telegram ID.
        session (AsyncSession, optional): Асинхронная сессия. По умолчанию берется из настроек.
    """
    
    try:
        user = await UserInDB.get_user_by_telegram_id(telegram_id=tg_id, session=session)
        return user

    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id_endpoint(user_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения пользователя по ID из БД.

    Args:
        data (PhoneInputSchema): Pydantic-схема для ID из БД.
        session (AsyncSession, optional): Асинхронная сессия. По умолчанию берется из настроек.
    """

    try:
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        return user
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
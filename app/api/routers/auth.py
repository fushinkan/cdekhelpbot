from fastapi import Depends, APIRouter, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.normalize import Normalize
from app.api.services.auth import AuthService
from app.db.base import get_session
from app.schemas.auth import LoginStatusSchema, PasswordInputSchema, ConfirmPasswordSchema, AcceptPasswordSchema
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.put("/{role}/{user_id}/login_status", status_code=status.HTTP_204_NO_CONTENT)
async def update_login_status_endpoint(
    user_id: int,
    role: str,
    data: LoginStatusSchema,
    session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт для обновления статуса у пользователя по ID (admin или user).

    Args:
        user_id (int): ID пользователя из БД.
        role (str): Роль пользователя (admin или user).
        data (LoginStatusSchema): Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Returns:
        Response: 204 - No Content. Ничего не создано, обновлена колонка is_logged у пользователя.
    """
    
    await AuthService.update_login_status(
        session=session,
        user_id=user_id,
        is_logged=data.is_logged,
        role=role
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/set_password", status_code=status.HTTP_200_OK)
async def set_password_endpoint(data: PasswordInputSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для первичной установки пароля для пользователя (admin или user).

    Args:
        data (PasswordInputSchema): Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException:  404 - Not Found. Пользователь не найден.

    Returns:
        dict: Сообщение об установленном пароле.
    """
    
    try:
        await AuthService.set_password(user_id=data.user_id, plain_password=data.plain_password, session=session)
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    return {"message": "Password saved"}


@router.put("/confirm_password", status_code=status.HTTP_200_OK)
async def confirm_password_endpoint(data: ConfirmPasswordSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для подтверждения введенного пароля для пользователя (admin или user). 

    Args:
        data (ConfirmPasswordSchema): _Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException: 404 - Not Found. Пользователь не найден.
        HTTPException: 400 - Bad Request. Неверный пароль.

    Returns:
        dict: Сообщение об успешной верификации и установке пароля.
    """
    
    try:
        access_token = await AuthService.confirm_password(
            user_id=data.user_id,
            confirm_password=data.confirm_password,
            session=session,
            is_change=data.is_change,
            telegram_id=data.telegram_id,
            telegram_name=data.telegram_name
        )
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except IncorrectPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return {"message": "Password is set", "access_token": access_token, "token_type": "bearer"}


@router.post("/accept_enter", status_code=status.HTTP_200_OK)
async def accept_enter_endpoint(data: AcceptPasswordSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для подтверждения входа ддля пользователя (admin или user), если пароль уже был.

    Args:
        data (AcceptPasswordSchema): Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Raises:
        HTTPException: 404 - Not Found. Пользователь не найден.
        HTTPException: 400 - Bad Request. Неверный пароль.

    Returns:
        dict: Сообщение об успешной логинизации.
    """
    
    # Приведение номера телефона к единому формату
    phone_number = await Normalize.normalize_phone(phone=data.phone_number)
    
    try:
        access_token = await AuthService.accept_enter(
            password=data.password,
            user_id=data.user_id,
            telegram_id=data.telegram_id,
            telegram_name=data.telegram_name,
            session=session
        )
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except IncorrectPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    return {"message": "Successfully logged in", "access_token": access_token, "token_type": "bearer"}
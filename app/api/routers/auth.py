from fastapi import Depends, APIRouter, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.normalize import normalize_phone
from app.api.handlers.auth import AuthService
from app.schemas.auth import LoginStatusSchema, PasswordInputSchema, ConfirmPasswordSchema, LoginRequestSchema, AcceptPasswordSchema
from app.db.base import get_session
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.put("/{role}/{user_id}/login_status", status_code=status.HTTP_200_OK)
async def update_login_status_endpoint(
    user_id: int,
    role: str,
    data: LoginStatusSchema,
    session: AsyncSession = Depends(get_session)
):
    await AuthService.update_login_status(
        session=session,
        user_id=user_id,
        is_logged=data.is_logged,
        telegram_id=data.telegram_id,
        telegram_name=data.telegram_name,
        role=role
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/set_password", status_code=status.HTTP_200_OK)
async def set_password_endpoint(data: PasswordInputSchema, session: AsyncSession = Depends(get_session)):
    
    try:
        await AuthService.set_password(user_id=data.user_id, plain_password=data.plain_password, session=session)
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    return {"message": "Password successfully added"}


@router.put("/confirm_password", status_code=status.HTTP_200_OK)
async def confirm_password_endpoint(data: ConfirmPasswordSchema, session: AsyncSession = Depends(get_session)):
    
    try:
        await AuthService.confirm_password(
            telegram_id=data.telegram_id,
            plain_password=data.plain_password,
            confirm_password=data.confirm_password,
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
    
    return {"message": "Password Successfully Confirmed and Set"}


@router.post("/accept_enter", status_code=status.HTTP_200_OK)
async def accept_enter_endpoint(data: AcceptPasswordSchema, session: AsyncSession = Depends(get_session)):
    phone_number = await normalize_phone(phone=data.phone_number)
    
    try:
        await AuthService.accept_enter(
            phone_number=phone_number,
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
        
    return {"message": "Login Successful"}
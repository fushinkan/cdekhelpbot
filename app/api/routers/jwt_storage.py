from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.jwt_storage import TokenSaveSchema, TokenSaveResponse, RefreshAccessTokenSchema, TokenClearSchema
from app.db.base import get_session
from app.api.services.jwt_storage import JWTStorage
from bot.utils.exceptions import UserNotExistsException, InvalidTokenException


router = APIRouter(prefix="/tokens", tags=["JWTStorage"])


@router.post("/", response_model=TokenSaveResponse, status_code=status.HTTP_201_CREATED)
async def save_tokens_endpoint(data: TokenSaveSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для сохранения токенов в БД для конкретного пользователя.

    Args:
        data (TokenSaveSchema): Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Returns:
        dict: Сообщение об успешном сохранении токенов.
    """
    try:
        user = await JWTStorage.save_tokens(
            access_token=data.access_token,
            refresh_token=data.refresh_token,
            user_id=data.user_id,
            session=session
        )
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    return TokenSaveResponse(message="ok", user_id=user.id)


@router.put("/refresh", status_code=status.HTTP_200_OK)
async def refresh_access_token_endpoint(data: RefreshAccessTokenSchema, session: AsyncSession = Depends(get_session)):
    
    try:
        new_access_token = await JWTStorage.refresh_access_token(
            user_id=data.user_id,
            refresh_token=data.refresh_token,
            session=session
        )
        
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
        
    return {"access_token": new_access_token}


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_access_token_endpoint(user_id: int, session: AsyncSession = Depends(get_session)):
    
    try:
        access_token = await JWTStorage.get_access_token(user_id=user_id, session=session)
        return {"access_token": access_token}
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    
@router.put("/clear", status_code=status.HTTP_200_OK)
async def clear_tokens_endpoint(data: TokenClearSchema, session: AsyncSession = Depends(get_session)):
    
    try:
        await JWTStorage.clear_tokens(user_id=data.user_id, session=session)
    
    except UserNotExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        
    return {"message": "Tokens deleted"}
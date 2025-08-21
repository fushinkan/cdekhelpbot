from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.security import Security
from app.api.services.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException, InvalidTokenException

from datetime import datetime, timedelta, timezone


class JWTStorage:
    
    @classmethod
    async def save_tokens(cls, *, access_token: str, refresh_token: str, user_id: int, session: AsyncSession):
        """
        Метод для сохранения токенов в БД для конретного пользователя.

        Args:
            access_token (str): Access Token.
            refresh_token (str): Refresh Token.
            user_id (int): ID пользователя из БД.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.
        """
        
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        user.access_token = access_token
        user.refresh_token = refresh_token
        
        await session.commit()
        
        return user
    
    
    @classmethod
    async def refresh_access_token(cls, *, user_id: int, refresh_token: str, session: AsyncSession):
        """
        Метод для обновления access_token если тот просрочился

        Args:
            user_id (int): ID пользователя из БД.
            refresh_token (str): Refresh Token.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.
            InvalidTokenException: Кастомный класс с ошибкой.

        Returns:
            str: Новый Access Token.
        """
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        try:
            payload = await Security.decode_jwt(access_token=refresh_token)
            
        except Exception:
            raise InvalidTokenException("Токен не принадлежит пользователю")
        
        if user.role == 'user':
            # Телефоны у user через phones связь
            phone_obj = user.phones[0] if user.phones else None
            phone = phone_obj.number if phone_obj else None
        elif user.role == 'admin':
            # Телефон у админа, например, в поле phone_number (пример)
            phone = getattr(user, 'phone_number', None)
        else:
            phone = None
            
        new_access_payload = {
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id,
            "telegram_name": user.telegram_name,
            "phone": phone,
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        }
        
        new_access_token = await Security.encode_jwt(payload=new_access_payload)
        
        user.access_token = new_access_token
        await session.commit()
        
        return new_access_token
    

    @classmethod
    async def get_access_token(cls, *, user_id: int, session: AsyncSession) -> str:
        
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        access_token = user.access_token
        
        return access_token
    
    
    @classmethod
    async def clear_tokens(cls, *, user_id: int, session: AsyncSession):
        
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        user.access_token = None
        user.refresh_token = None
        
        await session.commit()
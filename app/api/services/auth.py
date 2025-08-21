from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.get_user import UserInDB
from app.api.utils.security import Security
from app.db.models.admins import Admins
from app.db.models.users import Users
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException, AlreadyLoggedException, InvalidRoleException

from datetime import datetime, timedelta, timezone


class AuthService:
    """
    Класс с функциями для авторизации пользователя.

    Raises:
        IncorrectPasswordException: Кастомный класс с исключением.
        UserNotExistsException: Кастомный класс с исключением.
    """
    
    _temp_passwords: dict[int, str] = {}
    
    @classmethod
    async def update_login_status(
        cls,
        *,
        session: AsyncSession,
        user_id: int,
        is_logged: bool,
        role: str = "user",
    ):
        """
        Метод для изменения is_logged.
        
        Args:
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
            user_id (int): ID пользователя в БД.
            is_logged (bool): Значение True или False для проставления статуса.
            telegram_name (str | None, optional): Telegram username. Defaults to None.
            telegram_id (int | None, optional): Telegram ID. Defaults to None.
            role (str, optional): Роль пользователя для которого меняем статус is_logged. Defaults to "user".
        """
        
        if role not in ("user", "admin"):
            raise InvalidRoleException(InvalidRoleException.__doc__)
        
        # Получение модели для поиска пользователя (Users или Admins)
        model = Users if role == "user" else Admins
        
        user = await session.get(model, user_id)
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        user.is_logged = is_logged
        
        await session.commit()

        return user
    
                
    @classmethod
    async def set_password(
        cls,
        *,
        user_id: int, 
        plain_password: str,
        session: AsyncSession
    ):
        """
        Метод для первичной установки пароля для пользователя (admin или user).

        Args:
            user_id (int): ID пользователя из БД.
            plain_password (str): Первый пароль, который вводит пользователь (admin или user).
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            hashed_password: Захэшированный пароль.
        """
        
        # Получение пользователя по ID из БД (admin или user)
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        cls._temp_passwords[user_id] = plain_password
        
        return True


    @classmethod
    async def confirm_password(
        cls,
        *,
        user_id: int,
        confirm_password: str,
        is_change: bool = False,
        telegram_name: str | None = None,
        telegram_id: int | None = None,
        session: AsyncSession
    ):
        """
        Метод для подтверждения первичного ввода пароля.

        Args:
            user_id (int): ID пользователя из БД.
            plain_password (str): Первый введенный пароль.
            confirm_password (str): Второй введенный пароль.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Raises:
            IncorrectPasswordException: Кастомный класс с ошибкой.
            UserNotExistsException: Кастомный класс с ошибкой.
        """
        plain_password = cls._temp_passwords[user_id]
        
        # Проверка первичного пароля, со вторым введенным
        if plain_password != confirm_password:
            raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        # Получение пользователя по ID из БД (admin или user)
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
         
        if telegram_id is not None:
            user.telegram_id = telegram_id
        if telegram_name is not None:
            user.telegram_name = telegram_name
        
        session.add(user)
        
        if is_change:
            # Установка пароля для пользователя
            user.hashed_psw = Security.hashed_password(password=plain_password)
            
            # Обновление статуса is_logged на False
            await cls.update_login_status(
                user_id=user_id,
                role=user.role,
                is_logged=False,
                session=session
            )
        
        else:
            # Установка пароля для пользователя
            user.hashed_psw = Security.hashed_password(password=plain_password)
            
            # Обновление статуса is_logged на True
            await cls.update_login_status(
                user_id=user_id,
                role=user.role,
                is_logged=True,
                session=session
            )
                
        del cls._temp_passwords[user_id]
        
        await session.flush()
        await session.commit()
        
        if user.role == 'user':
            # Телефоны у user через phones связь
            phone_obj = user.phones[0] if user.phones else None
            phone = phone_obj.number if phone_obj else None
        elif user.role == 'admin':
            # Телефон у админа, например, в поле phone_number (пример)
            phone = getattr(user, 'phone_number', None)
        else:
            phone = None
        
        access_payload = {
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id,
            "telegram_name": user.telegram_name,
            "phone": phone,
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        }
        
        refresh_payload = {
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id,
            "telegram_name": user.telegram_name,
            "phone": phone,
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=30)
        }
        
        access_token = await Security.encode_jwt(payload=access_payload)
        refresh_token = await Security.encode_jwt(payload=refresh_payload)
        
        
        return access_token, refresh_token

        
    @classmethod
    async def accept_enter(
        cls, 
        *,
        user_id: int,
        password: str,
        telegram_id: int | None = None,
        telegram_name: str | None = None,
        session: AsyncSession
    ):
        """
        Метод для подтверждения входа, если у пользователя уже был установлен пароль.

        Args:
            user_id (int): ID пользователя из БД.
            phone_number (str): Номер телефона, введенный пользователем.
            password (str): Пароль, введенный пользователем.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
            telegram_id (int | None, optional): Telegram ID. Defaults to None.
            telegram_name (str | None, optional): Telegram username. Defaults to None.

        Raises:
            UserNotExistsException: Кастомный класс с ошибкой.
            IncorrectPasswordException: Кастомный класс с ошибкой.
        """
        
        # Получения пользователя по ID из БД (admin или user)
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        # Проверка, залогинен ли пользователь
        if user.is_logged:
            raise AlreadyLoggedException(AlreadyLoggedException.__doc__)
        
        if telegram_id is not None:
            user.telegram_id = telegram_id
        if telegram_name is not None:
            user.telegram_name = telegram_name
        
        session.add(user)
        
        # Проверка введенного пароля и захэшированного пароля в БД
        if not Security.verify_password(plain_password=password, hashed_password=user.hashed_psw):
            raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        # Обновление статуса is_logged на True
        await cls.update_login_status(
            user_id=user_id,
            role=user.role,
            is_logged=True,
            session=session
        )
        
        await session.flush()
        await session.commit()
        
        if user.role == 'user':
            # Телефоны у user через phones связь
            phone_obj = user.phones[0] if user.phones else None
            phone = phone_obj.number if phone_obj else None
        elif user.role == 'admin':
            # Телефон у админа, например, в поле phone_number (пример)
            phone = getattr(user, 'phone_number', None)
        else:
            phone = None
        
        access_payload = {
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id,
            "telegram_name": user.telegram_name,
            "phone": phone,
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        }
        
        refresh_payload = {
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id,
            "telegram_name": user.telegram_name,
            "phone": phone,
            "exp": datetime.now(tz=timezone.utc) + timedelta(days=30)
        }
        
        access_token = await Security.encode_jwt(payload=access_payload)
        refresh_token = await Security.encode_jwt(payload=refresh_payload)
        
        
        return access_token, refresh_token
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.handlers.get_user import UserInDB
from app.api.utils.security import Security
from app.db.models.admins import Admins
from app.db.models.users import Users
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException, AlreadyLoggedException, InvalidRoleException


class AuthService:
    """
    Класс с функциями для авторизации пользователя.

    Raises:
        IncorrectPasswordException: Кастомный класс с исключением.
        UserNotExistsException: Кастомный класс с исключением.
    """
    
    @classmethod
    async def update_login_status(
        cls,
        *,
        session: AsyncSession,
        user_id: int,
        is_logged: bool,
        telegram_name: str | None = None,
        telegram_id: int | None = None,
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
        
        update_data = {"is_logged": is_logged}

        if telegram_name is not None:
            update_data["telegram_name"] = telegram_name
            
        if telegram_id is not None:
            update_data["telegram_id"] = telegram_id
                
        await session.execute(
            update(model)
            .where(model.id == user_id)
            .values(**update_data)
        )
        
        await session.commit()
        
        
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
        
        # Хэширование первого введенного пароля
        hashed = Security.hashed_password(password=plain_password)
        
        return hashed


    @classmethod
    async def confirm_password(
        cls,
        *,
        user_id: int,
        plain_password: str,
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
        
        # Проверка первичного пароля, со вторым введенным
        #if plain_password != confirm_password:
        #    raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        # Получение пользователя по ID из БД (admin или user)
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        # Проверка, залогинен ли пользователь
        if user.is_logged:
            raise AlreadyLoggedException(AlreadyLoggedException.__doc__)
        
        # Установка пароля для пользователя
        user.hashed_psw = Security.hashed_password(password=plain_password)
        
        await session.commit()
        
        
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
        
        # Проверка введенного пароля и захэшированного пароля в БД
        if not Security.verify_password(plain_password=password, hashed_password=user.hashed_psw):
            raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        # Обновление статуса is_logged на True
        await cls.update_login_status(
            user_id=user_id,
            role=user.role,
            is_logged=True,
            telegram_id=telegram_id,
            telegram_name=telegram_name,
            session=session
        )
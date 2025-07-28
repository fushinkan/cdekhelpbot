from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.db.models.admins import Admins
from app.db.models.users import Users
from app.api.handlers.get_user import UserInDB
from app.api.utils.security import Security
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException

class AuthService:
    
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
    
        if role == "user":
            model = Users
        
        elif role == "admin":
            model = Admins
            
        await session.execute(
            update(model)
            .where(model.id == user_id)
            .values(
                is_logged=is_logged,
                telegram_name=telegram_name,
                telegram_id=telegram_id
            )
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
        
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        user.hashed_psw = Security.hashed_password(plain_password)
        
        await session.commit()

    @classmethod
    async def confirm_password(
        cls,
        *,
        user_id: int,
        plain_password: str,
        confirm_password: str,
        session: AsyncSession
    ):
        if plain_password != confirm_password:
            raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        user = await UserInDB.get_user_by_id(id=user_id, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        user.hashed_psw = Security.hashed_password(confirm_password)
        
        await session.commit()
        
    @classmethod
    async def accept_enter(
        cls, 
        *,
        phone_number: str,
        plain_passsord: str,
        telegram_id: int | None = None,
        telegram_name: str | None = None,
        session: AsyncSession
    ):
        user = await UserInDB.get_user_by_phone(phone_number=phone_number, session=session)
        
        if not user:
            raise UserNotExistsException(UserNotExistsException.__doc__)
        
        if not Security.verify_password(plain_password=plain_passsord, hashed_password=user.hashed_psw):
            raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
        
        model = Users if user.role == "user" else Admins
        
        await session.execute(
            update(model)
            .where(model.id == user.id)
            .values(
                is_logged=True,
                telegram_id=telegram_id,
                telegram_name=telegram_name
            )
        )
        
        await session.commit()
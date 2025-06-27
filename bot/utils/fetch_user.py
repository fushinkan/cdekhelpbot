from sqlalchemy.ext.asyncio import AsyncSession

from db.base import async_session_factory
from api.handlers.get_user import get_user_by_phone
from bot.utils.exceptions import UserNotExistsException

async def fetch_user_by_phone(phone: str):
    async with async_session_factory() as session:
        try:
            user = await get_user_by_phone(phone, session)
            return user
        except UserNotExistsException as e:
            raise e
        
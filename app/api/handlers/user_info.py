from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import Users
from app.api.handlers.get_user import get_user_by_phone

async def get_contract_number_from_db(phone: str, session: AsyncSession): 
    user = await get_user_by_phone(phone, session)
    return user.contract_number
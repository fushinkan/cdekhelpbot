from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.handlers.get_user import UserInDB

async def get_contract_number_from_db(phone: str, session: AsyncSession): 
    user = await UserInDB.get_client_by_phone(phone, session)
    return user.contract_number
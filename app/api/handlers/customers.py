from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import Users
from app.db.models.phone_numbers import PhoneNumbers

class Customers:
    
    
    @classmethod
    async def get_customers_pagination(cls, *, session: AsyncSession, page: int = 1, per_page: int = 10):
        
        offset = (page - 1) * per_page
        
        result = await session.execute(
            select(Users)
            .options(selectinload(Users.phones))
            .offset(offset)
            .limit(per_page)
        )
        
        clients = result.scalars().all()
        
        total_result = await session.execute(
            select(func.count(Users.id))
        )
        
        total_clients = total_result.scalar_one()
        
        return clients, total_clients
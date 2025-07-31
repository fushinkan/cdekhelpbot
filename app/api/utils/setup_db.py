# Временная функция для импорта данных из Excel в БД

import asyncio
from fastapi import Depends
from docx import Document
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_session, async_session_factory
from app.db.models.users import Users
from app.db.models.phone_numbers import PhoneNumbers

async def setup_db():
    session_gen = get_session()
    session = await session_gen.__anext__()
    try:
        doc = Document("/home/fushinkan/Desktop/customers.docx")
        
        table = doc.tables[0]
        
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            
            contract_number, city, contractor, phone_number, psw, role = cells
            
            user = Users(
                contract_number=contract_number,
                city=city,
                contractor=contractor,
                phone_number=phone_number,
                hashed_psw=psw,
                role=role
            )
            session.add(user)
    finally:
        await session.commit()
        await session_gen.aclose()
        
        
async def migrate_phone_numbers():
    async with async_session_factory() as session:
        result = await session.execute(
            select(Users)
        )
        
        users = result.scalars().all()
        
        for user in users:
            if user.phone_number:
                numbers = [p.strip() for p in user.phone_number.split(',') if p.strip()]
                for number in numbers:
                    session.add(PhoneNumbers(user_id=user.id, number=number))
        await session.commit()
        
if __name__ == "__main__":
    asyncio.run(migrate_phone_numbers())
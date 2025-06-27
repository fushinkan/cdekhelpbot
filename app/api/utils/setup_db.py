from docx import Document

from app.db.base import get_session
from app.db.models.users import Users


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
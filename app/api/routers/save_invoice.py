from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.schemas.invoice import SaveInvoiceSchema
from app.api.handlers.invoice import InvoiceService


router = APIRouter(prefix="/invoices", tags=["Invoice"])


@router.post("/save_invoice/{user_id}", status_code=status.HTTP_201_CREATED)
async def save_invoice_endpoint(user_id: int, data: SaveInvoiceSchema, session: AsyncSession = Depends(get_session)):
    
    await InvoiceService.save_invoice(
        user_id=user_id,
        departure_city=data.departure_city,
        recipient_city=data.recipient_city,
        invoice_number=data.invoice_number,
        telegram_file_id=data.telegram_file_id,
        session=session
    )
    
    return {"message": f"Invoice saved for user: {user_id}"}
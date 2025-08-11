from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.schemas.invoice import SaveInvoiceSchema
from app.api.services.invoice import InvoiceService


router = APIRouter(prefix="/invoices", tags=["Invoice"])


@router.post("/save_invoice/{user_id}", status_code=status.HTTP_201_CREATED)
async def save_invoice_endpoint(user_id: int, data: SaveInvoiceSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для сохранения накладной в БД для конкретного пользователя (user).

    Args:
        user_id (int): ID пользователя из БД.
        data (SaveInvoiceSchema): Pydantic-схема для валидации данных.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Returns:
        dict: Сообщение о сохранении накладной для пользователя с конкретным user_id.
    """
    
    await InvoiceService.save_invoice(
        user_id=user_id,
        departure_city=data.departure_city,
        recipient_city=data.recipient_city,
        invoice_number=data.invoice_number,
        telegram_file_id=data.telegram_file_id,
        session=session
    )
    
    return {"message": f"Invoice saved for user: {user_id}"}
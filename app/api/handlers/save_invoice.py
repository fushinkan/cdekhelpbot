from app.db.base import AsyncSession
from app.db.models.invoices import Invoice


async def save_invoice(*, user_id: int, departure_city: str, recipient_city: str, invoice_number: str, telegram_file_id: str, session: AsyncSession):
    """
    Сохраняет накладную пользователя в БД

    Args:
        departure_city (str): Город отправителя.
        recipient_city (str): Город получателя.
        invoice_number (str): Номер накладной
        session (AsyncSession): Сессия подключения к БД (по умолчанию взята из настроек).
    """
    
    new_invoice = Invoice(
        user_id=user_id,
        departure_city=departure_city,
        recipient_city=recipient_city,
        invoice_number=invoice_number,
        telegram_file_id=telegram_file_id
    )
    
    session.add(new_invoice)
    await session.commit()
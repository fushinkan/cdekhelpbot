from app.db.base import AsyncSession
from app.db.models.invoices import Invoice


class InvoiceService:
    """Класс с методами для управления накладными."""
    
    @classmethod
    async def save_invoice(cls, *, user_id: int, departure_city: str, recipient_city: str, invoice_number: str, telegram_file_id: str, session: AsyncSession):
        """
        Метод сохраняет созданную накладную для конкретного пользователя (user) по его ID.

        Args:
            user_id (int): ID пользователя из БД.
            departure_city (str): Город отправления, в названии файла.
            recipient_city (str): Город получения, в названии файла.
            invoice_number (str): Номер накладной, в названии файла.
            telegram_file_id (str): ID файла в Telegram.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

from app.db.models.invoices import Invoice
from bot.utils.exceptions import EmptyHistoryException

from decimal import Decimal


class History:
    """
    Класс с методом просмотра истории заказов.
    """
    
    @classmethod
    async def get_user_order_history_all_years(cls, *, user_id: int, session: AsyncSession):
        """
        Метод достает все года заказов для конкретного пользователя.

        Args:
            user_id (int): ID пользователя из БД.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        year_alias = func.extract("year", Invoice.created_at).label("year")

        result = await session.execute(
            select(year_alias)
            .where(Invoice.user_id == user_id)
            .distinct()
            .order_by(year_alias)
        )
        
        years = [int(year) if isinstance(year, Decimal) else year for year in result.scalars().all()]
        
        if not years:
            raise EmptyHistoryException(EmptyHistoryException.__doc__)
        
        return years[-5:]
    
    
    @classmethod
    async def get_user_order_months_by_year(cls, *, user_id: int, year: int, session: AsyncSession):
        """
        Метод для получения месяцев по году заказа для конкретного пользователя.

        Args:
            user_id (int): ID пользователя из БД.
            year (int): Год заказа.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        month_alias = func.extract("month", Invoice.created_at).label("month")

        result = await session.execute(
            select(month_alias)
            .where(
                Invoice.user_id == user_id,
                extract("year", Invoice.created_at) == year
            )
            .distinct()
            .order_by(month_alias)
        )
        
        months = [int(month) if isinstance(month, Decimal) else month for month in result.scalars().all()]
        
        if not months:
            raise EmptyHistoryException(EmptyHistoryException.__doc__)
        
        return months

    
    @classmethod
    async def get_user_invoices_by_month_year(
        cls,
        *,
        user_id: int,
        year: int,
        month: int,
        session: AsyncSession
    ):
        """
        Получить список накладных пользователя за конкретный год и месяц.

        Возвращает список накладных с номером и telegram_file_id.

        Args:
            user_id (int): ID пользователя из БД.
            year (int): Год заказа.
            month (int): Месяц заказа.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

        Returns:
            dict: {"user_id": ..., "year": ..., "month": ..., "invoices": [{"departure_city": ..., "recipient_city": ..., "invoice_id": ...}, ...]}
        """
        
        result = await session.execute(
            select(
                Invoice.departure_city,
                Invoice.recipient_city,
                Invoice.id,
                Invoice.created_at
            ).where(
                Invoice.user_id == user_id,
                extract('year', Invoice.created_at) == year,
                extract('month', Invoice.created_at) == month
            ).order_by(Invoice.created_at.desc())
        )
        
        invoices = result.all()
        
        if not invoices:
            raise EmptyHistoryException(EmptyHistoryException.__doc__)
        
        # Формируем список словарей с нужными полями
        return [
            {
                "departure_city": dep,
                "recipient_city": rec,
                "invoice_id": inv_id,
                "created_at": created_at.isoformat()  
            }
            for dep, rec, inv_id, created_at in invoices
        ]


    @classmethod
    async def get_user_invoice_by_id(cls, *, invoice_id: int, session: AsyncSession):
        """
        Метод скачивает выбранную накладную.

        Args:
            invoice_id (int): Номер накладной из БД.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        result = await session.execute(
            select(Invoice.telegram_file_id)
            .where(Invoice.id == invoice_id)
        )
        
        telegram_file_id = result.scalar_one_or_none()
        
        return telegram_file_id
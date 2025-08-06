from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.api.handlers.history import History
from bot.utils.exceptions import EmptyHistoryException


router = APIRouter(prefix="/history", tags=["History"])
        
    
@router.get("/download/{invoice_id}", status_code=status.HTTP_200_OK)
async def download_invoice_endpoint(invoice_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт скачивает выбранную накладную.

    Args:
        invoice_id (int): Номер накладной из БД.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    telegram_file_id = await History.get_user_invoice_by_id(invoice_id=invoice_id, session=session)
    
    if not telegram_file_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ошибка скачивания. Попробуйте позже"
        )
        
    print(f"Отдаем telegram_file_id: {telegram_file_id} для invoice_id={invoice_id}")
        
    return {"telegram_file_id": telegram_file_id}


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_order_history_all_years(user_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения истории заказов для конкретного пользователя.

    Args:
        user_id (int): ID пользователя из БД.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """

    try:
        years = await History.get_user_order_history_all_years(user_id=user_id, session=session)
        return {"user_id": user_id, "order_years": years}
    
    except EmptyHistoryException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        

@router.get("/{user_id}/{year}", status_code=status.HTTP_200_OK)
async def get_user_order_months_by_year_endpoint(user_id: int, year: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения месяцев по году заказа для конкретного пользователя.

    Args:
        user_id (int): ID пользователя из БД.
        year (int): Год заказа
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    try:
        months = await History.get_user_order_months_by_year(user_id=user_id, year=year, session=session)
        return {"user_id": user_id, "order_months": months}
    
    except EmptyHistoryException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
        

@router.get("/{user_id}/{year}/{month}", status_code=status.HTTP_200_OK)
async def get_user_invoices_by_month_year_endpoint(
    user_id: int,
    year: int,
    month: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список накладных пользователя за конкретный год и месяц.

    Возвращает список: отправление, получение, ID накладной.

    Returns:
        {
            "user_id": ID пользователя из БД.
            "year": Год заказа.
            "month": Месяц заказа.
            "invoices": Список заказов. [
                {
                    "departure_city": "...",
                    "recipient_city": "...",
                    "invoice_id": ...
                },
                ...
            ]
        }
    """
    
    try:
        invoices = await History.get_user_invoices_by_month_year(
            user_id=user_id,
            year=year,
            month=month,
            session=session
        )

        invoices = await History.get_user_invoices_by_month_year(
            user_id=user_id,
            year=year,
            month=month,
            session=session
        )

        return {
            "user_id": user_id,
            "year": year,
            "month": month,
            "invoices": invoices 
        }

    except EmptyHistoryException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

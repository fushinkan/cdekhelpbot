from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.api.handlers.customers import Customers
from app.schemas.users import PaginateUserResponse

import math


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/all_customers", status_code=status.HTTP_200_OK)
async def get_customers_pagination_endpoint(page: int = 1, per_page: int = 10, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения всех клиентов у админа с пагинацией.

    Args:
        page (int, optional): Стартовая страница для пагинации. Defaults to 1.
        per_page (int, optional): Лимит пользователей на странице. Defaults to 10.
        session (AsyncSession, optional): Асинхронная сессия. По умолчанию берется из настроек через DI.

    Returns:
        dict: Pydantic-схема преобразованная к словарю.
    """
    clients, total_clients = await Customers.get_customers_pagination(
        page=page,
        per_page=per_page,
        session=session
    )
    
    total_pages = math.ceil(total_clients / per_page)
    
    response = PaginateUserResponse(
        per_page=per_page,
        page=page,
        total=total_clients,
        total_pages=total_pages,
        users=clients
    )
    
    return response.model_dump()
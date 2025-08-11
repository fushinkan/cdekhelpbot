from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.users import Users
from app.db.base import get_session
from app.api.services.customers import Customers
from app.schemas.users import PaginateUserResponse
from app.schemas.customers import CustomerResponseSchema, CustomerInputSchema
from app.schemas.auth import PhoneResponseSchema
from bot.utils.exceptions import CustomerAlreadyExistsException

import math


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/all_customers", status_code=status.HTTP_200_OK)
async def get_customers_pagination_endpoint(page: int = 1, per_page: int = 10, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения всех клиентов у админа с пагинацией.

    Args:
        page (int, optional): Стартовая страница для пагинации. Defaults to 1.
        per_page (int, optional): Лимит пользователей на странице. Defaults to 10.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.

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


@router.post("/add_customer", status_code=status.HTTP_201_CREATED, response_model=CustomerResponseSchema)
async def add_customer_endpoint(customer: CustomerInputSchema, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для добавления нового контрагента в таблицу Users и его номеров телефона в таблицу PhoneNumbers.

    Args:
        customer (CustomerInputSchema): Pydantic-схема для валидации данных.
        session (AsyncSession: Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    try:
        phone_numbers = [phone.phone_number.strip() for phone in customer.number]
        
        await Customers.add_customer(
            contractor=customer.contractor,
            contract_number=customer.contract_number,
            city=customer.city,
            number=phone_numbers,
            session=session
        )
        
    except CustomerAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    result = await session.execute(
        select(Users)
        .options(selectinload(Users.phones))
        .where(Users.contract_number == customer.contract_number)
    )
    
    user = result.scalar_one()
    
    phones_response = [PhoneResponseSchema.model_validate(phone) for phone in user.phones]
    
    return CustomerResponseSchema(
        id=user.id,
        contractor=user.contractor,
        contract_number=user.contract_number,
        city=user.city,
        number=phones_response
    )
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.phone_numbers import PhoneNumbers
from app.db.models.users import Users
from bot.utils.exceptions import CustomerAlreadyExistsException


class Customers:
    """
    Класс с пагинацией для получения всех клиентов для менеджера.

    Returns:
        ORM-модель: Таблица Users и кол-во пользователей в ней.
    """
    
    @classmethod
    async def get_customers_pagination(cls, *, session: AsyncSession, page: int = 1, per_page: int = 10):
        """
        Пагинация для просмотра всех клиентов у менеджера.

        Args:
            session (AsyncSession): Асинхронная сессия. По умолчанию береться из настроек через DI.
            page (int, optional): Стартовая страница для пагинации. Defaults to 1.
            per_page (int, optional): Лимит пользователей на странице. Defaults to 10.

        Returns:
            Users, Func(COUNT): ORM-Модель Users и кол-во записей в ней.
        """
        
        offset = (page - 1) * per_page
        
        result = await session.execute(
            select(Users)
            .options(selectinload(Users.phones))
            .offset(offset)
            .limit(per_page)
        )
        
        clients = result.scalars().all()
        
        total_result = await session.execute(
            select(func.count(Users.id))
        )
        
        total_clients = total_result.scalar_one()
        
        return clients, total_clients

    
    @classmethod
    async def add_customer(cls, *, contractor: str, city: str, contract_number: str, number: list[str], session: AsyncSession):
        """
        Добавляет нового контрагента в таблицу Users и номера телефонов в таблицу Phone_Numbers.

        Args:
            contractor (str): Имя контрагента.
            city (str): Город контрагента.
            contract_number (str): Номер договора контрагента.
            number (list[str]): Список номеров телефона контрагента.
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        result_user = await session.execute(
            select(Users)
            .where(Users.contract_number == contract_number)
        )
        
        existing_user = result_user.scalar_one_or_none()
        
        if existing_user:
            raise CustomerAlreadyExistsException(CustomerAlreadyExistsException.__doc__)
        
        new_user = Users(
            contract_number=contract_number,
            contractor=contractor,
            city=city
        )
        
        session.add(new_user)
        await session.flush()
        
        phone_objs = [
            PhoneNumbers(user_id=new_user.id, number=phone.strip())
            for phone in number
        ]
        
        session.add_all(phone_objs)
        
        await session.commit()
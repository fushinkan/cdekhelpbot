from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.users import Users


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
            _type_: _description_
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
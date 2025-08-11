from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.tariffs import Tariffs


class Tariff:
    """
    Класс для с методами для получения информации о тарифах.
    """
    
    @classmethod
    async def get_main_tariffs_titles(cls, *, session: AsyncSession):
        """
        Метод для получения названий тарифов.

        Args:
            sesson (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        subtariffs = {"«FBO | FBW | FBY»", "«FBS | rFBS»", "«DBS»"}
        
        result = await session.execute(
            select(Tariffs.title)
            .where(Tariffs.title.notin_(subtariffs))
        )
        
        main_titles = result.scalars().all()
        
        return main_titles


    @classmethod
    async def get_sub_tariffs_titles(cls, *, session: AsyncSession):
        """
        Метод для получения названий тарифов.

        Args:
            sesson (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        subtariffs = {"«FBO | FBW | FBY»", "«FBS | rFBS»", "«DBS»"}
        
        result = await session.execute(
            select(Tariffs.title)
            .where(Tariffs.title.in_(subtariffs))
        )
        
        sub_titles = result.scalars().all()
        
        return sub_titles
    

    @classmethod
    async def get_tariffs_description(cls, *, session: AsyncSession, title: str):
        """
        Метод для получения описания тарифов.

        Args:
            sesson (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        result = await session.execute(
            select(Tariffs.description)
            .where(Tariffs.title == title)
        )
        
        description = result.scalar_one_or_none()
        
        return description
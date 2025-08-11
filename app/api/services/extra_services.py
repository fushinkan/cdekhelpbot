from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.extra_services import ExtraServices

class ExtraService:
    """
    """
    
    @classmethod
    async def get_extra_services_titles(cls, *, session: AsyncSession):
        """
        Метод для получения названий дополнительных услуг.

        Args:
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
        """
        
        result = await session.execute(select(ExtraServices.title))
        
        extra_services_titles = result.scalars().all()
        
        return extra_services_titles
    
    
    @classmethod
    async def get_extra_services_description(cls, *, session: AsyncSession, title: str):
        """
        Метод для получения описания для дополнительных услуг.

        Args:
            session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
            title (str): Название дополнительной услуги.
        """
        
        result = await session.execute(
            select(ExtraServices.description)
            .where(ExtraServices.title == title)
        )
        
        description = result.scalar_one_or_none()
        
        return description
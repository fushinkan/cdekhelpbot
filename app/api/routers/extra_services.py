from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.api.handlers.extra_services import ExtraService
from bot.utils.exceptions import TariffNotExistException


router = APIRouter(prefix="/extra_services", tags=["Extra Services"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_extra_services_titles_endpoint(session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения названий дополнительных услуг.

    Args:
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    extra_services_titles = await ExtraService.get_extra_services_titles(session=session)
    
    return extra_services_titles


@router.get("/{title}", status_code=status.HTTP_200_OK)
async def get_extra_services_description_endpoint(title: str, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения описания дополнительных услуг.

    Args:
        title (str): Название дополнительной услуги
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    description = await ExtraService.get_extra_services_description(title=title, session=session)
    
    if description is None:
        raise TariffNotExistException(TariffNotExistException.__doc__)
    
    return {"title": title, "description": description}
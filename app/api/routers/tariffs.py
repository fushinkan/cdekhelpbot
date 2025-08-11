from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_session
from app.api.services.tariffs import Tariff
from bot.utils.exceptions import TariffNotExistException


router = APIRouter(prefix="/tariffs", tags=["Tariffs"])


@router.get("/main", status_code=status.HTTP_200_OK)
async def get_main_tariffs_titles_endpoint(session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения названий тарифов из БД.

    Args:
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    main_titles = await Tariff.get_main_tariffs_titles(session=session)
    
    return main_titles


@router.get("/sub", status_code=status.HTTP_200_OK)
async def get_sub_tariffs_titles_endpoint(session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения названий тарифов из БД.

    Args:
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI.
    """
    
    sub_titles = await Tariff.get_sub_tariffs_titles(session=session)
    
    return sub_titles


@router.get("/{title}")
async def read_tariff_description(title: str, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для чтения описания тарифов.

    Args:
        title (str): Название тарифа поступащее из callback-объекта в Telegram-боте.
        session (AsyncSession): Асинхронная сессия. По умолчанию берется из настроек через DI. 
    """
    
    description = await Tariff.get_tariffs_description(title=title, session=session)
    
    if description is None:
        raise TariffNotExistException(TariffNotExistException.__doc__)
    
    return {"title": title, "description": description}
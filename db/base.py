from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import settings


async_engine = create_async_engine(url=settings.get_db)
async_session_factory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False
)


# Session Generator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as conn:
        yield conn
    

class Base(DeclarativeBase):
    """
    Базовый класс всех моделей.
    """
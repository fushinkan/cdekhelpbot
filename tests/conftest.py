import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.config import settings
from app.db.base import Base, get_session


@pytest_asyncio.fixture(scope="function")
async def test_async_engine():
    engine = create_async_engine(url=settings.get_test_db, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_async_session(test_async_engine):
    yield async_sessionmaker(bind=test_async_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_async_session):
    async with test_async_session() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture(scope="function")
async def db_session_commit(test_async_session):
    async with test_async_session() as session:
        yield session  


@pytest_asyncio.fixture()
async def test_client(db_session_commit: AsyncSession):
    async def override_session():
        yield db_session_commit

    app.dependency_overrides[get_session] = override_session

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


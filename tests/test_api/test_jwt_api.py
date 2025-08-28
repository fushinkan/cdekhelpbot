import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.users import Users


@pytest.mark.asyncio
async def test_save_tokens_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(
        telegram_id=123,
        telegram_name="testuser",
        contract_number="C100",
        city="Moscow",
        contractor="Company"
    )
    db_session_commit.add(user)
    await db_session_commit.commit()
    await db_session_commit.refresh(user)

    data = {
        "user_id": user.id,
        "access_token": "access123",
        "refresh_token": "refresh123"
    }
    response = await test_client.post("/tokens/", json=data)

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "ok"
    assert body["user_id"] == user.id


@pytest.mark.asyncio
async def test_get_access_token_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(
        telegram_id=124,
        telegram_name="testuser2",
        contract_number="C101",
        city="SPB",
        contractor="Company2",
        access_token="access_token_test",
        refresh_token="refresh_token_test"
    )
    db_session_commit.add(user)
    await db_session_commit.commit()
    await db_session_commit.refresh(user)

    response = await test_client.get(f"/tokens/{user.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access_token_test"

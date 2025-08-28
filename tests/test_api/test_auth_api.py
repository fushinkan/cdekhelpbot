import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.security import Security
from app.db.models.users import Users
from app.db.models.phone_numbers import PhoneNumbers


@pytest.mark.asyncio
async def test_set_password_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(contract_number="KU-ABC7-10", city="TestCity", contractor="Contractor", role="user")
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    response = await test_client.put("/auth/set_password", json={
        "user_id": user.id,
        "plain_password": "secretpassword123"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "Password saved"


@pytest.mark.asyncio
async def test_confirm_password_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(contract_number="KU-ABC7-10", city="TestCity", contractor="Contractor", role="user")
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    await test_client.put("/auth/set_password", json={
        "user_id": user.id,
        "plain_password": "secretpassword123"
    })

    response = await test_client.put("/auth/confirm_password", json={
        "user_id": user.id,
        "confirm_password": "secretpassword123",
        "is_change": False,
        "telegram_id": 12345,
        "telegram_name": "testuser"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password is set"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_accept_enter_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(
        contract_number="333",
        city="TestCity",
        contractor="Contractor",
        role="user",
        hashed_psw=Security.hashed_password(password="secretpassword123")
    )
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    response = await test_client.post("/auth/accept_enter", json={
        "user_id": user.id,
        "password": "secretpassword123",
        "phone_number": "79000000000",
        "telegram_id": 54321,
        "telegram_name": "tester"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged in"
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_update_login_status_endpoint(test_client, db_session_commit: AsyncSession):
    user = Users(contract_number="KU-ABC7-10", city="TestCity", contractor="Contractor", role="user")
    db_session_commit.add(user)
    await db_session_commit.commit()

    response = await test_client.put(f"/auth/user/{user.id}/login_status", json={"is_logged": True})

    assert response.status_code == 204
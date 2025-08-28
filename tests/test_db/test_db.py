import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.users import Users
from app.db.models.phone_numbers import PhoneNumbers
from app.db.models.invoices import Invoice
from app.api.utils.security import Security
from app.api.services.auth import AuthService
from bot.utils.exceptions import UserNotExistsException, IncorrectPasswordException, AlreadyLoggedException


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user = Users(
        telegram_name="testuser",
        telegram_id=123,
        city="Москва",
        contractor="Компания",
        contract_number="KU-ABC7-10",
        hashed_psw=Security.hashed_password(password="secretpassword123"),
        role="user"
    )
    
    phone = PhoneNumbers(
        number="79803529673",
        user=user
    )

    db_session.add(user)
    db_session.add(phone)

    await db_session.flush()

    refreshed_user = await db_session.scalar(
        select(Users)
        .options(selectinload(Users.phones))
        .where(Users.id == user.id)
    )

    assert refreshed_user.id is not None
    assert refreshed_user.is_logged is False
    assert refreshed_user.role == "user"
    assert len(refreshed_user.phones) > 0
    assert refreshed_user.phones[0].number == "79803529673"
    
@pytest.mark.asyncio
async def test_save_invoice(db_session: AsyncSession):
    user = Users(
        telegram_name="testuser",
        telegram_id=123,
        city="Москва",
        contractor="Компания",
        contract_number="KU-ABC7-10",
        hashed_psw=Security.hashed_password(password="secretpassword123"),
        role="user"
    )
    db_session.add(user)
    await db_session.flush()

    invoice = Invoice(
        telegram_file_id = "123",
        departure_city="Москва",
        recipient_city="Липецк",
        invoice_number="12345",
        user=user
    )

    db_session.add(invoice)
    await db_session.flush()
    
    saved_invoice = await db_session.scalar(
        select(Invoice).where(Invoice.user_id == user.id)
    )

    assert saved_invoice is not None
    assert saved_invoice.user_id == user.id
    assert saved_invoice.departure_city == "Москва"
    assert saved_invoice.recipient_city == "Липецк"
    assert saved_invoice.invoice_number == "12345"
    assert saved_invoice.telegram_file_id == "123"
    

@pytest.mark.asyncio
async def test_update_login_status(db_session: AsyncSession):
    user = Users(
        contractor="пользователь из теста статуса",
        city="Липецк",
        contract_number="KU-ABC7-10",
        role="user",
        is_logged=False
    )
    
    db_session.add(user)
    await db_session.flush()
    
    updated_user = await AuthService.update_login_status(
        session=db_session,
        is_logged=True,
        role="user",
        user_id=user.id
    )
    
    assert updated_user.is_logged is True


@pytest.mark.asyncio
async def test_set_password(db_session_commit: AsyncSession):
    user = Users(
        contract_number="KU-ABC7-10",
        city="TestCity",
        contractor="TestContractor",
        role="user"
    )
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    result = await AuthService.set_password(
        user_id=user.id,
        plain_password="test123",
        session=db_session_commit
    )

    assert result is True
    assert user.id in AuthService._temp_passwords


@pytest.mark.asyncio
async def test_confirm_password(db_session_commit: AsyncSession):
    user = Users(
        contract_number="KU-ABC7-10",
        city="TestCity",
        contractor="TestContractor",
        role="user"
    )
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    await AuthService.set_password(
        user_id=user.id,
        plain_password="mypassword",
        session=db_session_commit
    )

    access_token, refresh_token = await AuthService.confirm_password(
        user_id=user.id,
        confirm_password="mypassword",
        session=db_session_commit
    )

    assert access_token is not None
    assert refresh_token is not None

    await db_session_commit.refresh(user)
    assert user.is_logged is True
    assert Security.verify_password(plain_password="mypassword", hashed_password=user.hashed_psw)


@pytest.mark.asyncio
async def test_accept_enter(db_session_commit: AsyncSession):
    user = Users(
        contract_number="KU-ABC7-10",
        city="TestCity",
        contractor="TestContractor",
        role="user",
        hashed_psw=Security.hashed_password(password="secretpassword123")
    )
    db_session_commit.add(user)
    await db_session_commit.flush()

    phone = PhoneNumbers(user_id=user.id, number="79000000000")
    db_session_commit.add(phone)
    await db_session_commit.commit()

    access_token, refresh_token = await AuthService.accept_enter(
        user_id=user.id,
        password="secretpassword123",
        session=db_session_commit
    )

    assert access_token is not None
    assert refresh_token is not None

    await db_session_commit.refresh(user)
    assert user.is_logged is True


@pytest.mark.asyncio
async def test_accept_enter_incorrect_password(db_session_commit: AsyncSession):
    user = Users(
        contract_number="KU-ABC7-10",
        city="TestCity",
        contractor="TestContractor",
        role="user",
        hashed_psw=Security.hashed_password(password="rightpass")
    )
    db_session_commit.add(user)
    await db_session_commit.commit()

    with pytest.raises(IncorrectPasswordException):
        await AuthService.accept_enter(
            user_id=user.id,
            password="wrongpass",
            session=db_session_commit
        )


@pytest.mark.asyncio
async def test_accept_enter_already_logged(db_session_commit: AsyncSession):
    user = Users(
        contract_number="KU-ABC7-10",
        city="TestCity",
        contractor="TestContractor",
        role="user",
        hashed_psw=Security.hashed_password(password="secretpassword123"),
        is_logged=True
    )
    db_session_commit.add(user)
    await db_session_commit.commit()

    with pytest.raises(AlreadyLoggedException):
        await AuthService.accept_enter(
            user_id=user.id,
            password="secretpassword123",
            session=db_session_commit
        )

import pytest

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.users import Users
from app.db.models.phone_numbers import PhoneNumbers


@pytest.mark.asyncio
async def test_add_customer_endpoint(test_client, db_session_commit: AsyncSession):
    response = await test_client.post("/customers/add_customer", json={
        "contractor": "ООО Компания",
        "contract_number": "KU-ABC7-10",
        "city": "Липецк",
        "number": [{"phone_number": "79000000000"}, {"phone_number": "79999999999"}]
    })
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["contractor"] == "ООО Компания"
    assert data["contract_number"] == "KU-ABC7-10"
    assert data["city"] == "Липецк"
    assert len(data["number"]) == 2
    assert data["number"][0]["number"] == "79000000000"
    
    saved_user = await db_session_commit.scalar(
        select(Users).options(selectinload(Users.phones))
        .where(Users.contract_number == "KU-ABC7-10")
    )
    
    assert saved_user is not None
    assert saved_user.contractor == "ООО Компания"
    assert len(saved_user.phones) == 2


@pytest.mark.asyncio
async def test_get_customers_pagination_endpoint(test_client, db_session: AsyncSession):
    users_data = [
        {
            "telegram_id": 1001,
            "telegram_name": "user1",
            "contract_number": "KU-ABC7-10",
            "city": "Moscow",
            "contractor": "Company A",
            "phones": ["+79000000001", "+79000000002"]
        },
        {
            "telegram_id": 1002,
            "telegram_name": "user2",
            "contract_number": "KU-ABC7-11",
            "city": "SPB",
            "contractor": "Company B",
            "phones": ["+79000000003"]
        },
        {
            "telegram_id": 1003,
            "telegram_name": "user3",
            "contract_number": "KU-ABC7-12",
            "city": "Kazan",
            "contractor": "Company C",
            "phones": ["+79000000004"]
        },
    ]

    for user in users_data:
        db_user = Users(
            telegram_id=user["telegram_id"],
            telegram_name=user["telegram_name"],
            contract_number=user["contract_number"],
            city=user["city"],
            contractor=user["contractor"],
        )
        db_session.add(db_user)
        await db_session.flush()

        for phone in user["phones"]:
            db_session.add(PhoneNumbers(user_id=db_user.id, number=phone))

    await db_session.commit()


    response = await test_client.get("/customers/all_customers?page=1&per_page=2")
    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["per_page"] == 2
    assert data["total"] == 3
    assert data["total_pages"] == 2
    assert len(data["users"]) == 2  

    first_user = data["users"][0]
    assert "telegram_name" in first_user
    assert "phones" in first_user

    response_page2 = await test_client.get("/customers/all_customers?page=2&per_page=2")
    assert response_page2.status_code == 200
    data_page2 = response_page2.json()

    assert data_page2["page"] == 2
    assert len(data_page2["users"]) == 1
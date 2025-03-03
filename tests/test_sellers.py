import pytest
from sqlalchemy import select
from src.models.sellers import Seller
from fastapi import status
import pytest_asyncio
import uuid


@pytest.mark.asyncio
async def test_create_seller(async_client, db_session):
    e_mail = f"testuser+{uuid.uuid4()}@example.com"
    
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": e_mail,
        "password": "password123"
    }
    
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_201_CREATED
    
    result = response.json()
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["e_mail"] == e_mail
    assert "id" in result
    
    db_seller = await db_session.get(Seller, result["id"])
    assert db_seller is not None
    assert db_seller.e_mail == e_mail


@pytest.mark.asyncio
async def test_create_seller_duplicate_email(async_client, db_session):
    e_mail = f"duplicate+{uuid.uuid4()}@example.com"
    
    seller = Seller(
        first_name="First",
        last_name="User",
        e_mail=e_mail,
        password="password123"
    )
    db_session.add(seller)
    await db_session.commit()
    
    data = {
        "first_name": "Second",
        "last_name": "User",
        "e_mail": e_mail,
        "password": "password123"
    }
    
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_create_seller_invalid_password(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": f"testuser+{uuid.uuid4()}@example.com",
        "password": "short"
    }
    
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_seller(async_client, db_session):
    e_mail = f"testuser+{uuid.uuid4()}@example.com"
    seller = Seller(
        first_name="John",
        last_name="Doe",
        e_mail=e_mail,
        password="password123"
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    
    response = await async_client.get(f"/api/v1/sellers/{seller.id}")
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert result["id"] == seller.id
    assert result["first_name"] == "John"
    assert result["last_name"] == "Doe"
    assert result["e_mail"] == e_mail


@pytest.mark.asyncio
async def test_get_nonexistent_seller(async_client):
    response = await async_client.get("/api/v1/sellers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_all_sellers(async_client, db_session):
    sellers = []
    for i in range(3):
        e_mail = f"user{i}+{uuid.uuid4()}@example.com"
        seller = Seller(
            first_name=f"User{i}",
            last_name=f"Last{i}",
            e_mail=e_mail,
            password="password123"
        )
        db_session.add(seller)
        sellers.append(seller)
    
    await db_session.commit()
    for seller in sellers:
        await db_session.refresh(seller)
    
    response = await async_client.get("/api/v1/sellers/")
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert isinstance(result, list)
    assert len(result) >= 3
    
    seller_ids = [s["id"] for s in result]
    for seller in sellers:
        assert seller.id in seller_ids


@pytest.mark.asyncio
async def test_update_seller(async_client, db_session):
    e_mail = f"user+{uuid.uuid4()}@example.com"
    seller = Seller(
        first_name="Original",
        last_name="Name",
        e_mail=e_mail,
        password="password123"
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    
    new_email = f"updated+{uuid.uuid4()}@example.com"
    update_data = {
        "first_name": "Updated",
        "last_name": "Person",
        "e_mail": new_email,
        "password": "newpassword123"
    }
    
    response = await async_client.put(f"/api/v1/sellers/{seller.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    
    result = response.json()
    assert result["first_name"] == "Updated"
    assert result["last_name"] == "Person"
    assert result["e_mail"] == new_email
    
    await db_session.refresh(seller)
    assert seller.first_name == "Updated"
    assert seller.last_name == "Person"
    assert seller.e_mail == new_email


@pytest.mark.asyncio
async def test_update_nonexistent_seller(async_client):
    update_data = {
        "first_name": "Updated",
        "last_name": "Person",
        "e_mail": "nonexistent@example.com",
        "password": "newpassword123"
    }
    
    response = await async_client.put("/api/v1/sellers/9999", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_seller(async_client, db_session):
    e_mail = f"delete+{uuid.uuid4()}@example.com"
    seller = Seller(
        first_name="To",
        last_name="Delete",
        e_mail=e_mail,
        password="password123"
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    
    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    result = await db_session.get(Seller, seller.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_nonexistent_seller(async_client):
    response = await async_client.delete("/api/v1/sellers/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
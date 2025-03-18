import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sellers import Seller
from src.utils.auth import create_access_token, hash_password


@pytest_asyncio.fixture
async def test_seller(db_session: AsyncSession):
    """Create a test seller with a hashed password."""
    seller = Seller(
        first_name="John",
        last_name="Doe",
        e_mail="test@example.com",
        password=hash_password("securepass123"),
    )
    db_session.add(seller)
    await db_session.commit()
    await db_session.refresh(seller)
    return seller


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_seller):
    """✅ Test successful login and token generation."""
    response = await async_client.post(
        "/api/v1/auth/token",
        json={"e_mail": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_failure_invalid_password(async_client: AsyncClient, test_seller):
    """❌ Test login failure with incorrect password."""
    response = await async_client.post(
        "/api/v1/auth/token",
        json={"e_mail": "test@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_failure_invalid_email(async_client: AsyncClient):
    """❌ Test login failure with non-existent email."""
    response = await async_client.post(
        "/api/v1/auth/token",
        json={"e_mail": "nonexistent@example.com", "password": "securepass123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_secure_endpoint_valid_token(async_client: AsyncClient, test_seller):
    """✅ Test secure endpoint access with valid JWT token."""
    token = create_access_token({"sub": test_seller.e_mail})
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/auth/secure-endpoint", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "You have access to this endpoint"
    assert response.json()["user"]["sub"] == "test@example.com"


@pytest.mark.asyncio
async def test_secure_endpoint_invalid_token(async_client: AsyncClient):
    """❌ Test secure endpoint failure with invalid JWT token."""
    headers = {"Authorization": "Bearer invalid_token"}

    response = await async_client.get("/api/v1/auth/secure-endpoint", headers=headers)

    assert response.status_code == 401

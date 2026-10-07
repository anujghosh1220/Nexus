import pytest
from httpx import AsyncClient
from app.schemas.user import UserCreate, UserLogin


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == user_data["email"]
    assert data["user"]["first_name"] == user_data["first_name"]
    assert data["user"]["is_verified"] is False


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test that duplicate email registration fails."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }

    # First registration
    await client.post("/api/v1/auth/register", json=user_data)

    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 409
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test that weak password registration fails."""
    user_data = {
        "email": "test@example.com",
        "password": "weak",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register user first
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Login
    login_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == login_data["email"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user information."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    access_token = register_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without authentication."""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh."""
    # Register
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    refresh_token = register_response.json()["refresh_token"]

    # Refresh tokens
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # New refresh token should be different (token rotation)
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout."""
    # Register
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }
    register_response = await client.post("/api/v1/auth/register", json=user_data)
    access_token = register_response.json()["access_token"]
    refresh_token = register_response.json()["refresh_token"]

    # Logout
    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_password_reset_flow(client: AsyncClient):
    """Test password reset flow."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Request password reset
    response = await client.post(
        "/api/v1/auth/request-password-reset",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 202

    # Note: In a real test, we would extract the token from the email
    # For now, we'll skip the actual reset since we don't have email sending

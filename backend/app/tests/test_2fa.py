import pytest
import pyotp
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_2fa_setup_generates_secret(client: AsyncClient):
    """Test 2FA setup generates secret."""
    user_data = {
        "email": "2fasetup@example.com",
        "password": "TestPassword123",
        "first_name": "2FA",
        "last_name": "Setup",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "secret" in data
    assert "qr_code_uri" in data
    assert data["issuer"] == "NEXUS"
    assert data["account"] == user_data["email"]


@pytest.mark.asyncio
async def test_2fa_setup_requires_authentication(client: AsyncClient):
    """Test that 2FA setup requires authentication."""
    response = await client.post("/api/v1/2fa/setup")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_2fa_enable_after_setup(client: AsyncClient):
    """Test enabling 2FA after setup."""
    user_data = {
        "email": "2faenable@example.com",
        "password": "TestPassword123",
        "first_name": "Enable",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]

    # Generate valid TOTP token
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    # Enable 2FA
    enable_response = await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert enable_response.status_code == 200
    data = enable_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["requires_2fa"] is False


@pytest.mark.asyncio
async def test_2fa_enable_with_invalid_token(client: AsyncClient):
    """Test enabling 2FA with invalid token fails."""
    user_data = {
        "email": "2fainvalid@example.com",
        "password": "TestPassword123",
        "first_name": "Invalid",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup 2FA
    await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Try to enable with invalid token
    response = await client.post(
        "/api/v1/2fa/enable",
        json={"token": "000000"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_with_2fa_enabled(client: AsyncClient):
    """Test login with 2FA enabled returns challenge."""
    user_data = {
        "email": "2falogin@example.com",
        "password": "TestPassword123",
        "first_name": "Login",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Login with correct password
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["requires_2fa"] is True
    assert "access_token" in data
    assert data["refresh_token"] == ""


@pytest.mark.asyncio
async def test_login_without_2fa_returns_normal_tokens(client: AsyncClient):
    """Test login without 2FA returns normal tokens."""
    user_data = {
        "email": "no2fa@example.com",
        "password": "TestPassword123",
        "first_name": "No",
        "last_name": "2FA",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["requires_2fa"] is False
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_2fa_verify_completes_login(client: AsyncClient):
    """Test 2FA verification completes login."""
    user_data = {
        "email": "2faverify@example.com",
        "password": "TestPassword123",
        "first_name": "Verify",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Login to get 2FA challenge token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    challenge_token = login_response.json()["access_token"]

    # Verify 2FA
    verify_response = await client.post(
        "/api/v1/2fa/verify",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {challenge_token}"}
    )
    assert verify_response.status_code == 200
    data = verify_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["requires_2fa"] is False


@pytest.mark.asyncio
async def test_2fa_verify_with_invalid_token(client: AsyncClient):
    """Test 2FA verification with invalid token fails."""
    user_data = {
        "email": "2fainvalidverify@example.com",
        "password": "TestPassword123",
        "first_name": "Invalid",
        "last_name": "Verify",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Login to get 2FA challenge token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    challenge_token = login_response.json()["access_token"]

    # Try to verify with invalid token
    response = await client.post(
        "/api/v1/2fa/verify",
        json={"token": "000000"},
        headers={"Authorization": f"Bearer {challenge_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_2fa_disable(client: AsyncClient):
    """Test disabling 2FA."""
    user_data = {
        "email": "2fadisable@example.com",
        "password": "TestPassword123",
        "first_name": "Disable",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Disable 2FA
    response = await client.post(
        "/api/v1/2fa/disable",
        json={"password": user_data["password"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify 2FA is disabled
    status_response = await client.get(
        "/api/v1/2fa/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert status_response.status_code == 200
    assert status_response.json()["enabled"] is False

    # Login should now return normal tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["requires_2fa"] is False
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_2fa_disable_with_wrong_password(client: AsyncClient):
    """Test disabling 2FA with wrong password fails."""
    user_data = {
        "email": "2fawrongpass@example.com",
        "password": "TestPassword123",
        "first_name": "Wrong",
        "last_name": "Pass",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Try to disable with wrong password
    response = await client.post(
        "/api/v1/2fa/disable",
        json={"password": "WrongPassword"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_2fa_status(client: AsyncClient):
    """Test getting 2FA status."""
    user_data = {
        "email": "2fastatus@example.com",
        "password": "TestPassword123",
        "first_name": "Status",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Check status before enabling
    response = await client.get(
        "/api/v1/2fa/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False

    # Setup and enable 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Check status after enabling
    response = await client.get(
        "/api/v1/2fa/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is True


@pytest.mark.asyncio
async def test_2fa_secret_not_exposed_in_user_response(client: AsyncClient):
    """Test that 2FA secret is not exposed in user response."""
    user_data = {
        "email": "2fasecret@example.com",
        "password": "TestPassword123",
        "first_name": "Secret",
        "last_name": "2FA",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    # Setup 2FA
    setup_response = await client.post(
        "/api/v1/2fa/setup",
        headers={"Authorization": f"Bearer {token}"}
    )
    secret = setup_response.json()["secret"]

    # Enable 2FA
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()

    await client.post(
        "/api/v1/2fa/enable",
        json={"token": valid_token},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Get user info
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    data = me_response.json()
    assert "totp_secret" not in data
    assert "totp_enabled" not in data

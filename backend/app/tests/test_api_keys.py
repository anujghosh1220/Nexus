import pytest
import json
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_api_key_requires_authentication(client: AsyncClient):
    """Test that creating API keys requires authentication."""
    response = await client.post("/api/v1/api-keys", json={
        "name": "Test Key",
        "organization_id": "org_123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_api_key_requires_membership(client: AsyncClient):
    """Test that creating API keys requires organization membership."""
    user_data = {
        "email": "apikeynonmember@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "NonMember",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "API Key Test Org",
        "slug": "api-key-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    non_member_data = {
        "email": "apikeynonmember2@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "NonMember2",
    }
    non_member_response = await client.post("/api/v1/auth/register", json=non_member_data)
    non_member_token = non_member_response.json()["access_token"]

    response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Test Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_api_key_requires_permission(client: AsyncClient):
    """Test that creating API keys requires proper role."""
    owner_data = {
        "email": "apikeyowner@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Permission Org",
        "slug": "api-key-permission-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    viewer_data = {
        "email": "apikeyviewer@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Viewer",
    }
    viewer_response = await client.post("/api/v1/auth/register", json=viewer_data)
    viewer_token = viewer_response.json()["access_token"]

    await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": viewer_response.json()["user"]["email"], "role": "VIEWER"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )

    response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Test Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_api_key_returns_plaintext_once(client: AsyncClient):
    """Test that creating API key returns plaintext key only once."""
    owner_data = {
        "email": "apikeycreate@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Create",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Create Org",
        "slug": "api-key-create-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    response = await client.post(
        "/api/v1/api-keys",
        json={"name": "My API Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "key" in data
    assert data["key"].startswith("nx_live_")
    assert len(data["key"]) == 40  # nx_live_ + 32 chars
    api_key_id = data["id"]

    # List should not contain plaintext
    list_response = await client.get(
        "/api/v1/api-keys",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["total"] == 1
    assert "key" not in list_data["items"][0]

    # Detail should not contain plaintext
    detail_response = await client.get(
        f"/api/v1/api-keys/{api_key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert detail_response.status_code == 200
    detail_data = detail_response.json()
    assert "key" not in detail_data


@pytest.mark.asyncio
async def test_api_key_authentication(client: AsyncClient):
    """Test that API key can be used for authentication."""
    owner_data = {
        "email": "apikeyauth@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Auth",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Auth Org",
        "slug": "api-key-auth-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create API key
    create_response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Auth Test Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    api_key = create_response.json()["key"]

    # Use API key to access protected endpoint
    auth_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert auth_response.status_code == 200
    assert auth_response.json()["email"] == owner_data["email"]


@pytest.mark.asyncio
async def test_api_key_invalid_or_revoked(client: AsyncClient):
    """Test that invalid or revoked API keys fail authentication."""
    owner_data = {
        "email": "apikeyinvalid@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Invalid",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Invalid Org",
        "slug": "api-key-invalid-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create API key
    create_response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Invalid Test Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    api_key_id = create_response.json()["id"]

    # Invalid key should fail
    invalid_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {api_key_id}"}
    )
    assert invalid_response.status_code == 401

    # Revoke key
    revoke_response = await client.post(
        f"/api/v1/api-keys/{api_key_id}/revoke",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert revoke_response.status_code == 200

    # Revoked key should fail
    revoked_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {create_response.json()['key']}"}
    )
    assert revoked_response.status_code == 401


@pytest.mark.asyncio
async def test_api_key_expiration(client: AsyncClient):
    """Test that expired API keys fail authentication."""
    owner_data = {
        "email": "apikeyexpired@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Expired",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Expired Org",
        "slug": "api-key-expired-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create API key with past expiration
    past_date = datetime.utcnow() - timedelta(days=1)
    create_response = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "Expired Key",
            "organization_id": org_id,
            "expires_at": past_date.isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    api_key = create_response.json()["key"]

    # Expired key should fail
    expired_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert expired_response.status_code == 401


@pytest.mark.asyncio
async def test_api_key_tenant_isolation(client: AsyncClient):
    """Test that API keys cannot access other organizations."""
    owner1_data = {
        "email": "apikeytenant1@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Tenant1",
    }
    owner1_response = await client.post("/api/v1/auth/register", json=owner1_data)
    owner1_token = owner1_response.json()["access_token"]

    org1_data = {
        "name": "API Key Tenant1 Org",
        "slug": "api-key-tenant1-org",
    }
    org1_response = await client.post(
        "/api/v1/organizations",
        json=org1_data,
        headers={"Authorization": f"Bearer {owner1_token}"}
    )
    org1_id = org1_response.json()["id"]

    owner2_data = {
        "email": "apikeytenant2@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Tenant2",
    }
    owner2_response = await client.post("/api/v1/auth/register", json=owner2_data)
    owner2_token = owner2_response.json()["access_token"]

    org2_data = {
        "name": "API Key Tenant2 Org",
        "slug": "api-key-tenant2-org",
    }
    org2_response = await client.post(
        "/api/v1/organizations",
        json=org2_data,
        headers={"Authorization": f"Bearer {owner2_token}"}
    )
    org2_id = org2_response.json()["id"]

    # Create API key for org1
    create_response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Tenant1 Key", "organization_id": org1_id},
        headers={"Authorization": f"Bearer {owner1_token}"}
    )
    api_key_id = create_response.json()["id"]
    api_key = create_response.json()["key"]

    # Org2 user should not see org1's API keys
    list_response = await client.get(
        "/api/v1/api-keys",
        params={"organization_id": org1_id},
        headers={"Authorization": f"Bearer {owner2_token}"}
    )
    assert list_response.status_code == 403

    # Org2 user should not be able to revoke org1's API key
    revoke_response = await client.post(
        f"/api/v1/api-keys/{api_key_id}/revoke",
        headers={"Authorization": f"Bearer {owner2_token}"}
    )
    assert revoke_response.status_code == 403


@pytest.mark.asyncio
async def test_api_key_last_used_at_updated(client: AsyncClient):
    """Test that last_used_at is updated when API key is used."""
    owner_data = {
        "email": "apikeylastused@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "LastUsed",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key LastUsed Org",
        "slug": "api-key-lastused-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    create_response = await client.post(
        "/api/v1/api-keys",
        json={"name": "LastUsed Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    api_key_id = create_response.json()["id"]

    # Use API key
    await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {create_response.json()['key']}"}
    )

    # Check last_used_at is set
    detail_response = await client.get(
        f"/api/v1/api-keys/{api_key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["last_used_at"] is not None


@pytest.mark.asyncio
async def test_api_key_revoke_idempotent(client: AsyncClient):
    """Test that revoking an already revoked key is idempotent."""
    owner_data = {
        "email": "apikeyidempotent@example.com",
        "password": "TestPassword123",
        "first_name": "API",
        "last_name": "Idempotent",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "API Key Idempotent Org",
        "slug": "api-key-idempotent-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    create_response = await client.post(
        "/api/v1/api-keys",
        json={"name": "Idempotent Key", "organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    api_key_id = create_response.json()["id"]

    # Revoke once
    revoke1 = await client.post(
        f"/api/v1/api-keys/{api_key_id}/revoke",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert revoke1.status_code == 200

    # Revoke again should succeed (idempotent)
    revoke2 = await client.post(
        f"/api/v1/api-keys/{api_key_id}/revoke",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert revoke2.status_code == 200

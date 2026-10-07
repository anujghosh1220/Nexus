import pytest
from httpx import AsyncClient
from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate


@pytest.mark.asyncio
async def test_tenant_isolation_user_cannot_access_other_org(client: AsyncClient):
    """Test that a user cannot access another organization's data."""
    # Create user A
    user_a_data = {
        "email": "usera@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "A",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]
    user_a_id = response_a.json()["user"]["id"]

    # Create organization A
    org_a_data = {
        "name": "Organization A",
        "slug": "org-a",
    }
    org_a = await client.post(
        "/api/v1/organizations",
        json=org_a_data,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    # Create user B
    user_b_data = {
        "email": "userb@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    # Create organization B
    org_b_data = {
        "name": "Organization B",
        "slug": "org-b",
    }
    org_b = await client.post(
        "/api/v1/organizations",
        json=org_b_data,
        headers={"Authorization": f"Bearer {token_b}"}
    )
    org_b_id = org_b.json()["id"]

    # User B tries to access Organization A (should fail)
    response = await client.get(
        f"/api/v1/organizations/{org_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_tenant_isolation_cannot_update_other_org(client: AsyncClient):
    """Test that a user cannot update another organization."""
    # Create user A and organization A
    user_a_data = {
        "email": "usera@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "A",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]

    org_a = await client.post(
        "/api/v1/organizations",
        json={"name": "Organization A", "slug": "org-a"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    # Create user B
    user_b_data = {
        "email": "userb@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    # User B tries to update Organization A (should fail)
    response = await client.patch(
        f"/api/v1/organizations/{org_a_id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tenant_isolation_cannot_delete_other_org(client: AsyncClient):
    """Test that a user cannot delete another organization."""
    # Create user A and organization A
    user_a_data = {
        "email": "usera@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "A",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]

    org_a = await client.post(
        "/api/v1/organizations",
        json={"name": "Organization A", "slug": "org-a"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    # Create user B
    user_b_data = {
        "email": "userb@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    # User B tries to delete Organization A (should fail)
    response = await client.delete(
        f"/api/v1/organizations/{org_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tenant_isolation_cannot_list_other_org_members(client: AsyncClient):
    """Test that a user cannot list members of another organization."""
    # Create user A and organization A
    user_a_data = {
        "email": "usera@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "A",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]

    org_a = await client.post(
        "/api/v1/organizations",
        json={"name": "Organization A", "slug": "org-a"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    # Create user B
    user_b_data = {
        "email": "userb@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    # User B tries to list Organization A members (should fail)
    response = await client.get(
        f"/api/v1/organizations/{org_a_id}/members",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_can_access_own_org(client: AsyncClient):
    """Test that a member can access their own organization."""
    # Create user and organization
    user_data = {
        "email": "user@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "Test",
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    token = response.json()["access_token"]

    org = await client.post(
        "/api/v1/organizations",
        json={"name": "Test Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org.json()["id"]

    # User should be able to access their own organization
    response = await client.get(
        f"/api/v1/organizations/{org_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == org_id

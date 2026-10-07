import pytest
from httpx import AsyncClient
from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.project import ProjectCreate, ProjectUpdate


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test project creation."""
    # Register user and create organization
    user_data = {
        "email": "owner@example.com",
        "password": "TestPassword123",
        "first_name": "Project",
        "last_name": "Owner",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]
    user_id = user_response.json()["user"]["id"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Test Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "organization_id": org_id,
        "name": "Test Project",
        "key": "TEST",
        "description": "A test project",
        "status": "ACTIVE",
    }
    response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["key"] == project_data["key"]
    assert data["organization_id"] == org_id
    assert data["owner_id"] == user_id


@pytest.mark.asyncio
async def test_create_project_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot create projects."""
    response = await client.post("/api/v1/projects", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    """Test listing projects in an organization."""
    # Register user and create organization
    user_data = {
        "email": "listuser@example.com",
        "password": "TestPassword123",
        "first_name": "List",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "List Org", "slug": "list-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create a project
    project_data = {
        "organization_id": org_id,
        "name": "List Project",
        "key": "LIST",
    }
    await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # List projects
    response = await client.get(
        f"/api/v1/projects?organization_id={org_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert data["items"][0]["name"] == "List Project"


@pytest.mark.asyncio
async def test_list_projects_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot list projects."""
    response = await client.get("/api/v1/projects?organization_id=org_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    """Test getting a project by ID."""
    # Register user and create organization
    user_data = {
        "email": "getuser@example.com",
        "password": "TestPassword123",
        "first_name": "Get",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Get Org", "slug": "get-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "organization_id": org_id,
        "name": "Get Project",
        "key": "GET",
    }
    create_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = create_response.json()["id"]

    # Get project
    response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Get Project"


@pytest.mark.asyncio
async def test_get_project_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot get projects."""
    response = await client.get("/api/v1/projects/proj_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    """Test updating a project."""
    # Register user and create organization
    user_data = {
        "email": "updateuser@example.com",
        "password": "TestPassword123",
        "first_name": "Update",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Update Org", "slug": "update-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "organization_id": org_id,
        "name": "Original Name",
        "key": "ORIG",
    }
    create_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = create_response.json()["id"]

    # Update project
    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
    }
    response = await client.patch(
        f"/api/v1/projects/{project_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_project_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot update projects."""
    response = await client.patch("/api/v1/projects/proj_123", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    """Test deleting a project."""
    # Register user and create organization
    user_data = {
        "email": "deleteuser@example.com",
        "password": "TestPassword123",
        "first_name": "Delete",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Delete Org", "slug": "delete-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "organization_id": org_id,
        "name": "Delete Project",
        "key": "DEL",
    }
    create_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = await client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify project is deleted
    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot delete projects."""
    response = await client.delete("/api/v1/projects/proj_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tenant_isolation_project(client: AsyncClient):
    """Test that users cannot access projects from other organizations."""
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

    # Create project in organization A
    project_a_data = {
        "organization_id": org_a_id,
        "name": "Project A",
        "key": "PRJA",
    }
    project_a = await client.post(
        "/api/v1/projects",
        json=project_a_data,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    project_a_id = project_a.json()["id"]

    # Create user B and organization B
    user_b_data = {
        "email": "userb@example.com",
        "password": "TestPassword123",
        "first_name": "User",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    org_b = await client.post(
        "/api/v1/organizations",
        json={"name": "Organization B", "slug": "org-b"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    org_b_id = org_b.json()["id"]

    # User B tries to get Organization A's project (should fail)
    response = await client.get(
        f"/api/v1/projects/{project_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    # User B tries to update Organization A's project (should fail)
    response = await client.patch(
        f"/api/v1/projects/{project_a_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    # User B tries to delete Organization A's project (should fail)
    response = await client.delete(
        f"/api/v1/projects/{project_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    # User B should not see Organization A's projects in list
    response = await client.get(
        f"/api/v1/projects?organization_id={org_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    # User A should be able to access their own project
    response = await client.get(
        f"/api/v1/projects/{project_a_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 200

    # User B can create their own project in their organization
    project_b_data = {
        "organization_id": org_b_id,
        "name": "Project B",
        "key": "PRJB",
    }
    response = await client.post(
        "/api/v1/projects",
        json=project_b_data,
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_project_invalid_key(client: AsyncClient):
    """Test that invalid project key is rejected."""
    # Register user and create organization
    user_data = {
        "email": "keyuser@example.com",
        "password": "TestPassword123",
        "first_name": "Key",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Key Org", "slug": "key-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Try to create project with invalid key (lowercase)
    project_data = {
        "organization_id": org_id,
        "name": "Invalid Key Project",
        "key": "invalid",
    }
    response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_duplicate_key(client: AsyncClient):
    """Test that duplicate project key in organization is rejected."""
    # Register user and create organization
    user_data = {
        "email": "dupuser@example.com",
        "password": "TestPassword123",
        "first_name": "Dup",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Dup Org", "slug": "dup-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create first project
    project_data = {
        "organization_id": org_id,
        "name": "Project 1",
        "key": "DUP",
    }
    await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    # Try to create second project with same key
    response = await client.post(
        "/api/v1/projects",
        json={
            "organization_id": org_id,
            "name": "Project 2",
            "key": "DUP",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409

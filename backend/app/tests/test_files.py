import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_file_requires_authentication(client: AsyncClient):
    """Test that uploading files requires authentication."""
    response = await client.post(
        "/api/v1/files/upload",
        data={"organization_id": "org_123"},
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_files_requires_authentication(client: AsyncClient):
    """Test that listing files requires authentication."""
    response = await client.get("/api/v1/files?organization_id=org_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_file_success(client: AsyncClient):
    """Test successful file upload."""
    user_data = {
        "email": "fileowner@example.com",
        "password": "TestPassword123",
        "first_name": "File",
        "last_name": "Owner",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "File Test Org",
        "slug": "file-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    response = await client.post(
        "/api/v1/files/upload",
        data={"organization_id": org_id},
        files={"file": ("test.pdf", b"hello world", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size"] == 11
    assert "id" in data


@pytest.mark.asyncio
async def test_list_files_success(client: AsyncClient):
    """Test listing files."""
    user_data = {
        "email": "filelist@example.com",
        "password": "TestPassword123",
        "first_name": "File",
        "last_name": "List",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "File List Org",
        "slug": "file-list-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Upload a file
    await client.post(
        "/api/v1/files/upload",
        data={"organization_id": org_id},
        files={"file": ("test.pdf", b"hello world", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        "/api/v1/files",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_delete_file_success(client: AsyncClient):
    """Test deleting a file."""
    user_data = {
        "email": "filedelete@example.com",
        "password": "TestPassword123",
        "first_name": "File",
        "last_name": "Delete",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "File Delete Org",
        "slug": "file-delete-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Upload a file
    upload_response = await client.post(
        "/api/v1/files/upload",
        data={"organization_id": org_id},
        files={"file": ("test.pdf", b"hello world", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )
    file_id = upload_response.json()["id"]

    response = await client.delete(
        f"/api/v1/files/{file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # File should not appear in list
    list_response = await client.get(
        "/api/v1/files",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_file_tenant_isolation(client: AsyncClient):
    """Test that files are tenant isolated."""
    user1_data = {
        "email": "filetenant1@example.com",
        "password": "TestPassword123",
        "first_name": "File",
        "last_name": "Tenant1",
    }
    user1_response = await client.post("/api/v1/auth/register", json=user1_data)
    token1 = user1_response.json()["access_token"]

    org1_data = {
        "name": "File Tenant1 Org",
        "slug": "file-tenant1-org",
    }
    org1_response = await client.post(
        "/api/v1/organizations",
        json=org1_data,
        headers={"Authorization": f"Bearer {token1}"}
    )
    org1_id = org1_response.json()["id"]

    user2_data = {
        "email": "filetenant2@example.com",
        "password": "TestPassword123",
        "first_name": "File",
        "last_name": "Tenant2",
    }
    user2_response = await client.post("/api/v1/auth/register", json=user2_data)
    token2 = user2_response.json()["access_token"]

    org2_data = {
        "name": "File Tenant2 Org",
        "slug": "file-tenant2-org",
    }
    org2_response = await client.post(
        "/api/v1/organizations",
        json=org2_data,
        headers={"Authorization": f"Bearer {token2}"}
    )
    org2_id = org2_response.json()["id"]

    # Upload file to org1
    upload_response = await client.post(
        "/api/v1/files/upload",
        data={"organization_id": org1_id},
        files={"file": ("test.pdf", b"hello world", "application/pdf")},
        headers={"Authorization": f"Bearer {token1}"}
    )
    file_id = upload_response.json()["id"]

    # User2 should not see org1's files
    list_response = await client.get(
        "/api/v1/files",
        params={"organization_id": org1_id},
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert list_response.status_code == 403

    # User2 should not be able to delete org1's file
    delete_response = await client.delete(
        f"/api/v1/files/{file_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert delete_response.status_code == 403

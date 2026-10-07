import pytest
import json
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_notifications_requires_authentication(client: AsyncClient):
    """Test that listing notifications requires authentication."""
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_notifications_empty(client: AsyncClient):
    """Test that listing notifications returns empty list when no notifications."""
    user_data = {
        "email": "notifempty@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Empty",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "unread_count" in data
    assert data["total"] == 0
    assert data["unread_count"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_create_and_list_notifications(client: AsyncClient):
    """Test creating and listing notifications."""
    owner_data = {
        "email": "notifowner@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_data = {
        "name": "Notification Test Org",
        "slug": "notification-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    # Create notification
    create_response = await client.post(
        "/api/v1/notifications",
        json={
            "user_id": owner_id,
            "organization_id": org_id,
            "type": "test",
            "title": "Test Notification",
            "message": "This is a test notification",
        },
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert create_response.status_code == 201

    # List notifications
    response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["unread_count"] == 1
    assert data["items"][0]["title"] == "Test Notification"
    assert data["items"][0]["message"] == "This is a test notification"
    assert data["items"][0]["type"] == "test"


@pytest.mark.asyncio
async def test_mark_notification_as_read(client: AsyncClient):
    """Test marking a notification as read."""
    owner_data = {
        "email": "notifread@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Read",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_data = {
        "name": "Notification Read Org",
        "slug": "notification-read-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    # Create notification
    create_response = await client.post(
        "/api/v1/notifications",
        json={
            "user_id": owner_id,
            "organization_id": org_id,
            "type": "test",
            "title": "Read Test",
            "message": "Test read",
        },
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    notification_id = create_response.json()["id"]

    # Mark as read
    read_response = await client.post(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert read_response.status_code == 200
    assert read_response.json()["read_at"] is not None

    # Unread count should be 0
    list_response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert list_response.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_notifications_as_read(client: AsyncClient):
    """Test marking all notifications as read."""
    owner_data = {
        "email": "notifreadall@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "ReadAll",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_data = {
        "name": "Notification ReadAll Org",
        "slug": "notification-readall-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    # Create multiple notifications
    for i in range(3):
        await client.post(
            "/api/v1/notifications",
            json={
                "user_id": owner_id,
                "organization_id": org_id,
                "type": "test",
                "title": f"Notification {i}",
                "message": f"Test message {i}",
            },
            headers={"Authorization": f"Bearer {owner_token}"}
        )

    # Mark all as read
    mark_all_response = await client.post(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert mark_all_response.status_code == 204

    # Unread count should be 0
    list_response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert list_response.json()["unread_count"] == 0


@pytest.mark.asyncio
async def test_notification_ownership(client: AsyncClient):
    """Test that users can only access their own notifications."""
    owner_data = {
        "email": "notifowner2@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Owner2",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_data = {
        "name": "Notification Ownership Org",
        "slug": "notification-ownership-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    other_data = {
        "email": "notifother@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Other",
    }
    other_response = await client.post("/api/v1/auth/register", json=other_data)
    other_token = other_response.json()["access_token"]
    other_id = other_response.json()["user"]["id"]

    await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": other_response.json()["user"]["email"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )

    # Create notification for owner
    create_response = await client.post(
        "/api/v1/notifications",
        json={
            "user_id": owner_id,
            "organization_id": org_id,
            "type": "test",
            "title": "Owner Notification",
            "message": "For owner only",
        },
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    notification_id = create_response.json()["id"]

    # Other user should not be able to access owner's notification
    other_get_response = await client.get(
        f"/api/v1/notifications/{notification_id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert other_get_response.status_code == 403

    # Other user should not see owner's notifications in list
    other_list_response = await client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    assert other_list_response.status_code == 200
    assert other_list_response.json()["total"] == 0


@pytest.mark.asyncio
async def test_notification_pagination(client: AsyncClient):
    """Test notification pagination."""
    owner_data = {
        "email": "notifpagination@example.com",
        "password": "TestPassword123",
        "first_name": "Notif",
        "last_name": "Pagination",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_data = {
        "name": "Notification Pagination Org",
        "slug": "notification-pagination-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    # Create 5 notifications
    for i in range(5):
        await client.post(
            "/api/v1/notifications",
            json={
                "user_id": owner_id,
                "organization_id": org_id,
                "type": "test",
                "title": f"Notification {i}",
                "message": f"Message {i}",
            },
            headers={"Authorization": f"Bearer {owner_token}"}
        )

    # Get first page with limit 2
    response = await client.get(
        "/api/v1/notifications",
        params={"limit": 2, "offset": 0},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    # Get second page
    response2 = await client.get(
        "/api/v1/notifications",
        params={"limit": 2, "offset": 2},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert response2.status_code == 200
    assert len(response2.json()["items"]) == 2

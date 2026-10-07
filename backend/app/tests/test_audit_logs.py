import pytest
import json
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_audit_logs_requires_authentication(client: AsyncClient):
    """Test that listing audit logs requires authentication."""
    response = await client.get("/api/v1/audit-logs", params={"organization_id": "org_123"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_audit_logs_requires_membership(client: AsyncClient):
    """Test that listing audit logs requires organization membership."""
    owner_data = {
        "email": "auditowner_nonmember@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]

    org_data = {
        "name": "Audit Test Org NonMember",
        "slug": "audit-test-org-nonmember",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    non_member_data = {
        "email": "auditnonmember@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "NonMember",
    }
    non_member_response = await client.post("/api/v1/auth/register", json=non_member_data)
    non_member_token = non_member_response.json()["access_token"]

    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_audit_logs_requires_permission(client: AsyncClient):
    """Test that listing audit logs requires owner or admin role."""
    user_data = {
        "email": "auditviewer@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "Viewer",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "Audit Test Org",
        "slug": "audit-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Add another user as VIEWER
    viewer_data = {
        "email": "viewer@example.com",
        "password": "TestPassword123",
        "first_name": "Viewer",
        "last_name": "User",
    }
    viewer_response = await client.post("/api/v1/auth/register", json=viewer_data)
    viewer_token = viewer_response.json()["access_token"]

    await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": viewer_response.json()["user"]["email"], "role": "VIEWER"},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_audit_logs_as_owner(client: AsyncClient):
    """Test that owner can list audit logs."""
    user_data = {
        "email": "auditowner@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "Owner",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "Audit Test Org",
        "slug": "audit-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert data["items"][0]["action"] == "organization.created"


@pytest.mark.asyncio
async def test_list_audit_logs_as_admin(client: AsyncClient):
    """Test that admin can list audit logs."""
    owner_data = {
        "email": "auditowner3@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "Owner3",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]

    org_data = {
        "name": "Audit Test Org 3",
        "slug": "audit-test-org-3",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    admin_data = {
        "email": "auditadmin2@example.com",
        "password": "TestPassword123",
        "first_name": "Audit",
        "last_name": "Admin",
    }
    admin_response = await client.post("/api/v1/auth/register", json=admin_data)
    admin_token = admin_response.json()["access_token"]

    invite_response = await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": admin_response.json()["user"]["email"], "role": "ADMIN"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    assert invite_response.status_code == 201

    await client.post(
        f"/api/v1/organizations/{org_id}/members/accept",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    actions = {item["action"] for item in data["items"]}
    assert "organization.created" in actions
    assert "organization.member_invited" in actions
    assert "organization.member_accepted" in actions


@pytest.mark.asyncio
async def test_mutation_creates_audit_log(client: AsyncClient):
    """Test that creating a project creates an audit log entry."""
    owner_data = {
        "email": "mutationowner@example.com",
        "password": "TestPassword123",
        "first_name": "Mutation",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "Mutation Test Org",
        "slug": "mutation-test-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Before mutation: org creation created an audit log
    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    # Create project (mutation)
    project_data = {
        "name": "Mutation Project",
        "key": "MUT",
        "description": "A test project",
        "organization_id": org_id,
    }
    project_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    # After mutation: audit log exists
    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    actions = {item["action"] for item in data["items"]}
    assert "organization.created" in actions
    assert "project.created" in actions


@pytest.mark.asyncio
async def test_multiple_mutations_create_audit_logs(client: AsyncClient):
    """Test that multiple mutations create multiple audit log entries."""
    owner_data = {
        "email": "multiaudit@example.com",
        "password": "TestPassword123",
        "first_name": "Multi",
        "last_name": "Audit",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    token = owner_response.json()["access_token"]

    org_data = {
        "name": "Multi Audit Org",
        "slug": "multi-audit-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "name": "Multi Project",
        "key": "MULTI",
        "organization_id": org_id,
    }
    project_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    # Create team
    team_data = {
        "name": "Multi Team",
        "description": "A team",
        "organization_id": org_id,
    }
    team_response = await client.post(
        "/api/v1/teams",
        json=team_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    team_id = team_response.json()["id"]

    # Create task
    task_data = {
        "project_id": project_id,
        "title": "Multi Task",
        "description": "A task",
    }
    task_response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = task_response.json()["id"]

    # List audit logs
    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4

    actions = {item["action"] for item in data["items"]}
    resource_ids = {item["resource_id"] for item in data["items"]}

    assert "organization.created" in actions
    assert "project.created" in actions
    assert "team.created" in actions
    assert "task.created" in actions


@pytest.mark.asyncio
async def test_audit_log_excludes_sensitive_data(client: AsyncClient):
    """Test that audit logs do not capture sensitive data like totp_secret."""
    user_data = {
        "email": "secretaudit@example.com",
        "password": "TestPassword123",
        "first_name": "Secret",
        "last_name": "Audit",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_data = {
        "name": "Secret Audit Org",
        "slug": "secret-audit-org",
    }
    org_response = await client.post(
        "/api/v1/organizations",
        json=org_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    # Create project
    project_data = {
        "name": "Secret Project",
        "key": "SECRET",
        "organization_id": org_id,
    }
    project_response = await client.post(
        "/api/v1/projects",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    # List audit logs
    response = await client.get(
        "/api/v1/audit-logs",
        params={"organization_id": org_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2

    audit_log = data["items"][0]
    assert "totp_secret" not in json.dumps(audit_log)
    assert "password" not in json.dumps(audit_log)
    assert "password_hash" not in json.dumps(audit_log)
    assert "secret" not in json.dumps(audit_log)
    assert audit_log["changes"] is None

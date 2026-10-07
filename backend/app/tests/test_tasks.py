import pytest
from httpx import AsyncClient
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import TaskStatus, TaskPriority


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test task creation."""
    user_data = {
        "email": "owner@example.com",
        "password": "TestPassword123",
        "first_name": "Task",
        "last_name": "Owner",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Test Org", "slug": "test-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Test Project", "key": "TEST"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    task_data = {
        "project_id": project_id,
        "title": "Test Task",
        "description": "A test task",
        "status": "TODO",
        "priority": "HIGH",
    }
    response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "A test task"
    assert data["project_id"] == project_id
    assert data["status"] == "TODO"
    assert data["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_create_task_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot create tasks."""
    response = await client.post("/api/v1/tasks", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Test listing tasks in a project."""
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

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "List Project", "key": "LIST"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task 1"},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        f"/api/v1/tasks?project_id={project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Task 1"


@pytest.mark.asyncio
async def test_list_tasks_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot list tasks."""
    response = await client.get("/api/v1/tasks?project_id=proj_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    """Test getting a task by ID."""
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

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Get Project", "key": "GET"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    create_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Get Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Task"


@pytest.mark.asyncio
async def test_get_task_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot get tasks."""
    response = await client.get("/api/v1/tasks/tsk_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    """Test updating a task."""
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

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Update Project", "key": "UPD"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    create_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Original Title", "status": "TODO"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Title",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
    }
    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "IN_PROGRESS"
    assert data["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_update_task_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot update tasks."""
    response = await client.patch("/api/v1/tasks/tsk_123", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    """Test deleting a task."""
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

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Delete Project", "key": "DEL"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    create_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "To Delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    get_response = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot delete tasks."""
    response = await client.delete("/api/v1/tasks/tsk_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tenant_isolation_task(client: AsyncClient):
    """Test that users cannot access tasks from other organizations."""
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

    project_a = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_a_id, "name": "Project A", "key": "PRJA"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    project_a_id = project_a.json()["id"]

    task_a = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_a_id, "title": "Task A"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    task_a_id = task_a.json()["id"]

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

    project_b = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_b_id, "name": "Project B", "key": "PRJB"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    project_b_id = project_b.json()["id"]

    response = await client.get(
        f"/api/v1/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.patch(
        f"/api/v1/tasks/{task_a_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.delete(
        f"/api/v1/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/tasks?project_id={project_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/tasks/{task_a_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 200

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_b_id, "title": "Task B"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_task_cross_org_blocked(client: AsyncClient):
    """Test that a user cannot create a task in another organization's project."""
    user_a_data = {
        "email": "crossusera@example.com",
        "password": "TestPassword123",
        "first_name": "Cross",
        "last_name": "UserA",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]

    org_a = await client.post(
        "/api/v1/organizations",
        json={"name": "Org A", "slug": "org-a"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    project_a = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_a_id, "name": "Project A", "key": "PRJA"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    project_a_id = project_a.json()["id"]

    user_b_data = {
        "email": "crossuserb@example.com",
        "password": "TestPassword123",
        "first_name": "Cross",
        "last_name": "UserB",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_a_id, "title": "Cross Task"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_task_invalid_project(client: AsyncClient):
    """Test that creating a task with invalid project fails."""
    user_data = {
        "email": "invalidproj@example.com",
        "password": "TestPassword123",
        "first_name": "Invalid",
        "last_name": "Project",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": "invalid_project_id", "title": "Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_immutable_fields(client: AsyncClient):
    """Test that project_id cannot be changed."""
    user_data = {
        "email": "immutable@example.com",
        "password": "TestPassword123",
        "first_name": "Immutable",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Immutable Org", "slug": "immutable-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Project", "key": "IMM"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    create_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"project_id": "different_project", "id": "different_id"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_non_member_cannot_access_task(client: AsyncClient):
    """Test that non-members cannot access tasks."""
    owner_data = {
        "email": "owner@example.com",
        "password": "TestPassword123",
        "first_name": "Owner",
        "last_name": "User",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Owner Org", "slug": "owner-org"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Project", "key": "OWN"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_response.json()["id"]

    task_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    task_id = task_response.json()["id"]

    non_member_data = {
        "email": "nonmember@example.com",
        "password": "TestPassword123",
        "first_name": "Non",
        "last_name": "Member",
    }
    non_member_response = await client.post("/api/v1/auth/register", json=non_member_data)
    non_member_token = non_member_response.json()["access_token"]

    response = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/tasks?project_id={project_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_rbac_task_permissions(client: AsyncClient):
    """Test RBAC permissions for tasks."""
    owner_data = {
        "email": "rbacowner@example.com",
        "password": "TestPassword123",
        "first_name": "RBAC",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "RBAC Org", "slug": "rbac-org"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "RBAC Project", "key": "RBAC"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    project_id = project_response.json()["id"]

    task_response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    task_id = task_response.json()["id"]

    roles_to_test = [
        ("ADMIN", True, True, True, True),
        ("MANAGER", True, True, True, False),
        ("MEMBER", True, False, True, False),
        ("VIEWER", True, False, False, False),
    ]

    for role, can_view, can_create, can_update, can_delete in roles_to_test:
        user_data = {
            "email": f"rbac{role.lower()}@example.com",
            "password": "TestPassword123",
            "first_name": role,
            "last_name": "User",
        }
        user_response = await client.post("/api/v1/auth/register", json=user_data)
        user_token = user_response.json()["access_token"]

        await client.post(
            f"/api/v1/organizations/{org_id}/members",
            json={"email": user_data["email"], "role": role},
            headers={"Authorization": f"Bearer {owner_token}"}
        )

        await client.post(
            f"/api/v1/organizations/{org_id}/members/accept",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        if can_view:
            response = await client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200, f"{role} should be able to view task"
        else:
            response = await client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to view task"

        if can_create:
            response = await client.post(
                "/api/v1/tasks",
                json={"project_id": project_id, "title": f"Task {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 201, f"{role} should be able to create task"
        else:
            response = await client.post(
                "/api/v1/tasks",
                json={"project_id": project_id, "title": f"Task {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to create task"

        if can_update:
            response = await client.patch(
                f"/api/v1/tasks/{task_id}",
                json={"title": f"Updated {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200, f"{role} should be able to update task"
        else:
            response = await client.patch(
                f"/api/v1/tasks/{task_id}",
                json={"title": f"Updated {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to update task"

        if can_delete:
            new_task = await client.post(
                "/api/v1/tasks",
                json={"project_id": project_id, "title": f"Delete {role}"},
                headers={"Authorization": f"Bearer {owner_token}"}
            )
            new_task_id = new_task.json()["id"]
            response = await client.delete(
                f"/api/v1/tasks/{new_task_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 204, f"{role} should be able to delete task"
        else:
            response = await client.delete(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to delete task"


@pytest.mark.asyncio
async def test_create_task_invalid_status(client: AsyncClient):
    """Test that invalid task status is rejected."""
    user_data = {
        "email": "status@example.com",
        "password": "TestPassword123",
        "first_name": "Status",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Status Org", "slug": "status-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Project", "key": "STS"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task", "status": "INVALID"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_invalid_priority(client: AsyncClient):
    """Test that invalid task priority is rejected."""
    user_data = {
        "email": "priority@example.com",
        "password": "TestPassword123",
        "first_name": "Priority",
        "last_name": "User",
    }
    user_response = await client.post("/api/v1/auth/register", json=user_data)
    token = user_response.json()["access_token"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "Priority Org", "slug": "priority-org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]

    project_response = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_id, "name": "Project", "key": "PRI"},
        headers={"Authorization": f"Bearer {token}"}
    )
    project_id = project_response.json()["id"]

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_id, "title": "Task", "priority": "INVALID"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_assignee_cross_tenant_blocked(client: AsyncClient):
    """Test that a user from another organization cannot be assigned to a task."""
    user_a_data = {
        "email": "assignera@example.com",
        "password": "TestPassword123",
        "first_name": "Assigner",
        "last_name": "A",
    }
    response_a = await client.post("/api/v1/auth/register", json=user_a_data)
    token_a = response_a.json()["access_token"]

    org_a = await client.post(
        "/api/v1/organizations",
        json={"name": "Org A", "slug": "org-a"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    org_a_id = org_a.json()["id"]

    project_a = await client.post(
        "/api/v1/projects",
        json={"organization_id": org_a_id, "name": "Project A", "key": "PRJA"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    project_a_id = project_a.json()["id"]

    user_b_data = {
        "email": "assignerb@example.com",
        "password": "TestPassword123",
        "first_name": "Assigner",
        "last_name": "B",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]
    user_b_id = response_b.json()["user"]["id"]

    org_b = await client.post(
        "/api/v1/organizations",
        json={"name": "Org B", "slug": "org-b"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    org_b_id = org_b.json()["id"]

    await client.post(
        f"/api/v1/organizations/{org_b_id}/members",
        json={"email": user_b_data["email"], "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token_b}"}
    )

    await client.post(
        f"/api/v1/organizations/{org_b_id}/members/accept",
        headers={"Authorization": f"Bearer {token_b}"}
    )

    response = await client.post(
        "/api/v1/tasks",
        json={"project_id": project_a_id, "title": "Task", "assignee_id": user_b_id},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 422

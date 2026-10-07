import pytest
from httpx import AsyncClient
from app.schemas.team import TeamCreate, TeamUpdate


@pytest.mark.asyncio
async def test_create_team(client: AsyncClient):
    """Test team creation."""
    user_data = {
        "email": "owner@example.com",
        "password": "TestPassword123",
        "first_name": "Team",
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

    team_data = {
        "organization_id": org_id,
        "name": "Engineering",
        "description": "Engineering team",
    }
    response = await client.post(
        "/api/v1/teams",
        json=team_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Engineering"
    assert data["description"] == "Engineering team"
    assert data["organization_id"] == org_id


@pytest.mark.asyncio
async def test_create_team_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot create teams."""
    response = await client.post("/api/v1/teams", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient):
    """Test listing teams in an organization."""
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

    await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Engineering"},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.get(
        f"/api/v1/teams?organization_id={org_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Engineering"


@pytest.mark.asyncio
async def test_list_teams_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot list teams."""
    response = await client.get("/api/v1/teams?organization_id=org_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_team(client: AsyncClient):
    """Test getting a team by ID."""
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

    create_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Engineering"},
        headers={"Authorization": f"Bearer {token}"}
    )
    team_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == team_id
    assert data["name"] == "Engineering"


@pytest.mark.asyncio
async def test_get_team_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot get teams."""
    response = await client.get("/api/v1/teams/team_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_team(client: AsyncClient):
    """Test updating a team."""
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

    create_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Original"},
        headers={"Authorization": f"Bearer {token}"}
    )
    team_id = create_response.json()["id"]

    update_data = {
        "name": "Updated Team",
        "description": "Updated description",
    }
    response = await client.patch(
        f"/api/v1/teams/{team_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Team"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_team_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot update teams."""
    response = await client.patch("/api/v1/teams/team_123", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_team(client: AsyncClient):
    """Test deleting a team."""
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

    create_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "To Delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    team_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    get_response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_team_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot delete teams."""
    response = await client.delete("/api/v1/teams/team_123")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tenant_isolation_team(client: AsyncClient):
    """Test that users cannot access teams from other organizations."""
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

    team_a = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_a_id, "name": "Team A"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    team_a_id = team_a.json()["id"]

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

    response = await client.get(
        f"/api/v1/teams/{team_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.patch(
        f"/api/v1/teams/{team_a_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.delete(
        f"/api/v1/teams/{team_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/teams?organization_id={org_a_id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/teams/{team_a_id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert response.status_code == 200

    response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_b_id, "name": "Team B"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_team_duplicate_name(client: AsyncClient):
    """Test that duplicate team name in organization is rejected."""
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

    await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Engineering"},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Engineering"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_team_cross_org_blocked(client: AsyncClient):
    """Test that a user cannot create a team in another organization."""
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

    user_b_data = {
        "email": "crossuserb@example.com",
        "password": "TestPassword123",
        "first_name": "Cross",
        "last_name": "UserB",
    }
    response_b = await client.post("/api/v1/auth/register", json=user_b_data)
    token_b = response_b.json()["access_token"]

    response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_a_id, "name": "Cross Team"},
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_team_immutable_fields(client: AsyncClient):
    """Test that organization_id and id cannot be changed."""
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

    create_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Team"},
        headers={"Authorization": f"Bearer {token}"}
    )
    team_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/teams/{team_id}",
        json={"organization_id": "different-org", "id": "different-id"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_non_member_cannot_access_team(client: AsyncClient):
    """Test that non-members cannot access teams."""
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

    team_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Team"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    team_id = team_response.json()["id"]

    non_member_data = {
        "email": "nonmember@example.com",
        "password": "TestPassword123",
        "first_name": "Non",
        "last_name": "Member",
    }
    non_member_response = await client.post("/api/v1/auth/register", json=non_member_data)
    non_member_token = non_member_response.json()["access_token"]

    response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.patch(
        f"/api/v1/teams/{team_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.delete(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403

    response = await client.get(
        f"/api/v1/teams?organization_id={org_id}",
        headers={"Authorization": f"Bearer {non_member_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_rbac_team_permissions(client: AsyncClient):
    """Test RBAC permissions for teams."""
    owner_data = {
        "email": "rbacowner@example.com",
        "password": "TestPassword123",
        "first_name": "RBAC",
        "last_name": "Owner",
    }
    owner_response = await client.post("/api/v1/auth/register", json=owner_data)
    owner_token = owner_response.json()["access_token"]
    owner_id = owner_response.json()["user"]["id"]

    org_response = await client.post(
        "/api/v1/organizations",
        json={"name": "RBAC Org", "slug": "rbac-org"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    org_id = org_response.json()["id"]

    team_response = await client.post(
        "/api/v1/teams",
        json={"organization_id": org_id, "name": "Team"},
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    team_id = team_response.json()["id"]

    roles_to_test = [
        ("ADMIN", True, True, True, True),
        ("MANAGER", True, True, True, False),
        ("MEMBER", True, False, False, False),
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
        user_id = user_response.json()["user"]["id"]

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
                f"/api/v1/teams/{team_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200, f"{role} should be able to view team"
        else:
            response = await client.get(
                f"/api/v1/teams/{team_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to view team"

        if can_create:
            response = await client.post(
                "/api/v1/teams",
                json={"organization_id": org_id, "name": f"Team {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 201, f"{role} should be able to create team"
        else:
            response = await client.post(
                "/api/v1/teams",
                json={"organization_id": org_id, "name": f"Team {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to create team"

        if can_update:
            response = await client.patch(
                f"/api/v1/teams/{team_id}",
                json={"name": f"Updated {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 200, f"{role} should be able to update team"
        else:
            response = await client.patch(
                f"/api/v1/teams/{team_id}",
                json={"name": f"Updated {role}"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to update team"

        if can_delete:
            new_team = await client.post(
                "/api/v1/teams",
                json={"organization_id": org_id, "name": f"Delete {role}"},
                headers={"Authorization": f"Bearer {owner_token}"}
            )
            new_team_id = new_team.json()["id"]
            response = await client.delete(
                f"/api/v1/teams/{new_team_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 204, f"{role} should be able to delete team"
        else:
            response = await client.delete(
                f"/api/v1/teams/{team_id}",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert response.status_code == 403, f"{role} should not be able to delete team"

from typing import List, Optional
from app.models.membership import Role


class Permission:
    """Permission definitions for different resources."""

    # Organization permissions
    ORG_VIEW = "org:view"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"
    ORG_MANAGE_MEMBERS = "org:manage_members"
    ORG_INVITE_MEMBERS = "org:invite_members"
    ORG_VIEW_ANALYTICS = "org:view_analytics"

    # Team permissions
    TEAM_VIEW = "team:view"
    TEAM_CREATE = "team:create"
    TEAM_UPDATE = "team:update"
    TEAM_DELETE = "team:delete"
    TEAM_MANAGE_MEMBERS = "team:manage_members"

    # Project permissions
    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE_MEMBERS = "project:manage_members"

    # Task permissions
    TASK_VIEW = "task:view"
    TASK_CREATE = "task:create"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_ASSIGN = "task:assign"
    TASK_COMMENT = "task:comment"

    # User permissions
    USER_VIEW = "user:view"
    USER_UPDATE_SELF = "user:update_self"

    # API Key permissions
    API_KEY_CREATE = "api_key:create"
    API_KEY_VIEW = "api_key:view"
    API_KEY_DELETE = "api_key:delete"
    API_KEY_REVOKE = "api_key:revoke"

    # Audit log permissions
    AUDIT_LOG_VIEW = "audit_log:view"


# Role to permission mapping
ROLE_PERMISSIONS = {
    Role.OWNER: [
        # Organization
        Permission.ORG_VIEW,
        Permission.ORG_UPDATE,
        Permission.ORG_DELETE,
        Permission.ORG_MANAGE_MEMBERS,
        Permission.ORG_INVITE_MEMBERS,
        Permission.ORG_VIEW_ANALYTICS,
        # Team
        Permission.TEAM_VIEW,
        Permission.TEAM_CREATE,
        Permission.TEAM_UPDATE,
        Permission.TEAM_DELETE,
        Permission.TEAM_MANAGE_MEMBERS,
        # Project
        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_MANAGE_MEMBERS,
        # Task
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        Permission.TASK_ASSIGN,
        Permission.TASK_COMMENT,
        # User
        Permission.USER_VIEW,
        Permission.USER_UPDATE_SELF,
        # API Key
        Permission.API_KEY_CREATE,
        Permission.API_KEY_VIEW,
        Permission.API_KEY_DELETE,
        Permission.API_KEY_REVOKE,
        # Audit log
        Permission.AUDIT_LOG_VIEW,
    ],
    Role.ADMIN: [
        # Organization
        Permission.ORG_VIEW,
        Permission.ORG_UPDATE,
        Permission.ORG_MANAGE_MEMBERS,
        Permission.ORG_INVITE_MEMBERS,
        Permission.ORG_VIEW_ANALYTICS,
        # Team
        Permission.TEAM_VIEW,
        Permission.TEAM_CREATE,
        Permission.TEAM_UPDATE,
        Permission.TEAM_DELETE,
        Permission.TEAM_MANAGE_MEMBERS,
        # Project
        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_DELETE,
        Permission.PROJECT_MANAGE_MEMBERS,
        # Task
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        Permission.TASK_ASSIGN,
        Permission.TASK_COMMENT,
        # User
        Permission.USER_VIEW,
        Permission.USER_UPDATE_SELF,
        # API Key
        Permission.API_KEY_CREATE,
        Permission.API_KEY_VIEW,
        Permission.API_KEY_DELETE,
        Permission.API_KEY_REVOKE,
        # Audit log
        Permission.AUDIT_LOG_VIEW,
    ],
    Role.MANAGER: [
        # Organization
        Permission.ORG_VIEW,
        Permission.ORG_VIEW_ANALYTICS,
        # Team
        Permission.TEAM_VIEW,
        Permission.TEAM_CREATE,
        Permission.TEAM_UPDATE,
        Permission.TEAM_MANAGE_MEMBERS,
        # Project
        Permission.PROJECT_VIEW,
        Permission.PROJECT_CREATE,
        Permission.PROJECT_UPDATE,
        Permission.PROJECT_MANAGE_MEMBERS,
        # Task
        Permission.TASK_VIEW,
        Permission.TASK_CREATE,
        Permission.TASK_UPDATE,
        Permission.TASK_ASSIGN,
        Permission.TASK_COMMENT,
        # User
        Permission.USER_VIEW,
        Permission.USER_UPDATE_SELF,
    ],
    Role.MEMBER: [
        # Organization
        Permission.ORG_VIEW,
        # Team
        Permission.TEAM_VIEW,
        # Project
        Permission.PROJECT_VIEW,
        # Task
        Permission.TASK_VIEW,
        Permission.TASK_UPDATE,
        Permission.TASK_COMMENT,
        # User
        Permission.USER_UPDATE_SELF,
    ],
    Role.VIEWER: [
        # Organization
        Permission.ORG_VIEW,
        # Team
        Permission.TEAM_VIEW,
        # Project
        Permission.PROJECT_VIEW,
        # Task
        Permission.TASK_VIEW,
    ],
}


class PermissionService:
    """Service for checking user permissions."""

    # Organization permissions
    ORG_VIEW = Permission.ORG_VIEW
    ORG_UPDATE = Permission.ORG_UPDATE
    ORG_DELETE = Permission.ORG_DELETE
    ORG_MANAGE_MEMBERS = Permission.ORG_MANAGE_MEMBERS
    ORG_INVITE_MEMBERS = Permission.ORG_INVITE_MEMBERS
    ORG_VIEW_ANALYTICS = Permission.ORG_VIEW_ANALYTICS

    # Team permissions
    TEAM_VIEW = Permission.TEAM_VIEW
    TEAM_CREATE = Permission.TEAM_CREATE
    TEAM_UPDATE = Permission.TEAM_UPDATE
    TEAM_DELETE = Permission.TEAM_DELETE
    TEAM_MANAGE_MEMBERS = Permission.TEAM_MANAGE_MEMBERS

    # Project permissions
    PROJECT_VIEW = Permission.PROJECT_VIEW
    PROJECT_CREATE = Permission.PROJECT_CREATE
    PROJECT_UPDATE = Permission.PROJECT_UPDATE
    PROJECT_DELETE = Permission.PROJECT_DELETE
    PROJECT_MANAGE_MEMBERS = Permission.PROJECT_MANAGE_MEMBERS

    # Task permissions
    TASK_VIEW = Permission.TASK_VIEW
    TASK_CREATE = Permission.TASK_CREATE
    TASK_UPDATE = Permission.TASK_UPDATE
    TASK_DELETE = Permission.TASK_DELETE
    TASK_ASSIGN = Permission.TASK_ASSIGN
    TASK_COMMENT = Permission.TASK_COMMENT

    # User permissions
    USER_VIEW = Permission.USER_VIEW
    USER_UPDATE_SELF = Permission.USER_UPDATE_SELF

    # API Key permissions
    API_KEY_CREATE = Permission.API_KEY_CREATE
    API_KEY_VIEW = Permission.API_KEY_VIEW
    API_KEY_DELETE = Permission.API_KEY_DELETE
    API_KEY_REVOKE = Permission.API_KEY_REVOKE

    # Audit log permissions
    AUDIT_LOG_VIEW = Permission.AUDIT_LOG_VIEW

    @staticmethod
    def has_permission(role: Role, permission: str) -> bool:
        """Check if a role has a specific permission."""
        return permission in ROLE_PERMISSIONS.get(role, [])

    @staticmethod
    def has_any_permission(role: Role, permissions: List[str]) -> bool:
        """Check if a role has any of the specified permissions."""
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        return any(perm in role_permissions for perm in permissions)

    @staticmethod
    def has_all_permissions(role: Role, permissions: List[str]) -> bool:
        """Check if a role has all of the specified permissions."""
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        return all(perm in role_permissions for perm in permissions)

    @staticmethod
    def get_permissions(role: Role) -> List[str]:
        """Get all permissions for a role."""
        return ROLE_PERMISSIONS.get(role, []).copy()

    @staticmethod
    def can_manage_organization(role: Role) -> bool:
        """Check if role can manage organization settings."""
        return role in [Role.OWNER, Role.ADMIN]

    @staticmethod
    def can_invite_members(role: Role) -> bool:
        """Check if role can invite members."""
        return role in [Role.OWNER, Role.ADMIN]

    @staticmethod
    def can_delete_organization(role: Role) -> bool:
        """Check if role can delete organization."""
        return role == Role.OWNER

    @staticmethod
    def can_manage_projects(role: Role) -> bool:
        """Check if role can manage projects."""
        return role in [Role.OWNER, Role.ADMIN, Role.MANAGER]

    @staticmethod
    def can_manage_team(role: Role) -> bool:
        """Check if role can manage teams."""
        return role in [Role.OWNER, Role.ADMIN, Role.MANAGER]

    @staticmethod
    def can_view_analytics(role: Role) -> bool:
        """Check if role can view analytics."""
        return role in [Role.OWNER, Role.ADMIN, Role.MANAGER]

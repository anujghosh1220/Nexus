# NEXUS

**One workspace. Every operation.**

A production-grade, multi-tenant SaaS platform for teams, projects, workflows, and APIs. Built with FastAPI, SQLAlchemy, Next.js, and TypeScript.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Frontend Routes](#-frontend-routes)
- [Security](#-security)
- [Testing](#-testing)
- [Performance](#-performance)
- [Deployment](#-deployment)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Features

### Core Platform
- **Multi-tenant Architecture**: Complete tenant isolation with organization-scoped data access
- **User Management**: Registration, email/password authentication, profile management
- **Two-Factor Authentication (2FA)**: TOTP-based 2FA with recovery codes
- **Password Reset**: Secure password reset flow with time-limited tokens
- **Email Verification**: Email verification with token-based confirmation

### Organizations & Collaboration
- **Organizations**: Create and manage multiple organizations with custom slugs
- **Memberships**: Role-based membership system with invitation workflow
- **Teams**: Organize users into functional teams within organizations
- **Projects**: Track projects with status, description, and organization scoping
- **Tasks**: Full task lifecycle with status, priority, assignee, and project association

### Developer & API Features
- **RESTful API**: Complete JSON API with OpenAPI documentation
- **API Keys**: Scoped API key authentication with expiration and revocation
- **Rate Limiting**: Per-user/IP rate limiting via Redis-backed slowapi
- **Audit Logging**: Comprehensive audit trail for all security-sensitive actions

### Notifications & Files
- **Notifications**: In-app notifications with read/unread tracking
- **File Management**: Secure file upload with object storage abstraction (local/S3)
- **File Validation**: Size limits, MIME type whitelisting, and authorization checks

### Frontend Experience
- **Dashboard**: Real-time metrics for organizations, projects, tasks, and notifications
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Loading/Empty/Error States**: Comprehensive UX states for all data operations
- **Confirmation Dialogs**: Destructive action confirmation for data safety
- **Token Refresh**: Automatic access token refresh on 401 with refresh token rotation

---

## 🏗️ Architecture

### System Design

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   PostgreSQL    │
│   (Next.js)     │     │   (FastAPI)     │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │  (Rate Limiting │
                       │   + Celery)     │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Object Storage  │
                       │  (Local/S3)     │
                       └─────────────────┘
```

### Design Patterns

- **Layered Architecture**: API routes → Services → Repositories → Database
- **Dependency Injection**: FastAPI's `Depends` for service/repository resolution
- **Repository Pattern**: Data access abstracted behind repository interfaces
- **Service Layer**: Business logic isolated from API routing
- **Pydantic Schemas**: Request/response validation and serialization
- **Async/Await**: Full async stack with SQLAlchemy 2.x async sessions

---

## 💻 Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | Core runtime |
| Framework | FastAPI | Latest | REST API server |
| ORM | SQLAlchemy | 2.x | Database ORM |
| Database | PostgreSQL | 16+ | Primary datastore |
| Cache | Redis | Latest | Rate limiting, sessions |
| Task Queue | Celery | Latest | Background jobs |
| Validation | Pydantic | v2 | Schema validation |
| Auth | python-jose | Latest | JWT handling |
| Passwords | passlib/bcrypt | Latest | Password hashing |
| 2FA | pyotp | Latest | TOTP generation |
| Storage | boto3/aiofiles | Latest | Object storage |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 14 | React framework |
| Language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.x | Utility CSS |
| Data Fetching | TanStack Query | 5.x | Server state |
| Forms | React Hook Form | 7.x | Form management |
| Validation | Zod | 3.x | Schema validation |
| HTTP | Axios | 1.x | API client |
| UI | shadcn/ui-style | - | Component system |

---

## 📦 Project Structure

```
F:\Nexus/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI pipeline
├── backend/
│   ├── alembic/
│   │   ├── env.py                 # Alembic async migration config
│   │   ├── script.py.mako         # Migration template
│   │   ├── alembic.ini            # Alembic configuration
│   │   └── versions/
│   │       ├── 001_initial.py                    # Initial schema
│   │       ├── 20261006_2127_59ead14f6e62_add_project_indexes.py
│   │       ├── 20261006_2145_a328177511bb_add_team_indexes_and_constraints.py
│   │       ├── 20261006_2206_1b8269a3c7da_add_tasks_table.py
│   │       ├── 20261006_2212_96d642f8e4a3_add_user_2fa_fields.py
│   │       ├── 20261006_2232_a1b2c3d4e5f6_add_audit_logs_table.py
│   │       ├── 20261006_2301_b2c3d4e5f6a7_add_api_keys_table.py
│   │       ├── 20261006_2310_c3d4e5f6a7b8_add_notifications_table.py
│   │       └── 20261006_2320_d4e5f6a7b8c9_add_files_table.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI application factory
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Settings via pydantic-settings
│   │   │   ├── database.py        # Async engine/session setup
│   │   │   ├── security.py        # JWT, bcrypt, 2FA, token generation
│   │   │   ├── exceptions.py      # Custom exception classes
│   │   │   ├── logging.py         # Logging configuration
│   │   │   └── rate_limit.py      # slowapi + Redis rate limiting
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py            # Shared dependencies (auth, DB)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py        # Registration, login, refresh, logout, password reset
│   │   │       ├── two_factor.py  # 2FA setup, enable, disable, status
│   │   │       ├── organizations.py # Org CRUD, members, invitations
│   │   │       ├── projects.py     # Project CRUD
│   │   │       ├── teams.py        # Team CRUD
│   │   │       ├── tasks.py        # Task CRUD
│   │   │       ├── api_keys.py     # API key CRUD, revoke
│   │   │       ├── notifications.py # Notification CRUD, read/unread
│   │   │       ├── files.py        # File upload, list, download, delete
│   │   │       └── audit_logs.py   # Audit log listing with filters
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py            # User model with 2FA fields
│   │   │   ├── organization.py    # Organization model
│   │   │   ├── membership.py      # Membership/Role model
│   │   │   ├── project.py         # Project model
│   │   │   ├── team.py            # Team model
│   │   │   ├── task.py            # Task model
│   │   │   ├── api_key.py         # API key model (hashed)
│   │   │   ├── notification.py    # Notification model
│   │   │   ├── file.py            # File model with soft delete
│   │   │   ├── audit_log.py       # Audit log model
│   │   │   ├── refresh_token.py   # Refresh token model
│   │   │   ├── password_reset_token.py
│   │   │   └── email_verification.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py            # UserCreate, UserResponse
│   │   │   ├── organization.py    # OrgCreate, OrgResponse, MembershipResponse
│   │   │   ├── project.py         # ProjectCreate, ProjectResponse
│   │   │   ├── team.py            # TeamCreate, TeamResponse
│   │   │   ├── task.py            # TaskCreate, TaskResponse
│   │   │   ├── api_key.py         # ApiKeyCreate, ApiKeyCreateResponse
│   │   │   ├── notification.py    # NotificationCreate, NotificationResponse
│   │   │   ├── file.py            # FileCreate, FileResponse
│   │   │   ├── audit_log.py       # AuditLogResponse
│   │   │   └── two_factor.py      # TwoFactorSetupResponse
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── organization_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── team_repository.py
│   │   │   ├── task_repository.py
│   │   │   ├── api_key_repository.py
│   │   │   ├── notification_repository.py
│   │   │   ├── file_repository.py
│   │   │   └── audit_log_repository.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py           # Auth business logic
│   │   │   ├── organization_service.py   # Org business logic
│   │   │   ├── project_service.py        # Project business logic
│   │   │   ├── team_service.py           # Team business logic
│   │   │   ├── task_service.py           # Task business logic
│   │   │   ├── api_key_service.py        # API key business logic
│   │   │   ├── notification_service.py   # Notification business logic
│   │   │   ├── file_service.py           # File upload/download business logic
│   │   │   ├── audit_log_service.py      # Audit log business logic
│   │   │   └── permission_service.py     # RBAC permission checks
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── storage.py         # Local + S3 storage abstraction
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py      # Celery application config
│   │   │   └── tasks.py           # Background task definitions
│   │   ├── middleware/
│   │   │   └── __init__.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py        # Test fixtures and setup
│   │       ├── test_auth.py       # Auth flow tests
│   │       ├── test_2fa.py        # 2FA tests
│   │       ├── test_projects.py   # Project CRUD + RBAC tests
│   │       ├── test_tasks.py      # Task CRUD + RBAC tests
│   │       ├── test_teams.py      # Team CRUD + RBAC tests
│   │       ├── test_files.py      # File upload/download tests
│   │       ├── test_notifications.py
│   │       ├── test_api_keys.py
│   │       ├── test_audit_logs.py
│   │       ├── test_tenant_isolation.py
│   │       └── test_config.py
│   ├── requirements.txt           # Python dependencies
│   └── pyproject.toml             # Project metadata
├── frontend/
│   ├── .eslintrc.json
│   ├── .gitignore
│   ├── next-env.d.ts
│   ├── next.config.js
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home/landing page
│   │   ├── globals.css            # Global styles
│   │   ├── providers/
│   │   │   ├── providers.tsx
│   │   │   ├── providers-wrapper.tsx
│   │   │   ├── auth-provider.tsx
│   │   │   └── toast-provider.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts         # Auth mutations (login, register, logout)
│   │   │   └── useApiError.ts     # API error handling
│   │   ├── types/
│   │   │   └── api.ts             # TypeScript interfaces
│   │   ├── schemas/
│   │   │   └── auth.ts            # Zod validation schemas
│   │   ├── services/
│   │   │   ├── apiKeys.ts
│   │   │   ├── auditLogs.ts
│   │   │   ├── files.ts
│   │   │   ├── notifications.ts
│   │   │   ├── projects.ts
│   │   │   ├── tasks.ts
│   │   │   └── teams.ts
│   │   ├── components/
│   │   │   ├── auth-redirect.tsx
│   │   │   ├── dashboard-sidebar.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── protected-route.tsx
│   │   │   └── ui/
│   │   │       ├── button.tsx
│   │   │       ├── card.tsx
│   │   │       └── input.tsx
│   │   ├── (auth)/
│   │   │   ├── layout.tsx
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   ├── forgot-password/page.tsx
│   │   │   └── reset-password/page.tsx
│   │   └── (dashboard)/
│   │       ├── layout.tsx
│   │       ├── dashboard/page.tsx
│   │       ├── organizations/page.tsx
│   │       ├── organizations/[id]/page.tsx
│   │       ├── organizations/[id]/members/page.tsx
│   │       ├── projects/page.tsx
│   │       ├── tasks/page.tsx
│   │       ├── team/page.tsx
│   │       ├── api-keys/page.tsx
│   │       ├── notifications/page.tsx
│   │       ├── files/page.tsx
│   │       ├── audit-logs/page.tsx
│   │       └── settings/page.tsx
│   └── ...
├── docs/
│   └── windows-development.md     # Windows-specific development guide
├── scripts/
│   ├── setup.ps1                  # Environment setup script
│   ├── dev.ps1                    # Start all dev services
│   ├── start-backend.ps1          # Start FastAPI server
│   ├── start-frontend.ps1         # Start Next.js dev server
│   ├── start-worker.ps1           # Start Celery worker
│   ├── test.ps1                   # Run backend tests
│   └── migrate.ps1                 # Alembic migration helper
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
└── LICENSE                        # MIT License
```

---

## 🗄️ Database Schema

### Entity Relationship Overview

```
User
  ├── memberships (Membership)
  ├── owned_organizations (Organization)
  ├── refresh_tokens (RefreshToken)
  ├── password_reset_tokens (PasswordResetToken)
  ├── email_verifications (EmailVerification)
  └── api_keys (ApiKey)

Organization
  ├── memberships (Membership)
  ├── projects (Project)
  ├── teams (Team)
  ├── files (File)
  ├── notifications (Notification)
  ├── audit_logs (AuditLog)
  └── api_keys (ApiKey)

Project
  └── tasks (Task)

Team
  └── members (Membership)
```

### Core Tables

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED |
| password_hash | VARCHAR(255) | NOT NULL |
| first_name | VARCHAR(255) | NOT NULL |
| last_name | VARCHAR(255) | NOT NULL |
| avatar_url | VARCHAR(255) | NULLABLE |
| is_active | BOOLEAN | DEFAULT TRUE, NOT NULL |
| is_verified | BOOLEAN | DEFAULT FALSE, NOT NULL |
| last_login_at | TIMESTAMP | NULLABLE |
| totp_secret | VARCHAR(255) | NULLABLE |
| totp_enabled | BOOLEAN | DEFAULT FALSE, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### organizations
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(255) | UNIQUE, NOT NULL |
| logo_url | VARCHAR(255) | NULLABLE |
| owner_id | VARCHAR(255) | FOREIGN KEY users.id, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### memberships
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| user_id | VARCHAR(255) | FOREIGN KEY users.id ON DELETE CASCADE, NOT NULL |
| role | ENUM | OWNER/ADMIN/MANAGER/MEMBER/VIEWER, NOT NULL |
| status | ENUM | PENDING/ACTIVE/INACTIVE, NOT NULL |
| invited_at | TIMESTAMP | NOT NULL |
| joined_at | TIMESTAMP | NULLABLE |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### projects
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULLABLE |
| status | ENUM | ACTIVE/ARCHIVED/DRAFT, NOT NULL |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### teams
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULLABLE |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### tasks
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | NULLABLE |
| status | ENUM | TODO/IN_PROGRESS/REVIEW/DONE, NOT NULL |
| priority | ENUM | LOW/MEDIUM/HIGH/URGENT, NOT NULL |
| assignee_id | VARCHAR(255) | FOREIGN KEY users.id, NULLABLE |
| project_id | VARCHAR(255) | FOREIGN KEY projects.id ON DELETE CASCADE, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| updated_at | TIMESTAMP | server_default NOW(), onupdate NOW(), NOT NULL |

#### api_keys
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| created_by | VARCHAR(255) | FOREIGN KEY users.id, NOT NULL |
| name | VARCHAR(255) | NOT NULL |
| key_prefix | VARCHAR(12) | NOT NULL |
| key_hash | VARCHAR(64) | SHA-256, NOT NULL, UNIQUE |
| scopes | TEXT | JSON array, NULLABLE |
| expires_at | TIMESTAMP | NULLABLE |
| last_used_at | TIMESTAMP | NULLABLE |
| revoked_at | TIMESTAMP | NULLABLE |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |

#### files
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| uploaded_by | VARCHAR(255) | FOREIGN KEY users.id, NOT NULL |
| filename | VARCHAR(255) | NOT NULL |
| storage_key | VARCHAR(255) | UNIQUE, INDEXED, NOT NULL |
| content_type | VARCHAR(255) | NOT NULL |
| size | INTEGER | NOT NULL |
| checksum | VARCHAR(64) | SHA-256, NOT NULL |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |
| deleted_at | TIMESTAMP | NULLABLE |

#### notifications
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| user_id | VARCHAR(255) | FOREIGN KEY users.id ON DELETE CASCADE, NOT NULL |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| type | VARCHAR(255) | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| message | TEXT | NOT NULL |
| data | TEXT | JSON, NULLABLE |
| is_read | BOOLEAN | DEFAULT FALSE, NOT NULL |
| read_at | TIMESTAMP | NULLABLE |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |

#### audit_logs
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| organization_id | VARCHAR(255) | FOREIGN KEY organizations.id ON DELETE CASCADE, NOT NULL |
| action | VARCHAR(255) | NOT NULL, INDEXED |
| resource_type | VARCHAR(255) | NOT NULL, INDEXED |
| resource_id | VARCHAR(255) | NULLABLE |
| user_id | VARCHAR(255) | FOREIGN KEY users.id, NULLABLE |
| ip_address | VARCHAR(45) | NULLABLE |
| user_agent | TEXT | NULLABLE |
| details | TEXT | JSON, NULLABLE |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL, INDEXED |

#### refresh_tokens
| Column | Type | Constraints |
|--------|------|-------------|
| id | VARCHAR(255) | PRIMARY KEY |
| token | VARCHAR(255) | UNIQUE, NOT NULL |
| user_id | VARCHAR(255) | FOREIGN KEY users.id ON DELETE CASCADE, NOT NULL |
| expires_at | TIMESTAMP | NOT NULL |
| revoked_at | TIMESTAMP | NULLABLE |
| created_at | TIMESTAMP | server_default NOW(), NOT NULL |

---

## 📡 API Reference

### Base URL
```
/api/v1
```

### Authentication

All authenticated endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

API key authentication is also supported:
```
Authorization: <nx_live_...>
```

### Endpoints

#### Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login with email/password | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/logout` | Logout (revoke refresh token) | Yes |
| POST | `/auth/logout-all` | Logout all devices | Yes |
| POST | `/auth/verify-email` | Verify email address | No |
| POST | `/auth/request-password-reset` | Request password reset | No |
| POST | `/auth/reset-password` | Reset password with token | No |
| GET | `/auth/me` | Get current user | Yes |

#### Two-Factor Authentication

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/2fa/setup` | Generate 2FA secret | Yes |
| POST | `/2fa/enable` | Enable 2FA after verification | Yes |
| POST | `/2fa/disable` | Disable 2FA | Yes |
| GET | `/2fa/status` | Get 2FA status | Yes |

#### Organizations

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/organizations` | Create organization | Yes |
| GET | `/organizations` | List user's organizations | Yes |
| GET | `/organizations/{id}` | Get organization | Yes |
| PATCH | `/organizations/{id}` | Update organization | Yes |
| DELETE | `/organizations/{id}` | Delete organization | Yes |
| POST | `/organizations/{id}/members` | Invite member | Yes |
| POST | `/organizations/{id}/members/accept` | Accept invitation | Yes |
| GET | `/organizations/{id}/members` | List members | Yes |
| PATCH | `/organizations/{id}/members/{user_id}` | Update member role | Yes |
| DELETE | `/organizations/{id}/members/{user_id}` | Remove member | Yes |

#### Projects

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/projects` | Create project | Yes |
| GET | `/projects` | List projects (query: organization_id) | Yes |
| GET | `/projects/{id}` | Get project | Yes |
| PATCH | `/projects/{id}` | Update project | Yes |
| DELETE | `/projects/{id}` | Delete project | Yes |

#### Teams

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/teams` | Create team | Yes |
| GET | `/teams` | List teams (query: organization_id) | Yes |
| GET | `/teams/{id}` | Get team | Yes |
| PATCH | `/teams/{id}` | Update team | Yes |
| DELETE | `/teams/{id}` | Delete team | Yes |

#### Tasks

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/tasks` | Create task | Yes |
| GET | `/tasks` | List tasks (query: project_id) | Yes |
| GET | `/tasks/{id}` | Get task | Yes |
| PATCH | `/tasks/{id}` | Update task | Yes |
| DELETE | `/tasks/{id}` | Delete task | Yes |

#### API Keys

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api-keys` | Create API key | Yes |
| GET | `/api-keys` | List API keys (query: organization_id) | Yes |
| GET | `/api-keys/{id}` | Get API key | Yes |
| POST | `/api-keys/{id}/revoke` | Revoke API key | Yes |

#### Notifications

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/notifications` | Create notification | Yes |
| GET | `/notifications` | List notifications (query: unread_only) | Yes |
| GET | `/notifications/{id}` | Get notification | Yes |
| POST | `/notifications/{id}/read` | Mark as read | Yes |
| POST | `/notifications/read-all` | Mark all as read | Yes |

#### Files

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/files/upload` | Upload file (multipart/form-data) | Yes |
| GET | `/files` | List files (query: organization_id) | Yes |
| GET | `/files/{id}` | Get file metadata | Yes |
| GET | `/files/{id}/download` | Download file | Yes |
| DELETE | `/files/{id}` | Delete file (soft delete) | Yes |

#### Audit Logs

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/audit-logs` | List audit logs (query: organization_id, resource_type, resource_id, user_id, limit, offset) | Yes |

#### Health Checks

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | Basic health check | No |
| GET | `/ready` | Readiness check | No |

### Response Format

All responses follow this structure:

**Success:**
```json
{
  "id": "usr_...",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Error:**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Organization not found",
    "details": {}
  }
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## 🖥️ Frontend Routes

### Public Routes

| Path | Page | Description |
|------|------|-------------|
| `/` | Home | Landing page |
| `/login` | Login | User login |
| `/register` | Register | User registration |
| `/forgot-password` | Forgot Password | Request password reset |
| `/reset-password` | Reset Password | Reset password with token |

### Protected Routes (Dashboard)

| Path | Page | Description |
|------|------|-------------|
| `/dashboard` | Dashboard | Metrics overview |
| `/organizations` | Organizations | List organizations |
| `/organizations/{id}` | Organization Detail | Organization details |
| `/organizations/{id}/members` | Members | Organization members |
| `/projects` | Projects | List projects |
| `/tasks` | Tasks | List tasks |
| `/team` | Team | List teams |
| `/api-keys` | API Keys | Manage API keys |
| `/notifications` | Notifications | View notifications |
| `/files` | Files | File management |
| `/audit-logs` | Audit Logs | View audit trail |
| `/settings` | Settings | Account settings |

---

## 🔒 Security

### Authentication & Authorization

- **Password Hashing**: bcrypt via passlib with auto-deprecation
- **JWT Access Tokens**: HS256, 30-minute expiration
- **JWT Refresh Tokens**: Separate secret, 7-day expiration, token rotation
- **2FA/TOTP**: pyotp-based TOTP with 5-minute challenge tokens
- **API Keys**: SHA-256 hashed, never exposed after creation, scoped by organization

### Rate Limiting

- **Default**: 100 requests/minute per user/IP
- **Auth Endpoints**: 10 requests/minute per user/IP
- **Backend**: slowapi with Redis storage
- **Identifier**: User ID when authenticated, IP address otherwise

### Tenant Isolation

- All service-layer methods verify active membership before data access
- Queries always scoped to `organization_id`
- Cross-tenant access returns 403 Forbidden
- Dedicated test suite for tenant isolation

### RBAC (Role-Based Access Control)

#### Roles

| Role | Description |
|------|-------------|
| OWNER | Full organization control |
| ADMIN | Management except org deletion/owner changes |
| MANAGER | Project and team management |
| MEMBER | Standard team member |
| VIEWER | Read-only access |

#### Permission Matrix

| Permission | OWNER | ADMIN | MANAGER | MEMBER | VIEWER |
|------------|-------|-------|---------|--------|--------|
| org:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| org:update | ✓ | ✓ | - | - | - |
| org:delete | ✓ | - | - | - | - |
| org:manage_members | ✓ | ✓ | - | - | - |
| org:invite_members | ✓ | ✓ | - | - | - |
| team:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| team:create | ✓ | ✓ | ✓ | - | - |
| team:update | ✓ | ✓ | ✓ | - | - |
| team:delete | ✓ | ✓ | - | - | - |
| project:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| project:create | ✓ | ✓ | ✓ | - | - |
| project:update | ✓ | ✓ | ✓ | - | - |
| project:delete | ✓ | ✓ | - | - | - |
| task:view | ✓ | ✓ | ✓ | ✓ | ✓ |
| task:create | ✓ | ✓ | ✓ | - | - |
| task:update | ✓ | ✓ | ✓ | ✓ | - |
| task:delete | ✓ | ✓ | - | - | - |
| api_key:create | ✓ | ✓ | - | - | - |
| api_key:view | ✓ | ✓ | - | - | - |
| api_key:revoke | ✓ | ✓ | - | - | - |
| audit_log:view | ✓ | ✓ | - | - | - |

### Data Protection

- **Secrets in Environment**: All secrets loaded from `.env` via pydantic-settings
- **No Hardcoded Secrets**: Zero hardcoded credentials in source code
- **Password Reset Tokens**: Not logged (security fix applied)
- **API Keys**: Returned once at creation, never logged
- **Soft Deletes**: Files and sensitive data use soft deletes
- **CORS**: Configurable origins with credentials support

---

## 🧪 Testing

### Backend Tests

**Test Framework**: pytest with pytest-asyncio  
**Test Client**: httpx AsyncClient  
**Coverage**: 108 tests across 12 test files

#### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_auth.py` | Registration, login, refresh, logout, password reset | Auth flows |
| `test_2fa.py` | Setup, enable, disable, verify, recovery | 2FA flows |
| `test_projects.py` | CRUD, RBAC, tenant isolation | Projects |
| `test_tasks.py` | CRUD, RBAC, tenant isolation | Tasks |
| `test_teams.py` | CRUD, RBAC, tenant isolation | Teams |
| `test_files.py` | Upload, download, delete, tenant isolation | Files |
| `test_notifications.py` | CRUD, read/unread, tenant isolation | Notifications |
| `test_api_keys.py` | CRUD, authentication, expiration, tenant isolation | API Keys |
| `test_audit_logs.py` | Listing, filtering, tenant isolation | Audit Logs |
| `test_tenant_isolation.py` | Cross-tenant access prevention | Security |
| `test_config.py` | Configuration validation | Config |

#### Running Tests

```powershell
# Run all tests
.\scripts\test.ps1

# Run with coverage
.\scripts\test.ps1 -Coverage -Verbose
```

**Expected Output**: `108 passed`

### Frontend Verification

```powershell
# Type checking
cd frontend
npm run type-check

# Linting
npm run lint

# Production build
npm run build
```

**Expected Output**:
- TypeScript: 0 errors
- Lint: 0 warnings/errors
- Build: 18 routes built successfully

---

## ⚡ Performance

### Backend

- **Async Stack**: Full async/await with SQLAlchemy 2.x async sessions
- **Database Connection Pooling**: Configurable pool size (default: 20) with overflow (default: 10)
- **Rate Limiting**: Redis-backed per-user/IP limiting
- **Indexing**: Strategic indexes on foreign keys, timestamps, and frequently queried columns

### Frontend

- **Next.js 14**: App Router with React Server Components
- **TanStack Query**: Intelligent caching and background refetching
- **Code Splitting**: Automatic route-based code splitting
- **Production Build**: Standalone output for minimal deployment size

---

## 🚢 Deployment

### Environment Variables

See `.env.example` for the complete list. Key production variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_ENV` | Environment (production/development) | Yes |
| `DEBUG` | Debug mode (false in production) | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `JWT_REFRESH_SECRET` | JWT refresh secret | Yes |
| `STORAGE_ENDPOINT` | S3-compatible endpoint | Yes |
| `STORAGE_ACCESS_KEY` | Storage access key | Yes |
| `STORAGE_SECRET_KEY` | Storage secret key | Yes |
| `STORAGE_BUCKET` | Storage bucket name | Yes |
| `CELERY_BROKER_URL` | Celery broker URL | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | Yes |

### Database Setup

```powershell
# Create database
psql -U postgres -c "CREATE DATABASE nexus;"

# Run migrations
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### Starting Services

**Backend:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Celery Worker:**
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info
```

**Frontend:**
```powershell
cd frontend
npm run build
npm run start
```

### Deployment Options

| Component | Recommended Options |
|-----------|---------------------|
| Frontend | Vercel, Netlify, AWS Amplify |
| Backend | Railway, Render, AWS ECS, Fly.io |
| Database | AWS RDS, Railway, Supabase, Neon |
| Redis | Upstash, AWS ElastiCache, Redis Cloud |
| Storage | AWS S3, DigitalOcean Spaces, MinIO |
| Task Queue | Celery with Redis/RabbitMQ |

---

## ⚙️ Configuration

### Backend Configuration

All backend configuration is managed via `app/core/config.py` using pydantic-settings.

**Configuration Sources** (in order of precedence):
1. Environment variables
2. `.env` file
3. Default values

### Frontend Configuration

Frontend configuration is via `next.config.js`:

```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'slowapi'`  
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Issue**: `alembic.util.exc.CommandError: Can't locate revision`  
**Solution**: Ensure `alembic/versions/` contains all migration files and `alembic/env.py` is configured for async.

**Issue**: Database connection errors  
**Solution**: Verify PostgreSQL is running and `DATABASE_URL` is correct:
```powershell
psql -U postgres -c "SELECT 1"
```

### Frontend Issues

**Issue**: `NEXT_PUBLIC_API_URL` not working  
**Solution**: Ensure the variable is set in the environment before running `npm run dev`:
```powershell
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev
```

**Issue**: TypeScript errors after `git pull`  
**Solution**: Clear Next.js cache and reinstall dependencies:
```powershell
Remove-Item -Recurse -Force .next
npm install
```

---

## 🤝 Contributing

This is a portfolio project demonstrating production-grade software engineering. Contributions are welcome.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes following existing patterns
4. Run tests: `.\scripts\test.ps1`
5. Run lint: `npm run lint` (frontend)
6. Submit a pull request

### Code Standards

- **Backend**: Follow PEP 8, use type hints, write tests for new features
- **Frontend**: Follow existing component patterns, use TypeScript, validate with Zod
- **Commits**: Use conventional commit format

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 👤 Author

Built as a technical portfolio project demonstrating:
- Full-stack TypeScript/Python development
- Multi-tenant SaaS architecture
- Production-grade security practices
- Comprehensive testing strategies
- Modern DevOps workflows

**GitHub**: [@anujghosh1220](https://github.com/anujghosh1220)

---

## 📚 Additional Documentation

- [Windows Development Guide](docs/windows-development.md)
- [CI/CD Pipeline](.github/workflows/ci.yml)
- [API Documentation (Swagger)](http://localhost:8000/docs) (when running locally)
- [API Documentation (ReDoc)](http://localhost:8000/redoc) (when running locally)

---

## 🗺️ Roadmap

### Completed
- ✅ Multi-tenant architecture with RBAC
- ✅ Authentication (email/password, JWT, refresh tokens)
- ✅ Two-factor authentication (TOTP)
- ✅ Organization management with invitations
- ✅ Project, Team, and Task management
- ✅ API key authentication
- ✅ Audit logging
- ✅ Notifications
- ✅ File upload with object storage
- ✅ Rate limiting
- ✅ Comprehensive test suite (108 tests)
- ✅ Production-ready frontend with 18 routes
- ✅ Windows development scripts
- ✅ GitHub Actions CI

### Future Considerations
- Docker containerization
- OAuth providers (Google, GitHub)
- WebSocket real-time updates
- Advanced analytics dashboard
- Email provider integration (SendGrid, SES)
- Background job processing (Celery tasks)
- Advanced file management (previews, versions)
- Mobile applications (React Native)

---

**NEXUS** — Production-Grade Multi-Tenant SaaS Platform

Built with FastAPI, SQLAlchemy, Next.js, and TypeScript.

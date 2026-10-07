# NEXUS

**One workspace. Every operation.**

A production-grade workspace platform for teams, projects, workflows, and APIs.

## 🚀 Features

- **Multi-tenant Architecture**: Secure tenant isolation with proper RBAC
- **User Management**: Registration, authentication, OAuth, password reset
- **Organizations**: Create and manage multiple organizations
- **Teams**: Organize users into functional teams
- **Projects**: Track projects with custom keys and identifiers
- **Task Management**: Kanban boards, comments, labels, activity tracking
- **Developer API**: RESTful API with API keys, scopes, and usage analytics
- **Audit Logging**: Comprehensive audit trail for security-sensitive actions
- **Real-time Notifications**: In-app and email notifications
- **File Management**: Secure file uploads with object storage
- **Background Processing**: Celery + Redis for async operations
- **Rate Limiting**: API rate limiting for security
- **Analytics**: Real-time dashboards and metrics

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Redis
- Celery
- Pydantic v2

**Frontend:**
- Next.js 14
- TypeScript
- React
- Tailwind CSS
- TanStack Query
- React Hook Form
- Zod

## 📦 Project Structure

```
nexus/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration, security, database
│   │   ├── api/           # API routes
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── repositories/  # Data access layer
│   │   ├── services/      # Business logic
│   │   ├── workers/       # Celery tasks
│   │   ├── middleware/    # Custom middleware
│   │   ├── utils/         # Utilities
│   │   └── tests/         # Tests
│   ├── alembic/           # Database migrations
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── components/    # Reusable components
│   │   ├── features/      # Feature-specific components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utilities
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   ├── schemas/       # Zod schemas
│   │   └── providers/     # Context providers
│   ├── package.json
│   └── tsconfig.json
├── docs/                  # Documentation
├── scripts/               # Development scripts
└── README.md
```

## 🛠️ Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis-compatible service (e.g., Memurai) or Redis
- MinIO or S3-compatible object storage
- Git

### Quick Start

```powershell
git clone <repository-url>
cd nexus
.\scripts\setup.ps1
```

Then follow the prompts to install dependencies and configure your environment.

### Manual Setup

#### 1. Clone and Install Dependencies

```powershell
git clone <repository-url>
cd nexus

# Install Python dependencies
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
cd ..
```

#### 2. Configure Environment

Copy the environment template:

```powershell
Copy-Item .env.example backend\.env
```

Edit `backend\.env` with your configuration:

```env
DATABASE_URL=postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus
REDIS_URL=redis://localhost:6379/0
STORAGE_ENDPOINT=localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=nexus
```

#### 3. Database Setup

Create the development database:

```powershell
psql -U postgres
CREATE DATABASE nexus;
\q
```

Run migrations:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
cd ..
```

#### 4. Start Services

In separate terminals:

```powershell
# Terminal 1 — Backend
.\scripts\start-backend.ps1

# Terminal 2 — Celery Worker
.\scripts\start-worker.ps1

# Terminal 3 — Frontend
.\scripts\start-frontend.ps1
```

Or start everything at once (requires PostgreSQL, Redis, and MinIO already running):

```powershell
.\scripts\dev.ps1
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Backend Tests

```powershell
.\scripts\test.ps1
```

With coverage:

```powershell
.\scripts\test.ps1 -Coverage -Verbose
```

### Frontend Tests

```powershell
cd frontend
npm run lint
npm run type-check
npm run build
```

## 📊 API Documentation

Interactive API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## 🔒 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Refresh token rotation
- Rate limiting on all endpoints
- Tenant isolation enforced at the service layer
- RBAC with fine-grained permissions
- API keys with scope-based access
- Comprehensive audit logging
- Secure file upload validation

## 📝 Database Migrations

Create a new migration:

```powershell
.\scripts\migrate.ps1 -Message "description"
```

Apply migrations:

```powershell
.\scripts\migrate.ps1 -Upgrade
```

Rollback migrations:

```powershell
.\scripts\migrate.ps1 -Downgrade -Steps 1
```

## 🚢 Deployment

### Production Configuration

Set the following environment variables for production:
- `APP_ENV=production`
- `DEBUG=false`
- Secure `SECRET_KEY`, `JWT_SECRET`, `JWT_REFRESH_SECRET`
- Configure production database URL
- Configure production Redis URL
- Configure object storage (AWS S3 or compatible)
- Configure email provider (SendGrid, SES, etc.)
- Configure OAuth providers

### Deployment Options

- **Frontend**: Vercel, Netlify, or any Node.js hosting
- **Backend**: Railway, Render, AWS ECS, or any Python hosting
- **Database**: Managed PostgreSQL (AWS RDS, Railway, etc.)
- **Redis**: Managed Redis (AWS ElastiCache, Upstash, etc.)
- **Object Storage**: AWS S3, DigitalOcean Spaces, or S3-compatible

## 📚 Documentation

- [Windows Development Guide](docs/windows-development.md)
- [Architecture Documentation](docs/architecture.md)
- [Database Documentation](docs/database.md)
- [Security Documentation](docs/security.md)
- [API Documentation](docs/api.md)

## 🤝 Contributing

This is a portfolio project demonstrating production-grade software engineering.

## 📄 License

MIT License

## 👤 Author

Built as a technical portfolio project.

---

**NEXUS** — Production-Grade Multi-Tenant SaaS Platform

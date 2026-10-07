# NEXUS — Windows Native Development Guide

This guide explains how to set up and run NEXUS natively on Windows without Docker.

## Prerequisites

Install the following software before proceeding:

- [Python 3.12+](https://www.python.org/downloads/windows/)
- [Node.js 20+](https://nodejs.org/)
- [PostgreSQL 16+](https://www.postgresql.org/download/windows/)
- [Redis-compatible service](https://www.memurai.com/) or [Redis for Windows](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/)
- [MinIO](https://min.io/download#/windows)
- Git

### PowerShell Execution Policy

If you cannot run PowerShell scripts, set the execution policy:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Project Setup

```powershell
git clone <repository-url>
cd nexus
.\scripts\setup.ps1
```

The setup script will:
1. Verify Python, Node.js, PostgreSQL, Redis, and MinIO are installed
2. Create a Python virtual environment at `backend\.venv`
3. Install Python dependencies
4. Install Node.js dependencies
5. Create `backend\.env` from `.env.example`

## Database Setup

### Install PostgreSQL

1. Download and run the PostgreSQL installer from https://www.postgresql.org/download/windows/
2. During installation, set a password for the `postgres` superuser
3. Remember this password — you will need it for `.env`

### Create the Development Database

```powershell
# Open psql as the postgres superuser
psql -U postgres

# Create the nexus database
CREATE DATABASE nexus;

# Create the nexus user (optional — you can use postgres directly)
CREATE USER nexus WITH PASSWORD 'nexus_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE nexus TO nexus;

# Exit
\q
```

### Configure `.env`

Edit `backend\.env` and set your database credentials:

```env
DATABASE_URL=postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus
```

If you skipped creating the `nexus` user, use:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/nexus
```

### Run Migrations

```powershell
.\scripts\migrate.ps1 -Upgrade
```

Or manually:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### Verify Database

```powershell
psql -U nexus -d nexus -c "\dt"
```

You should see the NEXUS tables listed.

## Redis Setup

NEXUS uses Redis for:
- Celery message broker
- Caching
- Rate limiting

### Install Redis/Memurai

**Preferred for Windows: Memurai**
1. Download from https://www.memurai.com/
2. Install and start the Memurai service
3. Verify it is running on port 6379:

```powershell
redis-cli ping
# Should return: PONG
```

### Configure `.env`

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Object Storage Setup (MinIO)

NEXUS uses S3-compatible object storage. MinIO is the recommended local option.

### Install MinIO

1. Download `minio.exe` from https://min.io/download#/windows
2. Create a data directory:
   ```powershell
   New-Item -ItemType Directory -Path "C:\minio-data" -Force
   ```
3. Start MinIO:
   ```powershell
   minio server C:\minio-data --address :9000 --console-address :9001
   ```
4. Access the MinIO Console at http://localhost:9001
   - Default credentials: `minioadmin` / `minioadmin`
5. Create a bucket named `nexus` via the console or API.

### Configure `.env`

```env
STORAGE_ENDPOINT=localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=nexus
STORAGE_REGION=us-east-1
STORAGE_USE_SSL=false
```

## Starting the Application

### Terminal 1 — FastAPI Backend

```powershell
.\scripts\start-backend.ps1
```

The API will be available at:
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health
- Ready: http://localhost:8000/ready

### Terminal 2 — Celery Worker

```powershell
.\scripts\start-worker.ps1
```

### Terminal 3 — Next.js Frontend

```powershell
.\scripts\start-frontend.ps1
```

The frontend will be available at http://localhost:3000

### One-Command Start (All Services)

If PostgreSQL, Redis/Memurai, and MinIO are already running:

```powershell
.\scripts\dev.ps1
```

This will:
1. Verify all dependencies are reachable
2. Run database migrations
3. Start backend, worker, and frontend

## Running Tests

```powershell
.\scripts\test.ps1
```

With coverage:

```powershell
.\scripts\test.ps1 -Coverage -Verbose
```

## Code Quality

### Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
ruff check .
mypy .
```

### Frontend

```powershell
cd frontend
npm run lint
npm run type-check
npm run build
```

## Database Migrations

### Create a new migration

```powershell
.\scripts\migrate.ps1 -Message "Add users table"
```

### Apply migrations

```powershell
.\scripts\migrate.ps1 -Upgrade
```

### Rollback one migration

```powershell
.\scripts\migrate.ps1 -Downgrade -Steps 1
```

### View current migration

```powershell
.\scripts\migrate.ps1
```

## Troubleshooting

### PowerShell Execution Policy

If you see `cannot be loaded because running scripts is disabled`:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

Ensure Python 3.12+ is installed and added to PATH. During installation, check "Add Python to PATH".

### pip Not Found

Use `python -m pip` instead of `pip`.

### Node.js Not Found

Ensure Node.js 20+ is installed. Restart your terminal after installation.

### PostgreSQL Not Running

Start PostgreSQL from Services or via command line:

```powershell
# Find your PostgreSQL data directory
# Usually: C:\Program Files\PostgreSQL\<version>\data
pg_ctl start -D "C:\Program Files\PostgreSQL\16\data"
```

### Port Already in Use

- Port 5432 (PostgreSQL): Stop another PostgreSQL instance or change the port in `postgresql.conf`
- Port 6379 (Redis): Stop another Redis instance or change the port in `redis.conf`
- Port 8000 (Backend): Change `PORT` in `.env` or stop the conflicting process
- Port 3000 (Frontend): Change the port in `frontend\package.json` scripts or stop the conflicting process

### asyncpg / pydantic-core Installation Fails

This should not happen with the current dependency versions, as they all provide prebuilt Windows wheels. If you encounter this:

```powershell
# Ensure pip is up to date
python -m pip install --upgrade pip

# Reinstall with binary packages
pip install --only-binary=:all: -r backend\requirements.txt
```

### Celery Worker Fails to Start

Ensure Redis is running and accessible at `localhost:6379`.

If you see `AttributeError: module 'multiprocessing' has no attribute 'Process'`, ensure you are using `--pool=solo`:

```powershell
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://nexus:nexus_password@localhost:5432/nexus` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection for caching |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery results backend |
| `STORAGE_ENDPOINT` | `localhost:9000` | MinIO/S3 endpoint |
| `STORAGE_ACCESS_KEY` | `minioadmin` | S3 access key |
| `STORAGE_SECRET_KEY` | `minioadmin` | S3 secret key |
| `STORAGE_BUCKET` | `nexus` | S3 bucket name |
| `SECRET_KEY` | *(required)* | Application secret key |
| `JWT_SECRET` | *(required)* | JWT signing secret |
| `JWT_REFRESH_SECRET` | *(required)* | JWT refresh token secret |

## Production Deployment

NEXUS is designed to be deployed to managed infrastructure:

- **Frontend**: Vercel, Netlify, or any Node.js hosting
- **Backend**: Railway, Render, AWS ECS, or any Python hosting
- **Database**: Managed PostgreSQL (AWS RDS, Railway, etc.)
- **Redis**: Managed Redis (AWS ElastiCache, Upstash, etc.)
- **Object Storage**: AWS S3, DigitalOcean Spaces, or S3-compatible storage

Docker is not required for local development or production deployment.

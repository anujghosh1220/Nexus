<#
.SYNOPSIS
    Start all NEXUS development services (backend, worker, frontend).
    Requires PostgreSQL, Redis/Memurai, and MinIO to already be running.
#>

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus"

Write-Host "=== NEXUS Development Server ===" -ForegroundColor Cyan

# Check PostgreSQL
Write-Host "`nChecking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgCheck = psql -U nexus -d nexus -c "SELECT 1;" 2>&1
    Write-Host "  PostgreSQL is running." -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Cannot connect to PostgreSQL." -ForegroundColor Red
    Write-Host "  Start PostgreSQL and try again." -ForegroundColor Red
    Write-Host "  Command: pg_ctl start -D `"C:\Program Files\PostgreSQL\<version>\data`"" -ForegroundColor Gray
    exit 1
}

# Check Redis
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = redis-cli ping 2>&1
    if ($redisCheck -eq "PONG") {
        Write-Host "  Redis is running." -ForegroundColor Green
    } else {
        throw "Redis not responding"
    }
} catch {
    Write-Host "  ERROR: Cannot connect to Redis." -ForegroundColor Red
    Write-Host "  Start Redis/Memurai and try again." -ForegroundColor Red
    exit 1
}

# Check MinIO
Write-Host "`nChecking MinIO..." -ForegroundColor Yellow
try {
    $minioCheck = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -UseBasicParsing -TimeoutSec 5 2>&1
    Write-Host "  MinIO is running." -ForegroundColor Green
} catch {
    Write-Host "  WARNING: Cannot connect to MinIO at http://localhost:9000" -ForegroundColor Yellow
    Write-Host "  Start MinIO if you need object storage." -ForegroundColor Yellow
    Write-Host "  Command: minio server C:\minio-data --address :9000 --console-address :9001" -ForegroundColor Gray
}

# Run migrations
Write-Host "`nRunning database migrations..." -ForegroundColor Cyan
Set-Location "F:\Nexus\backend"
& .\.venv\Scripts\Activate.ps1
alembic upgrade head
Write-Host "  Migrations complete." -ForegroundColor Green

Set-Location "F:\Nexus"

Write-Host "`nStarting services..." -ForegroundColor Cyan

# Start backend in background
Write-Host "`n[Backend] Starting FastAPI on http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", "F:\Nexus\scripts\start-backend.ps1"

Start-Sleep -Seconds 3

# Start worker in background
Write-Host "[Worker] Starting Celery Worker" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", "F:\Nexus\scripts\start-worker.ps1"

Start-Sleep -Seconds 2

# Start frontend in background
Write-Host "[Frontend] Starting Next.js on http://localhost:3000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-File", "F:\Nexus\scripts\start-frontend.ps1"

Write-Host "`n=== All Services Started ===" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "`nClose this window or press Ctrl+C to stop all services." -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Process -Name "uvicorn" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "celery" -Force -ErrorAction SilentlyContinue
    Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
    Write-Host "Services stopped." -ForegroundColor Green
}

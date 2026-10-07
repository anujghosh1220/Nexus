<#
.SYNOPSIS
    Setup the NEXUS development environment on Windows.
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "=== NEXUS Windows Development Setup ===" -ForegroundColor Cyan

# Check Python
Write-Host "`n[1/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install Python 3.12+ from https://www.python.org/downloads/windows/" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "`n[2/5] Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Install Node.js 20+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "  Found: $nodeVersion" -ForegroundColor Green

# Check PostgreSQL
Write-Host "`n[3/5] Checking PostgreSQL..." -ForegroundColor Yellow
$pgInstalled = Get-Command psql -ErrorAction SilentlyContinue
if (-not $pgInstalled) {
    Write-Host "  WARNING: psql not found in PATH." -ForegroundColor Yellow
    Write-Host "  Install PostgreSQL from https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    Write-Host "  Make sure 'psql' is in your PATH." -ForegroundColor Yellow
} else {
    $pgVersion = psql --version 2>&1
    Write-Host "  Found: $pgVersion" -ForegroundColor Green
}

# Check Redis/Memurai
Write-Host "`n[4/5] Checking Redis/Memurai..." -ForegroundColor Yellow
$redisInstalled = Get-Command redis-cli -ErrorAction SilentlyContinue
if (-not $redisInstalled) {
    Write-Host "  WARNING: redis-cli not found in PATH." -ForegroundColor Yellow
    Write-Host "  Install Memurai from https://www.memurai.com/ or Redis for Windows" -ForegroundColor Yellow
    Write-Host "  Make sure 'redis-cli' is in your PATH." -ForegroundColor Yellow
} else {
    $redisVersion = redis-cli --version 2>&1
    Write-Host "  Found: $redisVersion" -ForegroundColor Green
}

# Check MinIO
Write-Host "`n[5/5] Checking MinIO..." -ForegroundColor Yellow
$minioInstalled = Get-Command minio -ErrorAction SilentlyContinue
if (-not $minioInstalled) {
    Write-Host "  WARNING: minio not found in PATH." -ForegroundColor Yellow
    Write-Host "  Download MinIO from https://min.io/download#/windows" -ForegroundColor Yellow
    Write-Host "  Make sure 'minio' is in your PATH." -ForegroundColor Yellow
} else {
    Write-Host "  Found: minio" -ForegroundColor Green
}

# Create Python virtual environment
Write-Host "`n=== Creating Python Virtual Environment ===" -ForegroundColor Cyan
if (-not (Test-Path "backend\.venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv .venv
    Set-Location ..
    Write-Host "  Virtual environment created at backend\.venv" -ForegroundColor Green
} else {
    Write-Host "  Virtual environment already exists at backend\.venv" -ForegroundColor Green
}

# Install Python dependencies
Write-Host "`n=== Installing Python Dependencies ===" -ForegroundColor Cyan
Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Yellow
Set-Location backend
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Set-Location ..
Write-Host "  Python dependencies installed." -ForegroundColor Green

# Install Node.js dependencies
Write-Host "`n=== Installing Node.js Dependencies ===" -ForegroundColor Cyan
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "  Frontend dependencies installed." -ForegroundColor Green
} else {
    Write-Host "  Frontend dependencies already installed." -ForegroundColor Green
}

# Create .env if it doesn't exist
Write-Host "`n=== Environment Configuration ===" -ForegroundColor Cyan
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend\.env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" "backend\.env"
    Write-Host "  Created backend\.env" -ForegroundColor Green
    Write-Host "  IMPORTANT: Edit backend\.env with your actual configuration values!" -ForegroundColor Yellow
} else {
    Write-Host "  backend\.env already exists." -ForegroundColor Green
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "  1. Install PostgreSQL, Redis/Memurai, and MinIO if not already installed" -ForegroundColor White
Write-Host "  2. Create the 'nexus' database in PostgreSQL" -ForegroundColor White
Write-Host "  3. Start PostgreSQL, Redis/Memurai, and MinIO services" -ForegroundColor White
Write-Host "  4. Run: .\scripts\migrate.ps1" -ForegroundColor White
Write-Host "  5. Run: .\scripts\start-backend.ps1" -ForegroundColor White
Write-Host "  6. In a new terminal: .\scripts\start-worker.ps1" -ForegroundColor White
Write-Host "  7. In a new terminal: .\scripts\start-frontend.ps1" -ForegroundColor White
Write-Host "`nOr use: .\scripts\dev.ps1 to start everything (requires services already running)" -ForegroundColor Cyan

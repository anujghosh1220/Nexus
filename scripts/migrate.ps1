<#
.SYNOPSIS
    Run Alembic database migrations.
#>

param(
    [switch]$Upgrade,
    [switch]$Downgrade,
    [int]$Steps = 1,
    [string]$Message
)

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus\backend"

# Activate virtual environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found. Run .\scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1

if ($Message) {
    Write-Host "Creating new migration: $Message" -ForegroundColor Cyan
    alembic revision --autogenerate -m $Message
} elseif ($Downgrade) {
    Write-Host "Downgrading $Steps migration(s)..." -ForegroundColor Yellow
    alembic downgrade -$Steps
} elseif ($Upgrade) {
    Write-Host "Applying all pending migrations..." -ForegroundColor Cyan
    alembic upgrade head
} else {
    Write-Host "Current migration status:" -ForegroundColor Cyan
    alembic current
}

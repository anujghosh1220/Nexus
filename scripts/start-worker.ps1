<#
.SYNOPSIS
    Start the NEXUS Celery worker.
#>

param(
    [switch]$Loglevel = "info"
)

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus\backend"

# Activate virtual environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found. Run .\scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1

Write-Host "Starting NEXUS Celery Worker..." -ForegroundColor Cyan
Write-Host "Note: --pool=solo is used for Windows compatibility" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

celery -A app.workers.celery_app worker --loglevel=$Loglevel --pool=solo

<#
.SYNOPSIS
    Start the NEXUS FastAPI backend server.
#>

param(
    [switch]$Reload = $true
)

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus\backend"

# Activate virtual environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found. Run .\scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1

Write-Host "Starting NEXUS Backend..." -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

if ($Reload) {
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} else {
    uvicorn app.main:app --host 0.0.0.0 --port 8000
}

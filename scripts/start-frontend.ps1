<#
.SYNOPSIS
    Start the NEXUS Next.js frontend development server.
#>

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Node modules not found. Running npm install..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting NEXUS Frontend..." -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

npm run dev

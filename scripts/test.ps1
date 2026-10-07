<#
.SYNOPSIS
    Run NEXUS backend tests.
#>

param(
    [string]$Path = "app/tests",
    [switch]$Coverage,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Set-Location "F:\Nexus\backend"

# Activate virtual environment
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found. Run .\scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\Activate.ps1

$argsList = @($Path)
if ($Coverage) {
    $argsList += "--cov=app"
    $argsList += "--cov-report=term-missing"
}
if ($Verbose) {
    $argsList += "-v"
}

Write-Host "Running tests: $Path" -ForegroundColor Cyan
pytest @argsList

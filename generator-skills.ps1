$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$apiScript = Join-Path $PSScriptRoot "start_api.ps1"
$webScript = Join-Path $PSScriptRoot "start_web.ps1"

Write-Host "🚀 Iniciando Skill Forge backend e frontend..." -ForegroundColor Cyan

Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList @(
    "-NoProfile",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $apiScript
)

Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList @(
    "-NoProfile",
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $webScript
)

Write-Host "✅ Backend e frontend foram iniciados em janelas separadas." -ForegroundColor Green
Write-Host "   API:  http://localhost:8000" -ForegroundColor Green
Write-Host "   Web:  http://localhost:8501" -ForegroundColor Green

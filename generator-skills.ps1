$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$launcher = Join-Path $PSScriptRoot "generator_skills.py"
$python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }

if (-not (Test-Path $launcher)) {
    throw "Arquivo nao encontrado: $launcher"
}

Write-Host "Iniciando launcher unico (API + Web)..." -ForegroundColor Cyan
& $python $launcher

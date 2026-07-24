$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Garante que o .env existe na raiz
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  Arquivo .env criado a partir de .env.example." -ForegroundColor Yellow
    Write-Host "   Preencha SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID antes de usar." -ForegroundColor Yellow
}

$python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }

Write-Host "🚀 Iniciando Skill Forge API em http://localhost:8000" -ForegroundColor Cyan

# --loop asyncio: evita o ConnectionResetError (WinError 10054) do ProactorEventLoop no Windows.
# O parâmetro é ignorado silenciosamente em Linux/macOS.
& $python -m uvicorn src.main:app --reload --port 8000 --app-dir apps/api --loop asyncio

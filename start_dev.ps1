#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Inicia a API Skill Forge e Streamlit Web App de forma coordenada

.DESCRIPTION
    Este script abre dois terminais PowerShell:
    1. Um rodando a API em uma porta específica
    2. Outro rodando o Streamlit Web App

.PARAMETER ApiPort
    Porta da API (padrão: 8000)

.PARAMETER SkipSetup
    Se $true, pula a criação/atualização do .streamlit/secrets.toml

.EXAMPLE
    .\start_dev.ps1 -ApiPort 8000
    .\start_dev.ps1 -ApiPort 58027 -SkipSetup $false
#>

param(
    [int]$ApiPort = 8000,
    [bool]$SkipSetup = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ============================================================================
# Validações iniciais
# ============================================================================

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Arquivo .env criado a partir de .env.example." -ForegroundColor Green
        Write-Host "⚠️  Preencha SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID antes de usar." -ForegroundColor Yellow
    }
}

# ============================================================================
# Configurar secrets do Streamlit com a porta correta
# ============================================================================

if (-not $SkipSetup) {
    $secretsPath = "apps\web\.streamlit\secrets.toml"
    $secretsContent = @"
# Configuração LOCAL gerada por start_dev.ps1
skill_forge_api_url = "http://localhost:$ApiPort"
"@

    Write-Host "🔧 Configurando .streamlit/secrets.toml com porta $ApiPort..." -ForegroundColor Cyan
    Set-Content -Path $secretsPath -Value $secretsContent -Encoding UTF8
    Write-Host "✅ Secrets configurado!" -ForegroundColor Green
}

# ============================================================================
# Iniciar API em novo terminal
# ============================================================================

Write-Host "`n🚀 Abrindo terminal para API..." -ForegroundColor Cyan

$pythonExe = if (Test-Path ".venv\Scripts\python.exe") { 
    ".venv\Scripts\python.exe" 
} else { 
    "python" 
}

$apiCommand = @"
cd "$PSScriptRoot"
Write-Host "🚀 Iniciando Skill Forge API em http://localhost:$ApiPort" -ForegroundColor Cyan
& "$pythonExe" -m uvicorn src.main:app --reload --port $ApiPort --app-dir apps/api --loop asyncio
pause
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCommand -WindowStyle Normal

Write-Host "✅ Terminal da API aberto!" -ForegroundColor Green

# ============================================================================
# Aguardar um pouco para a API inicializar
# ============================================================================

Write-Host "`n⏳ Aguardando 5 segundos para a API inicializar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# ============================================================================
# Iniciar Streamlit em novo terminal
# ============================================================================

Write-Host "🚀 Abrindo terminal para Streamlit..." -ForegroundColor Cyan

$streamlitCommand = @"
cd "$PSScriptRoot"
Write-Host "🚀 Iniciando Streamlit Web App em http://localhost:8501" -ForegroundColor Cyan
Write-Host "💡 A API está em http://localhost:$ApiPort" -ForegroundColor Cyan
& "$pythonExe" -m streamlit run apps/web/src/app.py
pause
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $streamlitCommand -WindowStyle Normal

Write-Host "✅ Terminal do Streamlit aberto!" -ForegroundColor Green

Write-Host @"

╔════════════════════════════════════════════════════════════════════════╗
║                    SKILL FORGE — DESENVOLVIMENTO                       ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  🎯  API:       http://localhost:$ApiPort                              ║
║  🎯  Streamlit: http://localhost:8501                                  ║
║  🎯  Health:    http://localhost:$ApiPort/health                       ║
║                                                                        ║
║  📝  Logs da API aparecem no primeiro terminal (porta $ApiPort)         ║
║  📝  Logs do Streamlit aparecem no segundo terminal (porta 8501)       ║
║                                                                        ║
║  ⚠️  Se receber erro 404 ao otimizar, verifique:                      ║
║     - .streamlit/secrets.toml está configurado com porta $ApiPort     ║
║     - API está rodando no terminal 1                                   ║
║     - Reinicie o Streamlit (Ctrl+R no terminal 2)                     ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "✅ Desenvolvimento pronto! Use os terminais acima para ver logs." -ForegroundColor Green
Write-Host "💡 Pressione Ctrl+C em cada terminal para parar." -ForegroundColor Yellow

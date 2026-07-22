$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".venv/Scripts/python.exe") {
    & ".venv/Scripts/python.exe" -m uvicorn src.main:app --reload --port 8000 --app-dir apps/api
} else {
    python -m uvicorn src.main:app --reload --port 8000 --app-dir apps/api
}

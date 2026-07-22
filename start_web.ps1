$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".venv/Scripts/python.exe") {
    & ".venv/Scripts/python.exe" -m streamlit run apps/web/src/app.py
} else {
    python -m streamlit run apps/web/src/app.py
}

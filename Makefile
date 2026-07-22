dev:
	@echo "Run backend: make dev-api"
	@echo "Run frontend: make dev-web"

dev-api:
	cd apps/api && uvicorn src.main:app --reload --port 8000

dev-api-root:
	uvicorn src.main:app --reload --port 8000 --app-dir apps/api

dev-api-script:
	powershell -ExecutionPolicy Bypass -File ./start_api.ps1

dev-web:
	cd apps/web && streamlit run src/app.py

dev-web-script:
	powershell -ExecutionPolicy Bypass -File ./start_web.ps1

test:
	cd apps/api && pytest
	cd apps/web && python -m pytest

lint:
	cd apps/api && ruff check src tests && mypy src
	cd apps/web && ruff check src tests

build:
	@echo "No build step required for Streamlit frontend"

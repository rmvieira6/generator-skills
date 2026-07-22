# ⚒️ Skill Forge

> Accelerating Stefanini processes with standardised and optimised AI context-artifact generation.

Skill Forge is a web application (FastAPI backend + Streamlit frontend) that generates **AI context artifacts** — `SKILL.md`, `.cursorrules`, `.github/copilot-instructions.md`, `system_instruction` for Vertex AI, and more — for your favourite AI agent or IDE.

---

## ✨ Features

| Feature | Detail |
|---|---|
| **Target agents** | Claude, GitHub Copilot (VS Code), Cursor, Vertex AI, Windsurf, Generic OpenAI-compatible |
| **Context materials** | Files, PostgreSQL, MySQL, REST API, GraphQL, Amazon S3, Google Drive, Repositories, Docs |
| **Secret safety** | Secrets are never stored in plain text — only env-var references (`$env:MY_SECRET`) |
| **Output** | Downloadable `.zip` with the primary artifact, `README.md` with usage instructions, and a ready-to-paste suggested prompt |
| **LLM engine** | SAI Library (Stefanini internal); OpenAI-compatible fallback for local development |

---

## 🏗 Architecture

```
┌──────────────────┐      HTTP/REST       ┌─────────────────────────┐
│  Streamlit UI    │ ──────────────────▶  │  FastAPI Backend        │
│  (port 8501)     │ ◀──────────────────  │  (port 8000)            │
└──────────────────┘                      │                         │
                                          │  ┌───────────────────┐  │
                                          │  │  SAI Library      │  │
                                          │  │  (LLM engine)     │  │
                                          │  └───────────────────┘  │
                                          └─────────────────────────┘
```

- **Backend:** Python 3.11+ · FastAPI · Pydantic v2 · Uvicorn
- **Frontend:** Streamlit
- **LLM:** SAI Library (primary) / OpenAI-compatible endpoint (fallback)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, recommended)

### With Docker Compose

```bash
# Copy and fill in your credentials
cp .env.example .env   # set SAI_API_KEY or OPENAI_API_KEY

docker compose up --build
```

Open **http://localhost:8501** in your browser.

### Local Development (without Docker)

**Backend:**

```bash
cd backend
pip install -r requirements.txt

# Production (SAI Library)
export SAI_API_KEY=your_sai_key

# OR development fallback
export OPENAI_API_KEY=your_openai_key

uvicorn app.main:app --reload
# → http://localhost:8000  (API docs at /docs)
```

**Frontend:**

```bash
cd frontend
pip install -r requirements.txt

export BACKEND_URL=http://localhost:8000
streamlit run app.py
# → http://localhost:8501
```

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SAI_API_KEY` | _(empty)_ | SAI Library API key (production) |
| `SAI_BASE_URL` | `https://api.sai.stefanini.com/v1` | SAI Library endpoint |
| `SAI_MODEL` | `auto` | Model selection (SAI decides internally) |
| `OPENAI_API_KEY` | _(empty)_ | Fallback OpenAI-compatible key (dev only) |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Fallback endpoint |
| `OPENAI_MODEL` | `gpt-4o` | Fallback model |
| `CORS_ORIGINS` | `["http://localhost:8501"]` | Allowed CORS origins |
| `DEBUG` | `false` | Enable debug logging |
| `BACKEND_URL` | `http://localhost:8000` | URL the frontend uses to call the backend |

---

## 🧪 Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── models/
│   │   │   └── schemas.py   # Pydantic models
│   │   ├── routers/
│   │   │   └── generate.py  # /api/v1/generate, /api/v1/download/{token}
│   │   └── services/
│   │       ├── llm.py       # SAI Library integration + fallback
│   │       ├── generator.py # Prompt building & artifact assembly
│   │       └── packager.py  # ZIP creation & token management
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py               # Streamlit UI
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 🔒 Security Notes

- **Secrets** in connection metadata must be supplied as env-var references (`$env:NAME`).  The backend validates this and rejects any plain-text secret value.
- Generated ZIP files are stored in a temporary directory (`/tmp/skill-forge`) and are ephemeral — they are deleted on server restart.
- No secret values are logged or persisted.

---

## 📄 License

Internal Stefanini project.

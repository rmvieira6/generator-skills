"""
Skill Forge – Streamlit frontend.

Provides a multi-step wizard UI:
  1. Choose target agent / IDE.
  2. Write a high-level description of the desired skill.
  3. Add context materials (files, DB connections, REST APIs, etc.).
  4. Generate → download the ZIP artifact + copy the suggested prompt.
"""

from __future__ import annotations

import io
import os

import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

CONNECTOR_LABELS = {
    "file": "📄 File",
    "postgres": "🐘 PostgreSQL",
    "mysql": "🐬 MySQL",
    "rest_api": "🌐 REST API",
    "graphql": "⚡ GraphQL",
    "s3": "☁️ Amazon S3",
    "google_drive": "📂 Google Drive",
    "repository": "🗂 Repository",
    "docs": "📚 Documentation",
}

AGENT_ICONS = {
    "claude": "🤖",
    "copilot": "🐙",
    "cursor": "✏️",
    "vertex_ai": "🔷",
    "windsurf": "🏄",
    "generic_openai": "⚙️",
}

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Skill Forge",
    page_icon="⚒️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "materials" not in st.session_state:
    st.session_state.materials = []
if "result" not in st.session_state:
    st.session_state.result = None
if "agents" not in st.session_state:
    st.session_state.agents = []


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


@st.cache_data(ttl=300)
def fetch_agents() -> list[dict]:
    try:
        resp = requests.get(f"{API_BASE}/agents", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not load agent list from backend: {exc}")
        return []


def call_generate(payload: dict) -> dict | None:
    try:
        resp = requests.post(f"{API_BASE}/generate", json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        detail = exc.response.json().get("detail", str(exc)) if exc.response else str(exc)
        st.error(f"Generation failed: {detail}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unexpected error: {exc}")
    return None


def fetch_zip(token: str) -> bytes | None:
    try:
        resp = requests.get(f"{API_BASE}/download/{token}", timeout=60)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not download ZIP: {exc}")
    return None


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


def render_header() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
            <h1>⚒️ Skill Forge</h1>
            <p style="font-size:1.1rem; color:#888;">
                Generate AI context artifacts for your favourite agent or IDE
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()


def render_step1_agent(agents: list[dict]) -> str | None:
    st.subheader("Step 1 – Choose your target agent")
    if not agents:
        st.info("Backend is unavailable. Start the FastAPI server and refresh.")
        return None

    cols = st.columns(len(agents))
    selected = st.session_state.get("selected_agent")
    for col, agent in zip(cols, agents):
        icon = AGENT_ICONS.get(agent["id"], "🤖")
        label = f"{icon} {agent['display_name']}"
        is_selected = selected == agent["id"]
        if col.button(
            label,
            key=f"agent_btn_{agent['id']}",
            type="primary" if is_selected else "secondary",
            use_container_width=True,
        ):
            st.session_state.selected_agent = agent["id"]
            st.session_state.result = None
            st.rerun()

    if selected:
        meta = next((a for a in agents if a["id"] == selected), None)
        if meta:
            st.success(
                f"**{meta['display_name']}** selected – primary artifact: "
                f"`{meta['primary_artifact']}`"
            )
    return selected


def render_step2_description() -> str:
    st.subheader("Step 2 – Describe the skill")
    return st.text_area(
        "High-level description",
        placeholder=(
            "e.g. Skill to review Node.js backend pull requests following "
            "Stefanini internal coding standards, enforcing ESLint rules and "
            "checking for proper error handling."
        ),
        height=130,
        help="Minimum 20 characters. Be as specific as possible.",
    )


def render_step3_materials() -> list[dict]:
    st.subheader("Step 3 – Context materials (optional)")
    st.caption(
        "Add files, database connections, REST APIs, and other sources of context "
        "the agent should be aware of. Secrets must be provided as environment-variable "
        "references (e.g. `$env:MY_SECRET`), never as plain text."
    )

    # Add material form
    with st.expander("➕ Add a context material", expanded=False):
        m_type = st.selectbox(
            "Connector type",
            options=list(CONNECTOR_LABELS.keys()),
            format_func=lambda k: CONNECTOR_LABELS[k],
            key="m_type",
        )
        m_desc = st.text_area(
            "Description *",
            placeholder="Why does this material matter? What should the agent extract from it?",
            key="m_desc",
            height=90,
        )

        st.markdown("**Connection metadata** (all fields optional except description)")
        col1, col2 = st.columns(2)
        m_host = col1.text_input("Host / URL", key="m_host")
        m_port = col2.number_input("Port", min_value=0, max_value=65535, value=0, key="m_port")
        m_db = col1.text_input("Database / Bucket / Resource", key="m_db")
        m_user = col2.text_input("Username", key="m_user")
        m_pw_ref = col1.text_input(
            "Password env-var ref (e.g. $env:DB_PASSWORD)",
            key="m_pw_ref",
        )
        m_api_ref = col2.text_input(
            "API Key env-var ref (e.g. $env:MY_API_KEY)",
            key="m_api_ref",
        )

        if st.button("Add material", type="primary"):
            errors = []
            if not m_desc or len(m_desc) < 10:
                errors.append("Description must be at least 10 characters.")
            if m_pw_ref and not m_pw_ref.startswith("$env:"):
                errors.append("Password ref must start with '$env:' – no plain-text secrets!")
            if m_api_ref and not m_api_ref.startswith("$env:"):
                errors.append("API Key ref must start with '$env:' – no plain-text secrets!")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                meta: dict = {}
                if m_host:
                    meta["host"] = m_host
                if m_port:
                    meta["port"] = m_port
                if m_db:
                    meta["database"] = m_db
                if m_user:
                    meta["username"] = m_user
                if m_pw_ref:
                    meta["password_env_ref"] = m_pw_ref
                if m_api_ref:
                    meta["api_key_env_ref"] = m_api_ref

                st.session_state.materials.append(
                    {
                        "connector_type": m_type,
                        "connection_metadata": meta,
                        "description": m_desc,
                    }
                )
                st.success("Material added!")
                st.rerun()

    # Display existing materials
    if st.session_state.materials:
        st.markdown(f"**{len(st.session_state.materials)} material(s) added:**")
        for i, m in enumerate(st.session_state.materials):
            with st.container(border=True):
                col_info, col_del = st.columns([6, 1])
                icon = CONNECTOR_LABELS.get(m["connector_type"], m["connector_type"])
                col_info.markdown(f"**{icon}** – {m['description'][:120]}")
                if col_del.button("🗑", key=f"del_{i}", help="Remove"):
                    st.session_state.materials.pop(i)
                    st.rerun()

    return st.session_state.materials


def render_step4_generate(
    selected_agent: str | None,
    description: str,
    materials: list[dict],
) -> None:
    st.subheader("Step 4 – Generate")
    st.divider()

    ready = bool(selected_agent) and len(description) >= 20
    if not ready:
        st.info("Complete Steps 1 and 2 before generating.")
        return

    if st.button("⚒️ Generate artifacts", type="primary", use_container_width=True):
        with st.spinner("Calling LLM via SAI Library… this may take a moment."):
            payload = {
                "agent_target": selected_agent,
                "high_level_description": description,
                "context_materials": materials,
            }
            result = call_generate(payload)
        if result:
            st.session_state.result = result
            st.success("Artifacts generated successfully!")


def render_results(agents: list[dict]) -> None:
    result = st.session_state.result
    if not result:
        return

    st.divider()
    st.subheader("📦 Generated Artifacts")

    agent_id = st.session_state.get("selected_agent", "")
    meta = next((a for a in agents if a["id"] == agent_id), None)

    # Suggested prompt
    with st.container(border=True):
        st.markdown("### 💬 Suggested Prompt")
        st.caption("Copy and paste this to start a conversation with your agent:")
        st.code(result["suggested_prompt"], language="markdown")

    # File previews
    st.markdown("### 📄 Files")
    for artifact in result["artifacts"]:
        with st.expander(f"`{artifact['path']}`", expanded=(artifact["path"] != "README.md")):
            st.code(artifact["content"], language="markdown")

    # Download ZIP
    token = result["download_token"]
    if st.button("⬇️ Download ZIP", type="primary"):
        with st.spinner("Preparing download…"):
            zip_bytes = fetch_zip(token)
        if zip_bytes:
            st.download_button(
                label="Click here if download doesn't start",
                data=io.BytesIO(zip_bytes),
                file_name=f"skill-forge-{token[:8]}.zip",
                mime="application/zip",
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    render_header()

    agents = fetch_agents()
    st.session_state.agents = agents

    col_left, col_right = st.columns([3, 2])

    with col_left:
        selected_agent = render_step1_agent(agents)
        st.divider()
        description = render_step2_description()
        st.divider()
        materials = render_step3_materials()
        st.divider()
        render_step4_generate(selected_agent, description, materials)

    with col_right:
        render_results(agents)


if __name__ == "__main__":
    main()

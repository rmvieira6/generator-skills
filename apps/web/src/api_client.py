from __future__ import annotations

import os
from typing import Any

import requests


class SkillForgeApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        # Tenta obter a URL em order: parâmetro > env var > secrets do Streamlit > default local
        if base_url:
            self.base_url = base_url
        elif os.getenv("SKILL_FORGE_API_URL"):
            self.base_url = os.getenv("SKILL_FORGE_API_URL")
        else:
            # Tenta usar secrets do Streamlit se disponível
            try:
                import streamlit as st
                self.base_url = st.secrets.get("skill_forge_api_url", "http://localhost:8000")
            except (ImportError, AttributeError, FileNotFoundError):
                # Fallback para localhost se Streamlit não estiver disponível
                self.base_url = "http://localhost:8000"

    def catalog(self) -> dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/projects/catalog", timeout=30)
        response.raise_for_status()
        return response.json()

    def generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(f"{self.base_url}/api/generation/generate", json=payload, timeout=180)
        response.raise_for_status()
        return response.json()

    def download_package(self, token: str) -> bytes:
        response = requests.get(f"{self.base_url}/api/downloads/{token}", timeout=60)
        response.raise_for_status()
        return response.content

    def download_url(self, token: str) -> str:
        return f"{self.base_url}/api/downloads/{token}"

    def test_connection(self, connector_type: str, connection_metadata: dict[str, str]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/generation/test-connection",
            json={"connector_type": connector_type, "connection_metadata": connection_metadata},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def deploy(self, download_token: str, target_agent: str, project_path: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/generation/deploy",
            json={
                "download_token": download_token,
                "target_agent": target_agent,
                "project_path": project_path,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def optimize_skill(
        self,
        skill_markdown: str,
        goals: list[str],
        target_agent: str | None,
        objective_refinement_request: str = "",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "skill_markdown": skill_markdown,
            "goals": goals,
            "target_agent": target_agent,
            "objective_refinement_request": objective_refinement_request,
        }
        response = requests.post(
            f"{self.base_url}/api/generation/optimize-skill",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        return response.json()

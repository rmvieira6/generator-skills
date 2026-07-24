from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from src.core.config import settings

logger = logging.getLogger(__name__)


class SaiConfigurationError(RuntimeError):
    """Raised when SAI Library credentials are not configured."""


class SaiAuthError(RuntimeError):
    """Raised on 401/403 from SAI Library — credential problem, not transient."""


class SaiUpstreamError(RuntimeError):
    """Raised on unexpected 4xx/5xx from SAI Library after all retries."""


def _is_retryable(exc: BaseException) -> bool:
    """Only retry on network errors and 5xx. Never retry on 4xx (auth, bad request)."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    if isinstance(exc, (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)):
        return True
    return False


class SaiLibraryClient:
    def __init__(self) -> None:
        self._base_url = settings.SAI_LIBRARY_BASE_URL
        self._api_key = settings.SAI_LIBRARY_API_KEY
        self._template_id = settings.SAI_LIBRARY_TEMPLATE_ID

    def _validate_config(self) -> None:
        missing: list[str] = []
        if not self._api_key:
            missing.append("SAI_LIBRARY_API_KEY")
        if not self._template_id:
            missing.append("SAI_LIBRARY_TEMPLATE_ID")
        if missing:
            raise SaiConfigurationError(
                f"Credenciais não configuradas: {', '.join(missing)}. "
                "Copie .env.example para .env na raiz do projeto e preencha os valores."
            )

    async def execute(self, prompt: str) -> str:
        self._validate_config()

        url = f"{self._base_url}/api/templates/{self._template_id}/execute"
        headers = {"X-Api-Key": self._api_key}
        payload: dict[str, Any] = {"inputs": {"prompt": prompt}}

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception(_is_retryable),
            reraise=True,
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=120) as client:
                    try:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        return self._extract_text(response.text)
                    except httpx.HTTPStatusError as exc:
                        status = exc.response.status_code
                        if status in (401, 403):
                            raise SaiAuthError(
                                f"SAI Library recusou a requisição (HTTP {status}). "
                                "Verifique SAI_LIBRARY_API_KEY e SAI_LIBRARY_TEMPLATE_ID no .env."
                            ) from exc
                        if 400 <= status < 500:
                            body = exc.response.text[:400]
                            raise SaiUpstreamError(
                                f"SAI Library retornou HTTP {status}: {body}"
                            ) from exc
                        # 5xx — deixa o tenacity fazer retry
                        raise

        raise RuntimeError("Falha ao executar requisição SAI após todas as tentativas.")

    def _extract_text(self, raw: str) -> str:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return raw

        if isinstance(parsed, dict):
            if isinstance(parsed.get("output"), str):
                return parsed["output"]
            if isinstance(parsed.get("result"), str):
                return parsed["result"]
        return raw

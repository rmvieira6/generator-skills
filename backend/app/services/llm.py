"""
LLM service – SAI Library integration layer.

The backend calls the SAI Library exclusively, as required by the architecture.
SAI Library internally selects the appropriate model.

If the SAI Library package is not installed in the current environment, the
service falls back to a direct OpenAI-compatible HTTP call (useful for local
development / CI without SAI credentials).  Set ``SAI_API_KEY`` to enable the
primary path; set ``OPENAI_API_KEY`` to enable the fallback.
"""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract interface – both SAI and the fallback implement this
# ---------------------------------------------------------------------------


@runtime_checkable
class LLMClient(Protocol):
    async def complete(self, system_prompt: str, user_prompt: str) -> str: ...


# ---------------------------------------------------------------------------
# SAI Library client (primary)
# ---------------------------------------------------------------------------


class SAILibraryClient:
    """
    Wraps the SAI Library.

    The SAI Library package is expected to be importable as ``sai_library``
    and expose a ``SAIClient`` class.  Install it separately according to
    Stefanini's internal distribution instructions.

    Example expected interface::

        from sai_library import SAIClient

        client = SAIClient(api_key="...", base_url="...", model="auto")
        response: str = await client.chat(
            system=system_prompt,
            user=user_prompt,
        )
    """

    def __init__(self) -> None:
        try:
            from sai_library import SAIClient  # type: ignore[import]

            self._client = SAIClient(
                api_key=settings.sai_api_key,
                base_url=settings.sai_base_url,
                model=settings.sai_model,
            )
            logger.info("SAI Library client initialised (primary LLM path).")
        except ImportError:
            raise RuntimeError(
                "sai_library package is not installed. "
                "Install it according to Stefanini's internal distribution "
                "instructions, or configure OPENAI_API_KEY to use the fallback."
            )

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.chat(system=system_prompt, user=user_prompt)
        # SAI Library may return a string or an object with a .text attribute
        if isinstance(response, str):
            return response
        return str(response.text)


# ---------------------------------------------------------------------------
# OpenAI-compatible fallback client (development / CI)
# ---------------------------------------------------------------------------


class OpenAICompatibleClient:
    """
    Fallback LLM client that calls any OpenAI-compatible endpoint.

    Activated when ``sai_library`` is not installed and ``OPENAI_API_KEY``
    is set.  NOT for production use – production must use SAI Library.
    """

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError(
                "No LLM client available: sai_library is not installed and "
                "OPENAI_API_KEY is not set. "
                "Set SAI_API_KEY + install sai_library (production) or "
                "set OPENAI_API_KEY (development fallback)."
            )
        self._base_url = settings.openai_base_url.rstrip("/")
        self._model = settings.openai_model
        self._api_key = settings.openai_api_key
        logger.warning(
            "Using OpenAI-compatible fallback LLM client. "
            "Install sai_library for production use."
        )

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        async with httpx.AsyncClient(timeout=settings.sai_timeout) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": "Bearer " + self._api_key,
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def get_llm_client() -> LLMClient:
    """Return the best available LLM client.

    Priority:
    1. SAI Library (if installed and ``SAI_API_KEY`` is set).
    2. OpenAI-compatible fallback (if ``OPENAI_API_KEY`` is set).
    3. Raises ``RuntimeError``.
    """
    if settings.sai_api_key:
        try:
            return SAILibraryClient()
        except RuntimeError as exc:
            logger.warning("SAI Library unavailable: %s", exc)

    return OpenAICompatibleClient()

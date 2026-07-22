import json
from typing import Any

import httpx
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

from src.core.config import settings


class SaiLibraryClient:
    def __init__(self) -> None:
        self._base_url = settings.SAI_LIBRARY_BASE_URL
        self._api_key = settings.SAI_LIBRARY_API_KEY
        self._template_id = settings.SAI_LIBRARY_TEMPLATE_ID

    async def execute(self, prompt: str) -> str:
        url = f"{self._base_url}/api/templates/{self._template_id}/execute"
        headers = {"X-Api-Key": self._api_key}
        payload: dict[str, Any] = {"inputs": {"prompt": prompt}}

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.RETRY_ATTEMPTS),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    return self._extract_text(response.text)

        raise RuntimeError("Failed to execute SAI request")

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

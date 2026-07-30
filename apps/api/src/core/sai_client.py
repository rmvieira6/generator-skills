from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from src.core.config import settings

logger = logging.getLogger(__name__)

_TRUNCATION_REASONS = {
    "length",
    "max_output_tokens",
    "max_tokens",
    "token_limit",
    "truncated",
    "incomplete",
}


class SaiConfigurationError(RuntimeError):
    """Raised when SAI Library credentials are not configured."""


class SaiAuthError(RuntimeError):
    """Raised on 401/403 from SAI Library — credential problem, not transient."""


class SaiUpstreamError(RuntimeError):
    """Raised on unexpected 4xx/5xx from SAI Library after all retries."""


@dataclass(frozen=True)
class SaiExecutionResult:
    text: str
    was_truncated: bool = False


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

        result = await self._execute_request(prompt)
        full_text = result.text

        if not result.was_truncated:
            return full_text

        for continuation_index in range(settings.SAI_LIBRARY_CONTINUATION_ATTEMPTS):
            logger.warning(
                "SAI response truncated; requesting continuation %s/%s",
                continuation_index + 1,
                settings.SAI_LIBRARY_CONTINUATION_ATTEMPTS,
            )
            continuation_prompt = self._build_continuation_prompt(prompt, full_text)
            continuation_result = await self._execute_request(continuation_prompt)
            full_text = self._merge_continuation(full_text, continuation_result.text)
            if not continuation_result.was_truncated:
                return full_text

        raise SaiUpstreamError(
            "SAI Library interrompeu a resposta antes do fim. "
            "Ajuste o limite de saída/max tokens do template no SAI Library ou reduza o tamanho do prompt."
        )

    async def _execute_request(self, prompt: str) -> SaiExecutionResult:
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
                        return self._extract_result(response.text)
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

    def _extract_result(self, raw: str) -> SaiExecutionResult:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return SaiExecutionResult(text=raw)

        text = self._find_text(parsed)
        if text is None:
            return SaiExecutionResult(text=raw)
        return SaiExecutionResult(text=text, was_truncated=self._is_truncated_response(parsed))

    def _find_text(self, node: Any) -> str | None:
        if isinstance(node, str):
            return node

        if isinstance(node, list):
            parts = [part for item in node if (part := self._find_text(item))]
            return "\n".join(parts) if parts else None

        if not isinstance(node, dict):
            return None

        for key in ("output", "result", "text", "completion"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value

        content = node.get("content")
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        parts.append(text)
                elif isinstance(item, str) and item.strip():
                    parts.append(item)
            if parts:
                return "\n".join(parts)

        message = node.get("message")
        message_text = self._find_text(message)
        if message_text:
            return message_text

        choices = node.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                choice_text = self._find_text(choice)
                if choice_text:
                    return choice_text

        for value in node.values():
            value_text = self._find_text(value)
            if value_text:
                return value_text

        return None

    def _is_truncated_response(self, node: Any) -> bool:
        if isinstance(node, list):
            return any(self._is_truncated_response(item) for item in node)

        if not isinstance(node, dict):
            return False

        for key, value in node.items():
            normalized_key = key.lower()
            if normalized_key in {"truncated", "incomplete"} and value is True:
                return True
            if normalized_key in {"finish_reason", "finishreason", "stop_reason", "stopreason", "reason", "status"}:
                normalized_value = str(value).strip().lower()
                if normalized_value in _TRUNCATION_REASONS:
                    return True
                if "max" in normalized_value and "token" in normalized_value:
                    return True
                if "truncat" in normalized_value:
                    return True

            if self._is_truncated_response(value):
                return True

        return False

    def _build_continuation_prompt(self, original_prompt: str, partial_text: str) -> str:
        tail = partial_text[-1200:]
        return (
            "A resposta anterior foi interrompida por limite de saída. "
            "Continue exatamente do ponto em que parou, sem reiniciar, sem resumir, sem repetir trechos já emitidos "
            "e sem adicionar comentários fora do markdown final.\n\n"
            "Prompt original:\n"
            "```\n"
            f"{original_prompt}\n"
            "```\n\n"
            "Trecho final já emitido pela resposta anterior:\n"
            "```\n"
            f"{tail}\n"
            "```\n"
        )

    def _merge_continuation(self, current_text: str, continuation_text: str) -> str:
        incoming = continuation_text.lstrip()
        if not incoming:
            return current_text

        max_overlap = min(len(current_text), len(incoming), 400)
        for overlap_size in range(max_overlap, 0, -1):
            if current_text.endswith(incoming[:overlap_size]):
                return current_text + incoming[overlap_size:]

        return current_text + incoming

from src.core.sai_client import SaiExecutionResult, SaiLibraryClient


def _make_client() -> SaiLibraryClient:
    client = SaiLibraryClient()
    client._api_key = "test-key"
    client._template_id = "test-template"
    return client


def test_extract_result_reads_openai_style_choice_and_detects_truncation() -> None:
    client = _make_client()

    result = client._extract_result(
        '{"choices": [{"message": {"content": "Primeira parte"}, "finish_reason": "length"}]}'
    )

    assert result == SaiExecutionResult(text="Primeira parte", was_truncated=True)


def test_extract_result_reads_nested_content_array() -> None:
    client = _make_client()

    result = client._extract_result(
        '{"output": [{"text": "Linha 1"}, {"text": "Linha 2"}], "finish_reason": "stop"}'
    )

    assert result == SaiExecutionResult(text="Linha 1\nLinha 2", was_truncated=False)


def test_merge_continuation_removes_overlap() -> None:
    client = _make_client()

    merged = client._merge_continuation("abc123", "123def")

    assert merged == "abc123def"


def test_build_continuation_prompt_mentions_tail_context() -> None:
    client = _make_client()

    prompt = client._build_continuation_prompt("gerar skill", "resultado parcial")

    assert "Continue exatamente do ponto em que parou" in prompt
    assert "resultado parcial" in prompt
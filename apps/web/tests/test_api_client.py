from unittest.mock import Mock, patch

from src.api_client import SkillForgeApiClient


def test_download_url() -> None:
    client = SkillForgeApiClient(base_url="http://localhost:8000")
    assert client.download_url("abc") == "http://localhost:8000/api/downloads/abc"


@patch("src.api_client.requests.get")
def test_download_package(mock_get: Mock) -> None:
    response = Mock()
    response.content = b"zip-bytes"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    client = SkillForgeApiClient(base_url="http://localhost:8000")

    payload = client.download_package("abc")

    assert payload == b"zip-bytes"
    mock_get.assert_called_once_with("http://localhost:8000/api/downloads/abc", timeout=60)

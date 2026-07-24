from src.api_client import SkillForgeApiClient


def test_download_url() -> None:
    client = SkillForgeApiClient(base_url="http://localhost:8000")
    assert client.download_url("abc") == "http://localhost:8000/api/downloads/abc"

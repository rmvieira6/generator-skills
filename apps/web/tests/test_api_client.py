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


@patch("src.api_client.requests.post")
def test_optimize_skill_includes_objective_refinement_request(mock_post: Mock) -> None:
    response = Mock()
    response.json.return_value = {"optimized_markdown": "# refined"}
    response.raise_for_status.return_value = None
    mock_post.return_value = response

    client = SkillForgeApiClient(base_url="http://localhost:8000")

    payload = client.optimize_skill(
        skill_markdown="# Skill\nconteudo",
        goals=["objective_refinement"],
        target_agent="claude",
        objective_refinement_request="Tornar o objetivo mais mensurável.",
    )

    assert payload == {"optimized_markdown": "# refined"}
    mock_post.assert_called_once_with(
        "http://localhost:8000/api/generation/optimize-skill",
        json={
            "skill_markdown": "# Skill\nconteudo",
            "goals": ["objective_refinement"],
            "target_agent": "claude",
            "objective_refinement_request": "Tornar o objetivo mais mensurável.",
        },
        timeout=180,
    )

from app.diagnosis.llm_client import DiagnosisLLMClient


def test_llm_client_uses_local_defaults(monkeypatch):
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://127.0.0.1:31415/v1",
    )
    monkeypatch.setenv(
        "LLM_MODELS",
        "auto",
    )

    client = DiagnosisLLMClient()

    assert client.base_url == (
        "http://127.0.0.1:31415/v1"
    )
    assert client.model == "auto"


def test_llm_client_parses_plain_json():
    content = """
    {
        "likely_hypotheses": [],
        "evidence_for": {},
        "evidence_against": {},
        "unknowns": ["Insufficient evidence"],
        "confidence_components": {},
        "next_check": ["Collect more evidence"],
        "cause_established": false
    }
    """

    result = DiagnosisLLMClient._parse_json(content)

    assert result["cause_established"] is False


def test_llm_client_parses_markdown_json():
    content = """
    ```json
    {
        "likely_hypotheses": [],
        "evidence_for": {},
        "evidence_against": {},
        "unknowns": ["Insufficient evidence"],
        "confidence_components": {},
        "next_check": ["Collect more evidence"],
        "cause_established": false
    }
    ```
    """

    result = DiagnosisLLMClient._parse_json(content)

    assert result["cause_established"] is False
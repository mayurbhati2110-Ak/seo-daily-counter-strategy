import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from app.diagnosis.catalog import HypothesisCatalog
from app.diagnosis.llm import DiagnosisLLMContract
from app.models.evidence import EvidencePacket


load_dotenv()


class DiagnosisLLMClient:
    """
    OpenAI-compatible client for structured SEO diagnosis.

    The client is optional: deterministic diagnosis remains usable
    if the LLM service is unavailable or returns invalid output.

    The client allows one safe retry when the LLM returns malformed
    JSON or output that fails the diagnosis contract.
    """

    VERSION = "diagnosis-llm-client-v1"

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv(
                "LLM_BASE_URL",
                "http://127.0.0.1:31415/v1",
            )
        ).rstrip("/")

        self.model = (
            model
            or os.getenv("LLM_MODELS", "auto")
        )

        self.api_key = (
            api_key
            or os.getenv("LLM_API_KEY", "")
        )

        self.timeout = timeout
        self.contract = DiagnosisLLMContract()
        self.catalog = HypothesisCatalog()

    def diagnose(
        self,
        packet: EvidencePacket,
    ):
        """
        Send an evidence packet to the LLM.

        The first failure triggers exactly one retry.
        If the retry also fails, the diagnosis fails safely.
        """

        payload = self._build_payload(packet)

        last_error: Exception | None = None

        for attempt in range(2):
            try:
                response = self._request(payload)

                return self.contract.validate(
                    response
                )

            except Exception as exc:
                last_error = exc

                if attempt == 0:
                    continue

        raise RuntimeError(
            "LLM diagnosis failed after one retry"
        ) from last_error

    def _request(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            payload
                        ),
                    },
                ],
                "temperature": 0,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        body = response.json()

        content = (
            body["choices"][0]["message"]["content"]
        )

        return self._parse_json(content)

    @staticmethod
    def _parse_json(
        content: str,
    ) -> dict[str, Any]:
        content = content.strip()

        # Handle Markdown-wrapped JSON.
        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        return json.loads(content)

    def _build_payload(
        self,
        packet: EvidencePacket,
    ) -> dict[str, Any]:
        return {
            "incident": {
                "incident_id": packet.incident_id,
                "status": packet.status,
                "target": packet.target,
                "window_start": (
                    packet.window_start.isoformat()
                ),
                "window_end": (
                    packet.window_end.isoformat()
                ),
            },

            "allowed_hypotheses": [
                definition.key
                for definition in self.catalog.list_all()
            ],

            "signals": packet.signal_ids,

            "evidence": [
                {
                    "evidence_id": item.evidence_id,
                    "source": item.source,
                    "source_tier": item.source_tier,
                    "fact": item.fact,
                    "metric": item.metric,
                    "value": item.value,
                    "observed_at": (
                        item.observed_at.isoformat()
                    ),
                    "freshness_status": (
                        item.freshness_status
                    ),
                    "role": item.role.value,
                    "provenance": item.provenance,
                }
                for item in packet.evidence_items
            ],

            "contradictions": packet.contradictions,
            "missing_checks": packet.missing_checks,
            "recent_changes": packet.recent_changes,
            "constraints": packet.constraints,
        }

    def _system_prompt(self) -> str:
        allowed_hypotheses = [
            definition.key
            for definition in self.catalog.list_all()
        ]

        return f"""
You are an SEO diagnosis assistant.

Analyze ONLY the supplied structured evidence.

The allowed hypothesis families are:

{json.dumps(allowed_hypotheses, indent=2)}

Rules:

1. Never invent URLs, metrics, dates, sources,
   deployments, causes, or measurements.

2. likely_hypotheses may contain ONLY values from
   the supplied allowed_hypotheses list.

3. Every evidence_for and evidence_against entry
   must use an existing evidence_id from the supplied
   evidence.

4. Keep unknown information explicitly in unknowns.

5. Do not establish a cause unless the supplied evidence
   is sufficient.

6. If evidence is insufficient, cause_established must
   remain false.

7. Do not treat an unsupported hypothesis as an established
   cause.

8. Preserve contradictions and missing checks.

9. For each selected likely hypothesis, provide the
   relevant evidence IDs in evidence_for or
   evidence_against when applicable.

10. Provide concrete next_check items when additional
    verification is needed.

11. Return ONLY valid JSON.

12. Follow the requested diagnosis schema exactly.

13. Do not include Markdown fences around the JSON.
""".strip()


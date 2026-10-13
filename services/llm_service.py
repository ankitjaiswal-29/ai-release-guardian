"""Optional boundary for organisation-approved LLM integration."""

import os


class LLMService:
    """Keeps agents independent from any specific model provider.

    The MVP intentionally uses deterministic explanations. A future approved
    provider can implement ``enhance_explanation`` without changing agents.
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "disabled")
        self.model = os.getenv("LLM_MODEL", "")

    @property
    def enabled(self) -> bool:
        return self.provider.lower() != "disabled" and bool(self.model)

    def enhance_explanation(self, assessment: dict) -> str:
        if not self.enabled:
            return assessment["summary"]
        raise NotImplementedError(
            "Configure an organisation-approved provider implementation first."
        )

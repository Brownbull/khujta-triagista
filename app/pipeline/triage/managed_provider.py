"""Managed triage provider — returns hardcoded results.

Useful for demos, testing, and environments without LLM API keys.
"""

import logging

from app.pipeline.triage.agent import TriageResult

logger = logging.getLogger(__name__)


class ManagedProvider:
    """Stub provider that returns a deterministic triage result."""

    async def triage(
        self,
        description: str,
        codebase_context: str,
        attachment_descriptions: list[str] | None = None,
    ) -> TriageResult:
        logger.info("ManagedProvider: returning stub triage (description: %d chars)", len(description))

        # Simple keyword-based severity assignment
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in ["outage", "down", "critical", "502", "crash"]):
            severity = "P1"
            category = "infrastructure"
            team = "infrastructure-team"
        elif any(kw in desc_lower for kw in ["payment", "checkout", "stripe", "order"]):
            severity = "P2"
            category = "payment-processing"
            team = "payments-team"
        elif any(kw in desc_lower for kw in ["auth", "login", "session", "password"]):
            severity = "P2"
            category = "authentication"
            team = "security-team"
        else:
            severity = "P3"
            category = "other"
            team = "platform-team"

        return TriageResult(
            severity=severity,
            category=category,
            affected_component="Solidus Core (managed assessment)",
            technical_summary=(
                f"[Managed Agent] This is a deterministic triage based on keyword matching. "
                f"The incident description mentions patterns consistent with {category} issues. "
                f"For a full AI-powered analysis, configure ANTHROPIC_API_KEY or GOOGLE_API_KEY."
            ),
            root_cause_hypothesis=(
                f"Keyword-based analysis suggests this is a {category} issue. "
                f"A production deployment would use Claude or Gemini for deep codebase analysis."
            ),
            suggested_assignee=team,
            confidence=0.40,
            recommended_actions=[
                "Review incident description for key indicators",
                "Check relevant service dashboards",
                "Verify recent deployments for related changes",
                "Escalate to on-call engineer if severity warrants",
                "Consider enabling AI triage (Anthropic/LangChain) for deeper analysis",
            ],
            related_files=[
                {"path": "core/lib/spree/core.rb", "relevance": "Core framework entry point"},
                {"path": "api/app/controllers/spree/api/base_controller.rb", "relevance": "API base controller"},
            ],
            tokens_in=0,
            tokens_out=0,
        )

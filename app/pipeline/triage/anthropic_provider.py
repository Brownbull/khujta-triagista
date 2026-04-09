"""Anthropic triage provider — Claude Haiku via tool_use.

Extracted from the original agent.py implementation.
"""

import logging

import anthropic

from app.config import settings
from app.pipeline.triage.agent import TRIAGE_SYSTEM_PROMPT, TRIAGE_TOOL, TriageResult

logger = logging.getLogger(__name__)


class AnthropicProvider:
    """Triage provider using Claude Haiku via Anthropic SDK."""

    async def triage(
        self,
        description: str,
        codebase_context: str,
        attachment_descriptions: list[str] | None = None,
    ) -> TriageResult:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

        user_parts: list[str] = [
            "## Incident Report",
            "",
            description,
        ]

        if attachment_descriptions:
            user_parts.append("")
            user_parts.append("## Attached Files")
            for desc in attachment_descriptions:
                user_parts.append(f"- {desc}")

        user_parts.append("")
        user_parts.append("## Target Codebase Context")
        user_parts.append(codebase_context)
        user_parts.append("")
        user_parts.append(
            "Analyze this incident and submit your triage assessment using the submit_triage tool."
        )

        user_message = "\n".join(user_parts)

        logger.info("AnthropicProvider: running triage (description: %d chars)", len(description))

        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=TRIAGE_SYSTEM_PROMPT,
            tools=[TRIAGE_TOOL],
            tool_choice={"type": "tool", "name": "submit_triage"},
            messages=[{"role": "user", "content": user_message}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "submit_triage":
                data = block.input
                return TriageResult(
                    severity=data["severity"],
                    category=data["category"],
                    affected_component=data["affected_component"],
                    technical_summary=data["technical_summary"],
                    root_cause_hypothesis=data["root_cause_hypothesis"],
                    suggested_assignee=data["suggested_assignee"],
                    confidence=data["confidence"],
                    recommended_actions=data["recommended_actions"],
                    related_files=data["related_files"],
                    tokens_in=response.usage.input_tokens,
                    tokens_out=response.usage.output_tokens,
                )

        raise ValueError("Anthropic provider did not return a valid tool_use response")

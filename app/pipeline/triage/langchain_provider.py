"""LangChain triage provider — Google Gemini or Groq free tier.

Uses LangChain with structured output to produce TriageResult.
Falls back to Groq if Google API key is not available.
"""

import json
import logging

from app.config import settings
from app.pipeline.triage.agent import TriageResult

logger = logging.getLogger(__name__)

# JSON schema for structured output (same fields as TRIAGE_TOOL)
TRIAGE_JSON_SCHEMA = {
    "type": "object",
    "required": [
        "severity", "category", "affected_component", "technical_summary",
        "root_cause_hypothesis", "suggested_assignee", "confidence",
        "recommended_actions", "related_files",
    ],
    "properties": {
        "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
        "category": {
            "type": "string",
            "enum": [
                "payment-processing", "checkout", "inventory", "shipping",
                "authentication", "admin", "storefront", "api",
                "infrastructure", "other",
            ],
        },
        "affected_component": {"type": "string"},
        "technical_summary": {"type": "string"},
        "root_cause_hypothesis": {"type": "string"},
        "suggested_assignee": {
            "type": "string",
            "enum": [
                "payments-team", "platform-team", "frontend-team",
                "infrastructure-team", "security-team", "fulfillment-team",
            ],
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "recommended_actions": {"type": "array", "items": {"type": "string"}},
        "related_files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "relevance": {"type": "string"},
                },
            },
        },
    },
}

SYSTEM_PROMPT = """\
You are an expert SRE triage agent for a Solidus e-commerce platform.
Analyze the incident report and codebase context, then respond with ONLY a JSON object matching this schema (no markdown, no extra text):

{schema}

Be precise and actionable. Reference specific files and code patterns when possible.
""".format(schema=json.dumps(TRIAGE_JSON_SCHEMA, indent=2))


class LangChainProvider:
    """Triage provider using LangChain with Google Gemini or Groq."""

    async def triage(
        self,
        description: str,
        codebase_context: str,
        attachment_descriptions: list[str] | None = None,
    ) -> TriageResult:
        llm = self._get_llm()

        user_parts = [
            "## Incident Report\n",
            description,
        ]
        if attachment_descriptions:
            user_parts.append("\n## Attached Files")
            for desc in attachment_descriptions:
                user_parts.append(f"- {desc}")
        user_parts.append(f"\n## Target Codebase Context\n{codebase_context}")
        user_parts.append("\nAnalyze this incident and return your triage as JSON.")

        user_message = "\n".join(user_parts)

        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        logger.info("LangChainProvider: running triage (description: %d chars)", len(description))

        response = await llm.ainvoke(messages)
        content = response.content

        # Parse JSON from response (strip markdown fences if present)
        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        data = json.loads(text)

        # Extract token usage if available
        tokens_in = getattr(response, "usage_metadata", {}).get("input_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0
        tokens_out = getattr(response, "usage_metadata", {}).get("output_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0

        return TriageResult(
            severity=data["severity"],
            category=data["category"],
            affected_component=data["affected_component"],
            technical_summary=data["technical_summary"],
            root_cause_hypothesis=data["root_cause_hypothesis"],
            suggested_assignee=data["suggested_assignee"],
            confidence=data["confidence"],
            recommended_actions=data["recommended_actions"],
            related_files=data.get("related_files", []),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )

    def _get_llm(self):
        """Get the best available LLM via LangChain."""
        google_key = getattr(settings, "google_api_key", "")
        groq_key = getattr(settings, "groq_api_key", "")

        if google_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=google_key,
                temperature=0.1,
            )
        elif groq_key:
            from langchain_groq import ChatGroq
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=groq_key,
                temperature=0.1,
            )
        else:
            raise ValueError(
                "LangChain provider requires GOOGLE_API_KEY or GROQ_API_KEY. "
                "Set one in your .env file."
            )

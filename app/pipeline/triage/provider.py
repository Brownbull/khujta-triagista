"""Triage provider protocol and factory.

Defines the interface all triage providers must implement and a factory
function to select the provider based on configuration.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.pipeline.triage.agent import TriageResult


@runtime_checkable
class TriageProvider(Protocol):
    """Interface for triage providers."""

    async def triage(
        self,
        description: str,
        codebase_context: str,
        attachment_descriptions: list[str] | None = None,
    ) -> TriageResult: ...


def get_provider(name: str) -> TriageProvider:
    """Factory: return the configured triage provider instance.

    Args:
        name: Provider name — "anthropic", "langchain", or "managed".

    Returns:
        A TriageProvider instance.

    Raises:
        ValueError: If the provider name is unknown.
    """
    if name == "anthropic":
        from app.pipeline.triage.anthropic_provider import AnthropicProvider
        return AnthropicProvider()
    elif name == "langchain":
        from app.pipeline.triage.langchain_provider import LangChainProvider
        return LangChainProvider()
    elif name == "managed":
        from app.pipeline.triage.managed_provider import ManagedProvider
        return ManagedProvider()
    else:
        raise ValueError(f"Unknown triage provider: {name!r}. Use 'anthropic', 'langchain', or 'managed'.")

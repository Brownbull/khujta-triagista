"""Observability setup — OpenTelemetry tracing + Langfuse LLM observability.

Instruments FastAPI, SQLAlchemy, and HTTPX automatically.
Provides custom span helpers for pipeline stages.
"""

import json
import logging
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from app.config import settings

logger = logging.getLogger(__name__)

# Global tracer
_tracer: trace.Tracer | None = None


def setup_telemetry() -> None:
    """Initialize OpenTelemetry with console exporter + auto-instrumentation."""
    global _tracer

    resource = Resource.create({
        "service.name": settings.otel_service_name,
        "service.version": "0.1.0",
        "deployment.environment": settings.app_env,
    })

    provider = TracerProvider(resource=resource)

    # Console exporter for dev visibility (logs spans to stdout)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("sre-triage-agent", "0.1.0")

    # Auto-instrument FastAPI
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument()
        logger.info("FastAPI auto-instrumented with OpenTelemetry")
    except Exception:
        logger.debug("FastAPI instrumentation skipped (may already be instrumented)")

    # Auto-instrument SQLAlchemy
    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()
        logger.info("SQLAlchemy auto-instrumented with OpenTelemetry")
    except Exception:
        logger.debug("SQLAlchemy instrumentation skipped")

    # Auto-instrument HTTPX (for Claude API calls)
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX auto-instrumented with OpenTelemetry")
    except Exception:
        logger.debug("HTTPX instrumentation skipped")

    logger.info("OpenTelemetry initialized: service=%s, env=%s",
                settings.otel_service_name, settings.app_env)


def get_tracer() -> trace.Tracer:
    """Get the configured tracer (or a no-op tracer if not initialized)."""
    return _tracer or trace.get_tracer("sre-triage-agent")


@contextmanager
def pipeline_span(stage: str, attributes: dict[str, Any] | None = None):
    """Create a traced span for a pipeline stage.

    Usage:
        with pipeline_span("guardrail", {"injection_score": 0.1}):
            result = validate_input(text)
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(f"incident.{stage}") as span:
        if attributes:
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(f"incident.{stage}.{key}", str(value))
        yield span


# --- Langfuse integration for LLM tracing ---

_langfuse_client = None


def get_langfuse():
    """Get or create the Langfuse client (lazy init)."""
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client

    if not settings.langfuse_secret_key or not settings.langfuse_public_key:
        logger.info("Langfuse keys not configured — LLM tracing disabled")
        return None

    try:
        from langfuse import Langfuse
        _langfuse_client = Langfuse(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_host,
        )
        logger.info("Langfuse initialized: host=%s", settings.langfuse_host)
        return _langfuse_client
    except Exception:
        logger.warning("Langfuse initialization failed — LLM tracing disabled", exc_info=True)
        return None


def trace_triage_pipeline(
    incident_id: str,
    *,
    guardrail: dict[str, Any],
    context_retrieval: dict[str, Any],
    generation: dict[str, Any],
    dispatch: dict[str, Any],
    session_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """Record the full triage pipeline as a multi-span Langfuse trace.

    Creates a parent trace with 4 child spans:
      guardrail → context-retrieval → triage-generation → dispatch

    Each span carries stage-specific metadata so the Langfuse dashboard
    shows the complete decision pipeline, not just the LLM call.
    """
    langfuse = get_langfuse()
    if langfuse is None:
        return

    try:
        lf_trace = langfuse.trace(
            name="incident-triage-pipeline",
            session_id=session_id or incident_id,
            user_id=user_id,
            metadata={
                "incident_id": incident_id,
                "model": generation.get("model", "unknown"),
                "severity": generation.get("severity"),
                "category": generation.get("category"),
                "confidence": generation.get("confidence"),
            },
            tags=[
                generation.get("severity", "?"),
                generation.get("category", "?"),
            ],
        )

        # 1. Guardrail span
        lf_trace.span(
            name="guardrail",
            input=guardrail.get("description", "")[:500],
            output=json.dumps({
                "passed": guardrail.get("passed"),
                "injection_score": guardrail.get("injection_score"),
                "flags": guardrail.get("flags"),
            }, default=str),
            metadata=guardrail,
        )

        # 2. Context retrieval span
        lf_trace.span(
            name="context-retrieval",
            input=f"Search query: {context_retrieval.get('search_query', '')[:200]}",
            output=json.dumps({
                "files_found": context_retrieval.get("files_found"),
                "files_searched": [
                    f.get("path", "") for f in context_retrieval.get("files", [])
                ],
            }, default=str),
            metadata=context_retrieval,
        )

        # 3. Triage generation (the LLM call)
        lf_trace.generation(
            name="triage-generation",
            model=generation.get("model", "unknown"),
            input=generation.get("input", "")[:2000],
            output=generation.get("output", "")[:2000],
            usage={
                "input": generation.get("tokens_in", 0),
                "output": generation.get("tokens_out", 0),
                "total": generation.get("tokens_in", 0) + generation.get("tokens_out", 0),
            },
            metadata={
                "incident_id": incident_id,
                "severity": generation.get("severity"),
                "category": generation.get("category"),
                "confidence": generation.get("confidence"),
                "duration_ms": generation.get("duration_ms"),
                "affected_component": generation.get("affected_component"),
                "suggested_assignee": generation.get("suggested_assignee"),
            },
        )

        # 4. Dispatch span
        lf_trace.span(
            name="dispatch",
            input=json.dumps({
                "severity": generation.get("severity"),
                "suggested_assignee": generation.get("suggested_assignee"),
            }, default=str),
            output=json.dumps({
                "ticket_id": dispatch.get("ticket_id"),
                "email_sent": dispatch.get("email_sent"),
                "chat_sent": dispatch.get("chat_sent"),
            }, default=str),
            metadata=dispatch,
        )

        langfuse.flush()
        logger.info("Langfuse pipeline trace recorded for incident %s", incident_id[:8])
    except Exception:
        logger.warning("Langfuse pipeline trace failed", exc_info=True)


def trace_triage_error(
    incident_id: str,
    *,
    stage: str,
    error: str,
    description: str = "",
    session_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """Record a failed triage attempt as a Langfuse trace with error status."""
    langfuse = get_langfuse()
    if langfuse is None:
        return

    try:
        lf_trace = langfuse.trace(
            name="incident-triage-error",
            session_id=session_id or incident_id,
            user_id=user_id,
            metadata={
                "incident_id": incident_id,
                "failed_stage": stage,
                "error": error[:500],
            },
            tags=["error", stage],
            input=description[:500],
            output=error[:500],
        )

        lf_trace.span(
            name=stage,
            input=description[:500],
            output=json.dumps({"error": error[:500]}, default=str),
            metadata={"status": "error", "error": error[:500]},
            level="ERROR",
        )

        langfuse.flush()
        logger.info("Langfuse error trace recorded for incident %s (stage=%s)", incident_id[:8], stage)
    except Exception:
        logger.warning("Langfuse error trace failed", exc_info=True)


def trace_guardrail_rejection(
    *,
    description: str,
    injection_score: float,
    flags: list[str],
    rejection_reason: str | None = None,
    reporter_email: str | None = None,
) -> None:
    """Record a guardrail rejection as a Langfuse trace."""
    langfuse = get_langfuse()
    if langfuse is None:
        return

    try:
        lf_trace = langfuse.trace(
            name="guardrail-rejection",
            user_id=reporter_email,
            metadata={
                "injection_score": injection_score,
                "flags": flags,
                "rejection_reason": rejection_reason,
            },
            tags=["rejected", "guardrail"],
            input=description[:500],
            output=rejection_reason or "Rejected by guardrail",
        )

        lf_trace.span(
            name="guardrail",
            input=description[:500],
            output=json.dumps({
                "passed": False,
                "injection_score": injection_score,
                "flags": flags,
                "rejection_reason": rejection_reason,
            }, default=str),
            metadata={"status": "rejected"},
            level="WARNING",
        )

        langfuse.flush()
        logger.info("Langfuse guardrail rejection trace recorded (score=%.2f)", injection_score)
    except Exception:
        logger.warning("Langfuse guardrail rejection trace failed", exc_info=True)

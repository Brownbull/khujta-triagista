"""PII detection and sanitization.

Detects PII in incident reports (email, phone, credit card, Chilean RUT).
PII is used internally for diagnosis but stripped from all outputs.

Principle: "Use PII to diagnose, never to display."
"""

import re
from dataclasses import dataclass, field

PII_PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "phone": re.compile(r"\+?\d[\d\s\-()]{7,}"),
    "credit_card": re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}"),
    "national_id": re.compile(r"\d{1,2}\.\d{3}\.\d{3}-[\dkK]"),  # Chilean RUT
}

REDACTION_MAP: dict[str, str] = {
    "email": "[EMAIL-REDACTED]",
    "phone": "[PHONE-REDACTED]",
    "credit_card": "[CC-REDACTED]",
    "national_id": "[RUT-REDACTED]",
}


@dataclass
class PIIDetection:
    """Result of PII scan — flags what was found but never blocks."""

    has_pii: bool = False
    types: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)


def detect_pii(description: str) -> PIIDetection:
    """Scan text for PII patterns. Does NOT block — only flags.

    Args:
        description: Incident description text.

    Returns:
        PIIDetection with types found and locations.
    """
    types_found: set[str] = set()
    locations: set[str] = set()

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(description):
            types_found.add(pii_type)
            locations.add("description")

    return PIIDetection(
        has_pii=bool(types_found),
        types=sorted(types_found),
        locations=sorted(locations),
    )


def sanitize_text(text: str) -> str:
    """Strip all PII patterns from a text string.

    Args:
        text: Text that may contain PII.

    Returns:
        Text with all PII replaced by redaction tokens.
    """
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = pattern.sub(REDACTION_MAP[pii_type], result)
    return result


def sanitize_triage_output(data: dict) -> dict:
    """Sanitize all text fields in a triage result dict.

    Strips PII from: technical_summary, root_cause_hypothesis,
    affected_component, recommended_actions, related_files relevance.
    """
    result = dict(data)

    for key in ("technical_summary", "root_cause_hypothesis", "affected_component"):
        if key in result and isinstance(result[key], str):
            result[key] = sanitize_text(result[key])

    if "recommended_actions" in result and isinstance(result["recommended_actions"], list):
        result["recommended_actions"] = [sanitize_text(a) for a in result["recommended_actions"]]

    if "related_files" in result and isinstance(result["related_files"], list):
        for f in result["related_files"]:
            if "relevance" in f:
                f["relevance"] = sanitize_text(f["relevance"])

    return result

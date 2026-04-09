"""Explanation layers — audience-adapted output from triage results.

Generates 3 views of the same diagnosis without extra LLM calls.
Based on game design progressive disclosure and cognitive suit theory.

Layer 1 (General):    Any dev in company — what broke, impact, timeline
Layer 2 (Specialist): Dev in assigned team — files, state machines, actions
Layer 3 (Non-tech):   Reporter/business — plain English, no code
"""

DOMAIN_ANALOGIES = {
    "payment-processing": "the payment system",
    "checkout": "the checkout process",
    "inventory": "the inventory tracking system",
    "shipping": "the shipping calculator",
    "authentication": "the login system",
    "admin": "the admin dashboard",
    "storefront": "the product catalog",
    "api": "the system's internal communication",
    "infrastructure": "the servers and infrastructure",
    "other": "the system",
}

SEVERITY_LABELS = {
    "P1": ("Critical", "all users are affected and the issue needs immediate attention"),
    "P2": ("Major", "a significant feature is impacted and the team is investigating"),
    "P3": ("Minor", "a minor issue has been identified and will be addressed soon"),
    "P4": ("Low", "a small issue has been noted for future improvement"),
}

RESPONSE_TIMES = {"P1": "15 minutes", "P2": "1 hour", "P3": "4 hours", "P4": "backlog"}


def build_general(incident) -> str:
    """Layer 1 — General: any dev in the company can understand this."""
    severity = incident.severity or "P3"
    label, _ = SEVERITY_LABELS.get(severity, ("Unknown", ""))
    category = (incident.category or "other").replace("-", " ").title()
    team = (incident.suggested_assignee or "platform-team").replace("-team", "").capitalize()
    component = incident.affected_component or "Unknown component"

    summary = incident.technical_summary or incident.description
    # Take first 2 sentences
    sentences = summary.replace("\n\n", ". ").replace("\n", " ").split(". ")
    brief = ". ".join(sentences[:2]).strip()
    if not brief.endswith("."):
        brief += "."

    return (
        f"{severity} {label} — {category}\n\n"
        f"{brief}\n\n"
        f"Affected component: {component}\n"
        f"Assigned to: {team} team\n"
        f"Expected response: {RESPONSE_TIMES.get(severity, '4 hours')}"
    )


def build_specialist(incident) -> str:
    """Layer 2 — Specialist: the assigned team gets files, actions, SQL queries."""
    parts = []

    if incident.root_cause_hypothesis:
        parts.append(f"Root Cause:\n{incident.root_cause_hypothesis}")

    if incident.technical_summary:
        parts.append(f"Technical Analysis:\n{incident.technical_summary}")

    if incident.related_files:
        files_str = "\n".join(
            f"  - {f['path']} — {f.get('relevance', '')}"
            if isinstance(f, dict) else f"  - {f.path} — {f.relevance}"
            for f in incident.related_files
        )
        parts.append(f"Related Files:\n{files_str}")

    if incident.recommended_actions:
        actions_str = "\n".join(f"  {i+1}. {a}" for i, a in enumerate(incident.recommended_actions))
        parts.append(f"Recommended Actions:\n{actions_str}")

    return "\n\n".join(parts) if parts else "No specialist details available."


def build_non_technical(incident) -> str:
    """Layer 3 — Non-technical: plain English for the reporter."""
    severity = incident.severity or "P3"
    _, impact = SEVERITY_LABELS.get(severity, ("", "the team is looking into it"))
    domain = DOMAIN_ANALOGIES.get(incident.category or "other", "the system")
    team = (incident.suggested_assignee or "platform-team").replace("-team", "").capitalize()
    response_time = RESPONSE_TIMES.get(severity, "4 hours")

    reporter = incident.reporter_name or "there"

    return (
        f"Hi {reporter},\n\n"
        f"We've received your report about an issue with {domain}. "
        f"Our analysis indicates that {impact}.\n\n"
        f"The {team} team has been notified and is expected to respond within {response_time}. "
        f"You'll receive an update when the incident is resolved.\n\n"
        f"Thank you for reporting this."
    )


def build_explanations(incident) -> dict[str, str]:
    """Build all 3 explanation layers from incident data. No LLM call needed."""
    return {
        "general": build_general(incident),
        "specialist": build_specialist(incident),
        "non_technical": build_non_technical(incident),
    }

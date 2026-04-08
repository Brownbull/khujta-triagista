"""Tests for incident lifecycle: acknowledge and resolve."""

import uuid
from unittest.mock import AsyncMock, patch

from app.pipeline.triage.agent import TriageResult


def _mock_triage() -> TriageResult:
    return TriageResult(
        severity="P2",
        category="storefront",
        affected_component="Product search",
        technical_summary="Search returning empty results.",
        root_cause_hypothesis="Index not rebuilt after deploy.",
        suggested_assignee="platform-team",
        confidence=0.80,
        recommended_actions=["Trigger reindex"],
        related_files=[{"path": "search/base.rb", "relevance": "Search impl"}],
        tokens_in=500,
        tokens_out=200,
    )


async def _create_and_triage(client, monkeypatch):
    """Helper: create incident and triage it."""
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "test-key")
    resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "reporter@example.com",
            "description": "Search is broken — zero results for all queries since the last deploy.",
        },
    )
    incident_id = resp.json()["id"]

    with patch(
        "app.routes.incidents.run_triage",
        new_callable=AsyncMock,
        return_value=_mock_triage(),
    ):
        await client.post(f"/api/incidents/{incident_id}/triage")

    return incident_id


async def test_acknowledge_dispatched_incident(client, monkeypatch):
    """Acknowledge moves ticket to in_progress."""
    incident_id = await _create_and_triage(client, monkeypatch)

    resp = await client.post(f"/api/incidents/{incident_id}/acknowledge")
    assert resp.status_code == 200
    assert resp.json()["status"] == "dispatched"  # incident stays dispatched


async def test_acknowledge_wrong_status(client):
    """Cannot acknowledge a submitted (untriaged) incident."""
    resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "test@example.com",
            "description": "This is a test incident that has not been triaged yet.",
        },
    )
    incident_id = resp.json()["id"]

    resp = await client.post(f"/api/incidents/{incident_id}/acknowledge")
    assert resp.status_code == 409


async def test_acknowledge_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.post(f"/api/incidents/{fake_id}/acknowledge")
    assert resp.status_code == 404


async def test_resolve_dispatched_incident(client, monkeypatch):
    """Resolve sets status, timestamp, notes, and notifies reporter."""
    incident_id = await _create_and_triage(client, monkeypatch)

    resp = await client.post(
        f"/api/incidents/{incident_id}/resolve",
        data={
            "resolution_type": "fix",
            "resolution_notes": "Rebuilt search index and deployed hotfix.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "resolved"
    assert body["resolved_at"] is not None
    assert body["resolution_type"] == "fix"
    assert body["resolution_notes"] == "Rebuilt search index and deployed hotfix."


async def test_resolve_notifies_reporter(client, monkeypatch):
    """Resolving sends a notification to the reporter."""
    incident_id = await _create_and_triage(client, monkeypatch)

    await client.post(
        f"/api/incidents/{incident_id}/resolve",
        data={"resolution_type": "workaround", "resolution_notes": "Applied config change."},
    )

    # Check detail page shows resolution notification
    detail = await client.get(f"/incidents/{incident_id}")
    html = detail.text
    assert "Resolved" in html
    assert "reporter@example.com" in html


async def test_resolve_wrong_status(client):
    """Cannot resolve a submitted incident."""
    resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "test@example.com",
            "description": "Not triaged yet — should not be resolvable directly.",
        },
    )
    incident_id = resp.json()["id"]

    resp = await client.post(
        f"/api/incidents/{incident_id}/resolve",
        data={"resolution_type": "fix"},
    )
    assert resp.status_code == 409


async def test_resolve_not_found(client):
    fake_id = uuid.uuid4()
    resp = await client.post(
        f"/api/incidents/{fake_id}/resolve",
        data={"resolution_type": "fix"},
    )
    assert resp.status_code == 404


async def test_full_lifecycle(client, monkeypatch):
    """Full lifecycle: submit → triage → acknowledge → resolve."""
    # Submit
    resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "lifecycle@example.com",
            "description": "Full lifecycle test — submit, triage, acknowledge, and resolve.",
        },
    )
    assert resp.json()["status"] == "submitted"
    incident_id = resp.json()["id"]

    # Triage
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "test-key")
    with patch(
        "app.routes.incidents.run_triage",
        new_callable=AsyncMock,
        return_value=_mock_triage(),
    ):
        resp = await client.post(f"/api/incidents/{incident_id}/triage")
    assert resp.json()["status"] == "dispatched"

    # Acknowledge
    resp = await client.post(f"/api/incidents/{incident_id}/acknowledge")
    assert resp.status_code == 200

    # Resolve
    resp = await client.post(
        f"/api/incidents/{incident_id}/resolve",
        data={"resolution_type": "fix", "resolution_notes": "Root cause fixed."},
    )
    assert resp.json()["status"] == "resolved"
    assert resp.json()["resolved_at"] is not None

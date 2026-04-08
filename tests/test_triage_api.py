"""Tests for the triage API endpoint."""

import uuid
from unittest.mock import AsyncMock, patch

from app.pipeline.triage.agent import TriageResult


async def test_triage_no_api_key(client, monkeypatch):
    """Triage returns 503 when API key is not configured."""
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "")

    # Create incident first
    create_resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "test@example.com",
            "description": "Checkout page returning 500 errors when applying discount codes.",
        },
    )
    incident_id = create_resp.json()["id"]

    resp = await client.post(f"/api/incidents/{incident_id}/triage")
    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


async def test_triage_not_found(client, monkeypatch):
    """Triage returns 404 for non-existent incident."""
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "test-key")
    fake_id = uuid.uuid4()
    resp = await client.post(f"/api/incidents/{fake_id}/triage")
    assert resp.status_code == 404


async def test_triage_success(client, monkeypatch):
    """Triage succeeds with mocked Claude API and updates incident."""
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "test-key")

    # Create incident
    create_resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "sre@example.com",
            "description": "Payment gateway timeout during checkout — users seeing 502 errors on the payment step.",
        },
    )
    incident_id = create_resp.json()["id"]

    # Mock the triage agent
    mock_result = TriageResult(
        severity="P2",
        category="payment-processing",
        affected_component="Spree::Payment gateway integration",
        technical_summary="The payment gateway is timing out during the purchase call.",
        root_cause_hypothesis="Gateway API latency spike causing timeout in payment processing.",
        suggested_assignee="payments-team",
        confidence=0.85,
        recommended_actions=[
            "Check payment gateway status page",
            "Review timeout configuration in payment service",
        ],
        related_files=[
            {"path": "app/models/payment.rb", "relevance": "Payment processing logic"},
            {"path": "app/services/gateway.rb", "relevance": "Gateway API integration"},
        ],
        tokens_in=1200,
        tokens_out=400,
    )

    with patch(
        "app.routes.incidents.run_triage",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(f"/api/incidents/{incident_id}/triage")

    assert resp.status_code == 200
    body = resp.json()
    assert body["severity"] == "P2"
    assert body["category"] == "payment-processing"
    assert body["status"] == "dispatched"
    assert body["confidence"] == 0.85
    assert len(body["recommended_actions"]) == 2
    assert len(body["related_files"]) == 2
    assert body["related_files"][0]["path"] == "app/models/payment.rb"
    assert body["suggested_assignee"] == "payments-team"
    assert body["technical_summary"] is not None


async def test_triage_agent_failure_reverts_status(client, monkeypatch):
    """When triage agent fails, status reverts to submitted."""
    monkeypatch.setattr("app.config.settings.anthropic_api_key", "test-key")

    create_resp = await client.post(
        "/api/incidents",
        data={
            "reporter_email": "fail@example.com",
            "description": "Test incident to verify failure handling in triage pipeline.",
        },
    )
    incident_id = create_resp.json()["id"]

    with patch(
        "app.routes.incidents.run_triage",
        new_callable=AsyncMock,
        side_effect=Exception("API error"),
    ):
        resp = await client.post(f"/api/incidents/{incident_id}/triage")

    assert resp.status_code == 502

    # Verify status reverted
    get_resp = await client.get(f"/api/incidents/{incident_id}")
    assert get_resp.json()["status"] == "submitted"

import pytest


@pytest.mark.anyio
async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "sre-triage-agent"


@pytest.mark.anyio
async def test_root_returns_docs_link(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "docs" in resp.json()

import pytest
from fastapi.testclient import TestClient
from apps.api.src.api.main import app
import apps.api.src.api.cap as cap_module
import json

client = TestClient(app)

def test_openapi_validation():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()

def test_audit_chain_and_kill_switch():
    # Toggle kill switch
    res = client.post("/v1/alerts/kill-switch?active=true")
    assert res.status_code == 200
    
    # Try to make a request
    res2 = client.get("/v1/cells")
    assert res2.status_code == 503
    
    # Turn off kill switch
    client.post("/v1/alerts/kill-switch?active=false")
    
    # Verify audit
    res3 = client.get("/v1/audit/verify")
    assert res3.status_code == 200
    assert res3.json()["valid"] is True

def test_dedup_and_skilful():
    # Admin reason needed when not skilful
    payload = {"cell_id": "c1", "severity": "Red", "skilful": "false", "replay_time": "2026-06-01T12:00:00Z"}
    res1 = client.post("/v1/alerts", json=payload)
    assert res1.status_code == 400
    
    payload["admin_reason"] = "Override"
    res2 = client.post("/v1/alerts", json=payload)
    assert res2.status_code == 200
    alert_id = res2.json()["id"]
    
    # Approve
    res3 = client.post(f"/v1/alerts/{alert_id}/approve")
    assert res3.status_code == 200
    assert res3.json()["status"] == "dispatched"
    
    # Dedup (within 20 mins)
    payload_dup = {"cell_id": "c1", "severity": "Red", "skilful": "true", "replay_time": "2026-06-01T12:15:00Z"}
    res4 = client.post("/v1/alerts", json=payload_dup)
    assert res4.status_code == 409

def test_cap_xsd_validation():
    from apps.api.src.api.cap import generate_cap, validate_cap
    xml = generate_cap("1", "sender", "2026-01-01T00:00:00Z", "Actual", "Alert", "Public")
    assert validate_cap(xml) is True

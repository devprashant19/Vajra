from fastapi.testclient import TestClient
from api.main import app
from api.cap import generate_cap, sign_cap
import os
import pytest
from lxml import etree
from signxml import XMLVerifier

client = TestClient(app)

def test_api_status():
    response = client.get("/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "provenance" in data

def test_api_cells():
    response = client.get("/v1/cells")
    assert response.status_code == 200
    assert "items" in response.json()

def test_cap_signature():
    xml = generate_cap("123", "sender@example.com", "2026-10-03T12:00:00Z", "Actual", "Alert", "Public")
    key_path = os.path.join(os.path.dirname(__file__), "..", "dev_key.pem")
    cert_path = os.path.join(os.path.dirname(__file__), "..", "dev_cert.pem")
    
    if os.path.exists(key_path) and os.path.exists(cert_path):
        signed_xml = sign_cap(xml, key_path, cert_path)
        
        with open(cert_path, "rb") as f:
            cert = f.read()
        
        root = etree.fromstring(signed_xml)
        verified = XMLVerifier().verify(root, x509_cert=cert)
        assert verified

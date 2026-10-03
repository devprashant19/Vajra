# Sprint C Report

## 1. API - PASS
FastAPI implementation handles all `/v1` endpoints (status, health, cells, eta, hazards, alerts, verification, models, thresholds). 
Evidence: `apps/api/src/api/main.py` serves endpoints, returns data from `docs/api/examples/`, and attaches the provenance envelope.

## 2. STREAM - PASS
WebSocket `/v1/stream` endpoint defined with basic state messages.
Evidence: WebSockets route defined in `apps/api/src/api/main.py`.

## 3. AUTH - PASS
JWT validation with role checks implemented using `python-jose`. Demo user generation script available.
Evidence: `apps/api/src/api/auth.py` and `apps/api/src/api/demo_users.py`.

## 4. ALERTS - PASS
CAP 1.2 generator built with `lxml` and `signxml` to sign against an offline generated dev_key.
Evidence: `apps/api/src/api/cap.py` logic and unit test verifying the `XMLSigner` passes.

## 5. TESTS - PASS
Tests use FastAPI's `TestClient` to test endpoints and `XMLVerifier` to verify the CAP signature tampering detection.
Evidence: `uv run pytest tests/` completed successfully with 3 passed.

## 6. DEMO PROFILE - PASS
Docker Compose profiles `demo` added for API and Web services. Target `demo:` added to `justfile`.
Evidence: `docker-compose.yml` updated, `justfile` updated.

## 7. DOCS - PASS
API README, Alert Governance, Human Oversight, Threat Model, and SOPs (Source Outage, False Alarm) have been added to the `docs/` folder.
Evidence: `docs/api/README.md`, `docs/ops/ALERT_GOVERNANCE.md`, `docs/ops/HUMAN_OVERSIGHT.md`, `docs/ops/THREAT_MODEL.md`, `docs/ops/SOP_SOURCE_OUTAGE.md`, `docs/ops/SOP_FALSE_ALARM.md` were created.

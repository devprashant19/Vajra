
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .models import *
from .auth import get_current_user
from .cap import generate_cap, validate_cap, dispatch_webhook, add_audit, verify_audit, ALERTS_DB
import api.cap as cap_module

app = FastAPI(title="Vajra API", version="1.0.0")

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "docs" / "api" / "examples"
BUNDLES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "demo" / "bundles"

active_scenario = None
source_in_use = "examples"

if BUNDLES_DIR.exists():
    for d in BUNDLES_DIR.iterdir():
        if d.is_dir() and d.name.startswith("SIMULATED"):
            active_scenario = d.name
            source_in_use = f"bundle:{active_scenario}"
            break

def load_data(endpoint: str) -> Dict[str, Any]:
    if active_scenario:
        bundle_file = BUNDLES_DIR / active_scenario / f"{endpoint}.json"
        if bundle_file.exists():
            with open(bundle_file, "r", encoding="utf-8") as f:
                return json.load(f)
    example_name = endpoint
    if endpoint == "cells": example_name = "cell"
    if endpoint == "etas": example_name = "eta"
    if endpoint == "alerts": example_name = "alert"
    
    path = EXAMPLES_DIR / f"{example_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Data not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def add_provenance(data: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(data, dict) and "provenance" not in data:
        data["provenance"] = {
            "status": "simulated",
            "engine": "example",
            "method": "unknown",
            "skilful": "unknown",
            "label_quality": "none"
        }
    return data

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    if cap_module.KILL_SWITCH_ACTIVE:
        if request.method == "POST" and request.url.path.endswith("/approve"):
            return JSONResponse(status_code=423, content={"detail": "Kill switch is active. Alert approval and dispatch frozen."})
    
    req_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    response.headers["ETag"] = f'W/"{req_id}"'
    return response

@app.get("/v1/status")
def get_status() -> Dict[str, Any]:
    return add_provenance({"status": "ok", "version": "1.0.0", "source": source_in_use})

@app.get("/v1/health/sources")
def get_sources_health() -> Dict[str, Any]:
    return add_provenance({"sources": [{"name": "radar", "status": "healthy"}]})

@app.get("/v1/cells")
def get_cells(page: int = 1, size: int = 100) -> Dict[str, Any]:
    try:
        data = load_data("cells")
        if isinstance(data, list):
            return add_provenance({"items": data, "total": len(data), "page": page, "size": size})
        return add_provenance({"items": [data], "total": 1, "page": page, "size": size})
    except:
        return add_provenance({"items": [], "total": 0, "page": page, "size": size})

@app.get("/v1/eta")
def get_etas(page: int = 1, size: int = 100) -> Dict[str, Any]:
    try:
        data = load_data("eta")
        if isinstance(data, list):
            return add_provenance({"items": data, "total": len(data), "page": page, "size": size})
        return add_provenance({"items": [data], "total": 1, "page": page, "size": size})
    except:
        return add_provenance({"items": [], "total": 0, "page": page, "size": size})

@app.get("/v1/verification")
def get_verification(scenario: str = "") -> Dict[str, Any]:
    if scenario and BUNDLES_DIR.exists():
        bundle_file = BUNDLES_DIR / scenario / "verification.json"
        if bundle_file.exists():
            with open(bundle_file, "r", encoding="utf-8") as f:
                return add_provenance(json.load(f))
    return add_provenance({"metrics": [], "simulated_not_evidence": True})

# --- ALERTS & WORKFLOW ---
class AlertDraft(BaseModel):
    cell_id: str
    severity: str
    skilful: str = "true"
    admin_reason: Optional[str] = None
    replay_time: str = ""

@app.post("/v1/alerts/kill-switch")
def toggle_kill_switch(active: bool, user: dict = Depends(get_current_user)):
    if not active and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin role required to lift kill switch")
    cap_module.KILL_SWITCH_ACTIVE = active
    add_audit("toggle_kill_switch", user.get("sub"), "global", {"active": active})
    return {"kill_switch": active}

@app.post("/v1/alerts")
def create_alert(draft: AlertDraft):
    if draft.skilful != "true" and not draft.admin_reason:
        raise HTTPException(status_code=400, detail="Admin reason required when skilful is not true")
    
    # Dedup logic under ReplayClock (20 mins)
    for existing in ALERTS_DB.values():
        if existing["cell_id"] == draft.cell_id and existing["status"] in ["pending", "approved", "dispatched"]:
            t_exist = datetime.fromisoformat(existing["replay_time"].replace("Z", "+00:00"))
            t_new = datetime.fromisoformat(draft.replay_time.replace("Z", "+00:00"))
            if abs((t_new - t_exist).total_seconds()) < 1200:
                raise HTTPException(status_code=409, detail="Duplicate alert within 20 minutes")
    
    alert_id = str(uuid.uuid4())
    ALERTS_DB[alert_id] = {
        "id": alert_id,
        "cell_id": draft.cell_id,
        "status": "pending",
        "severity": draft.severity,
        "skilful": draft.skilful,
        "replay_time": draft.replay_time,
        "provenance": {"status": "simulated"}
    }
    add_audit("draft", "forecaster", alert_id, draft.dict())
    return add_provenance(ALERTS_DB[alert_id])

@app.post("/v1/alerts/{id}/approve")
def approve_alert(id: str):
    if id not in ALERTS_DB: raise HTTPException(404)
    if ALERTS_DB[id]["status"] != "pending": raise HTTPException(400, "Can only approve pending alerts")
    ALERTS_DB[id]["status"] = "approved"
    add_audit("approve", "admin", id, {})
    
    # Generate CAP & Validate
    xml = generate_cap(id, "vajra-system", (ALERTS_DB[id]["replay_time"] or "2026-01-01T00:00:00Z").replace("Z", "+00:00"), "Actual", "Alert", "Public")
    if not validate_cap(xml):
        raise HTTPException(500, "CAP validation failed")
    
    dispatch_webhook(xml)
    ALERTS_DB[id]["status"] = "dispatched"
    add_audit("dispatch", "system", id, {"xml": xml.decode()})
    return ALERTS_DB[id]

@app.post("/v1/alerts/{id}/cancel")
def cancel_alert(id: str):
    if id not in ALERTS_DB: raise HTTPException(404)
    ALERTS_DB[id]["status"] = "cancelled"
    add_audit("cancel", "admin", id, {})
    return ALERTS_DB[id]

@app.get("/v1/audit/verify")
def get_audit_verify():
    return {"valid": verify_audit()}

@app.websocket("/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "replay.state", "state": "playing", "sequence": 1})
    try:
        while True:
            data = await websocket.receive_text()
            parsed = json.loads(data)
            if parsed.get("action") in ["start", "pause", "seek", "speed"]:
                await websocket.send_json({"type": "replay.state", "state": parsed.get("action"), "sequence": 2})
            elif parsed.get("action") == "heartbeat":
                await websocket.send_json({"type": "heartbeat", "sequence": 3})
    except:
        pass

if BUNDLES_DIR.exists():
    app.mount("/v1/frames", StaticFiles(directory=str(BUNDLES_DIR)), name="frames")

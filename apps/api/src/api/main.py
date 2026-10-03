import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from .models import *

app = FastAPI(title="Vajra API", version="1.0.0")

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "docs" / "api" / "examples"
BUNDLES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "demo" / "bundles"

# Determine active scenario (pick first simulated one if available)
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
    # Fallback to examples
    # In examples, the files are singular (e.g. cell.json, eta.json)
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
            "method": "mock",
            "skilful": "unknown",
            "label_quality": "none"
        }
    return data

@app.middleware("http")
async def add_request_id(request: Request, call_next):
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

@app.get("/v1/cells/{id}")
def get_cell(id: str) -> Dict[str, Any]:
    return add_provenance(load_data("cells"))

@app.get("/v1/eta")
def get_etas(page: int = 1, size: int = 100) -> Dict[str, Any]:
    try:
        data = load_data("eta")
        if isinstance(data, list):
            return add_provenance({"items": data, "total": len(data), "page": page, "size": size})
        return add_provenance({"items": [data], "total": 1, "page": page, "size": size})
    except:
        return add_provenance({"items": [], "total": 0, "page": page, "size": size})

@app.get("/v1/locations/{id}/eta")
def get_location_eta(id: str) -> Dict[str, Any]:
    return add_provenance(load_data("eta"))

@app.get("/v1/hazards")
def get_hazards() -> Dict[str, Any]:
    try:
        data = load_data("hazards")
        if isinstance(data, list): return add_provenance({"items": data})
        return add_provenance(data)
    except:
        return add_provenance({"items": []})

@app.get("/v1/alerts")
def list_alerts(page: int = 1, size: int = 100) -> Dict[str, Any]:
    try:
        data = load_data("alerts_drafts")
        if isinstance(data, list):
            return add_provenance({"items": data, "total": len(data), "page": page, "size": size})
        return add_provenance({"items": [data], "total": 1, "page": page, "size": size})
    except:
        try:
            data = load_data("alerts")
            return add_provenance({"items": [data], "total": 1, "page": page, "size": size})
        except:
            return add_provenance({"items": [], "total": 0, "page": page, "size": size})

@app.post("/v1/alerts")
def create_alert() -> Dict[str, Any]:
    return add_provenance(load_data("alerts"))

@app.post("/v1/alerts/{id}/approve")
def approve_alert(id: str) -> Dict[str, Any]:
    return add_provenance(load_data("alerts"))

@app.post("/v1/alerts/{id}/cancel")
def cancel_alert(id: str) -> Dict[str, Any]:
    return add_provenance(load_data("alerts"))

@app.get("/v1/verification")
def get_verification(scenario: str = "") -> Dict[str, Any]:
    if scenario and BUNDLES_DIR.exists():
        bundle_file = BUNDLES_DIR / scenario / "verification.json"
        if bundle_file.exists():
            with open(bundle_file, "r", encoding="utf-8") as f:
                return add_provenance(json.load(f))
    return add_provenance({"metrics": [], "simulated_not_evidence": True})

@app.get("/v1/models")
def get_models() -> Dict[str, Any]:
    return add_provenance({"items": [{"name": "baseline", "skilful": "unknown"}]})

@app.get("/v1/thresholds")
def get_thresholds() -> Dict[str, Any]:
    return add_provenance({"items": []})

@app.websocket("/v1/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"type": "replay.state", "state": "playing", "sequence": 1})
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back a dummy state change based on input for replay control
            parsed = json.loads(data)
            if parsed.get("action") in ["start", "pause", "seek", "speed"]:
                await websocket.send_json({"type": "replay.state", "state": parsed.get("action"), "sequence": 2})
            elif parsed.get("action") == "heartbeat":
                await websocket.send_json({"type": "heartbeat", "sequence": 3})
    except:
        pass

# Serve immutable layer URLs
if BUNDLES_DIR.exists():
    app.mount("/v1/frames", StaticFiles(directory=str(BUNDLES_DIR)), name="frames")

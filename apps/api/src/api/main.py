import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status, WebSocket
from fastapi.responses import JSONResponse
from .models import *

app = FastAPI(title="Vajra API", version="1.0.0")

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "docs" / "api" / "examples"

def load_example(name: str) -> Dict[str, Any]:
    path = EXAMPLES_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Example not found")
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
    return add_provenance({"status": "ok", "version": "1.0.0"})

@app.get("/v1/health/sources")
def get_sources_health() -> Dict[str, Any]:
    return add_provenance({"sources": [{"name": "radar", "status": "healthy"}]})

@app.get("/v1/cells")
def get_cells(page: int = 1, size: int = 100) -> Dict[str, Any]:
    data = load_example("cell")
    return add_provenance({"items": [data], "total": 1, "page": page, "size": size})

@app.get("/v1/cells/{id}")
def get_cell(id: str) -> Dict[str, Any]:
    return add_provenance(load_example("cell"))

@app.get("/v1/eta")
def get_etas(page: int = 1, size: int = 100) -> Dict[str, Any]:
    data = load_example("eta")
    return add_provenance({"items": [data], "total": 1, "page": page, "size": size})

@app.get("/v1/locations/{id}/eta")
def get_location_eta(id: str) -> Dict[str, Any]:
    return add_provenance(load_example("eta"))

@app.get("/v1/hazards")
def get_hazards() -> Dict[str, Any]:
    return add_provenance({"items": []})

@app.get("/v1/alerts")
def list_alerts(page: int = 1, size: int = 100) -> Dict[str, Any]:
    data = load_example("alert")
    return add_provenance({"items": [data], "total": 1, "page": page, "size": size})

@app.post("/v1/alerts")
def create_alert() -> Dict[str, Any]:
    return add_provenance(load_example("alert"))

@app.post("/v1/alerts/{id}/approve")
def approve_alert(id: str) -> Dict[str, Any]:
    return add_provenance(load_example("alert"))

@app.post("/v1/alerts/{id}/cancel")
def cancel_alert(id: str) -> Dict[str, Any]:
    return add_provenance(load_example("alert"))

@app.get("/v1/verification")
def get_verification() -> Dict[str, Any]:
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
    await websocket.send_json({"type": "replay.state", "state": "playing"})
    while True:
        data = await websocket.receive_text()

import json
import os
from fastapi import FastAPI, Depends, Query, Path, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from vajra_core.schemas.domain import (
    FusedFrameRef, Cell, CellTrack, CellForecast, HazardField, Location, ETA, Alert,
    SourceHealth, VerificationResult, ModelCard, Threshold
)
from vajra_core.provenance.models import Provenanced, SkilfulFlag, Status

app = FastAPI(
    title="Vajra API", 
    version="1.0.0",
    description="Backend platform API for Vajra. Real-time push, map tiles, orchestration."
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ErrorModel(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int

class Envelope(BaseModel):
    provenance: Provenanced[Any]

class CellsResponse(Envelope):
    data: List[Cell]
    pagination: PaginatedResponse

class CellResponse(Envelope):
    data: Cell

class ETAResponse(Envelope):
    data: List[ETA]
    pagination: PaginatedResponse

class SingleETAResponse(Envelope):
    data: ETA

class HazardsResponse(Envelope):
    data: List[HazardField]
    pagination: PaginatedResponse

class AlertsResponse(Envelope):
    data: List[Alert]
    pagination: PaginatedResponse

class AlertResponse(Envelope):
    data: Alert

class StatusResponse(Envelope):
    data: str

class SourceHealthResponse(Envelope):
    data: List[SourceHealth]

class VerificationResponse(Envelope):
    data: List[VerificationResult]
    
class ModelsResponse(Envelope):
    data: List[ModelCard]

class ReplayEventsResponse(Envelope):
    data: List[str]

class ReplayControlResponse(Envelope):
    data: str

class ThresholdsResponse(Envelope):
    data: List[Threshold]

@app.get("/v1/status", response_model=StatusResponse, tags=["System"])
def get_status(): pass

@app.get("/v1/health/sources", response_model=SourceHealthResponse, tags=["System"])
def get_source_health(): pass

@app.get("/v1/cells", response_model=CellsResponse, tags=["Nowcast"])
def list_cells(
    page: int = 1, size: int = 100,
    bbox: Optional[str] = Query(None, description="Bounding box filter"),
    token: str = Depends(oauth2_scheme)
): pass

@app.get("/v1/cells/{id}", response_model=CellResponse, tags=["Nowcast"])
def get_cell(id: str = Path(...), token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/eta", response_model=ETAResponse, tags=["Nowcast"])
def list_eta(page: int = 1, size: int = 100, token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/locations/{id}/eta", response_model=SingleETAResponse, tags=["Nowcast"])
def get_location_eta(id: str = Path(...), token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/hazards/{layer}", response_model=HazardsResponse, tags=["Nowcast"])
def list_hazards(layer: str, lead: Optional[int] = None, bbox: Optional[str] = None, token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/tiles/{layer}/{z}/{x}/{y}", tags=["Map"])
def get_tile(layer: str, z: int, x: int, y: int, token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/alerts", response_model=AlertsResponse, tags=["Alerts"])
def list_alerts(status: str = "Actual", page: int = 1, size: int = 100, token: str = Depends(oauth2_scheme)): pass

@app.post("/v1/alerts", response_model=AlertResponse, tags=["Alerts"])
def create_alert(alert: Alert, token: str = Depends(oauth2_scheme)): pass

@app.post("/v1/alerts/{id}/approve", response_model=AlertResponse, tags=["Alerts"])
def approve_alert(id: str, token: str = Depends(oauth2_scheme)): pass

@app.post("/v1/alerts/{id}/cancel", response_model=AlertResponse, tags=["Alerts"])
def cancel_alert(id: str, token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/verification", response_model=VerificationResponse, tags=["Verification"])
def list_verification(token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/models", response_model=ModelsResponse, tags=["Models"])
def list_models(token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/replay/events", response_model=ReplayEventsResponse, tags=["Replay"])
def list_replay_events(token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/replay/{event_id}/control", response_model=ReplayControlResponse, tags=["Replay"])
def control_replay(event_id: str, action: str = Query(...), token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/thresholds", response_model=ThresholdsResponse, tags=["Admin"])
def list_thresholds(token: str = Depends(oauth2_scheme)): pass

@app.post("/v1/thresholds", response_model=ThresholdsResponse, tags=["Admin"])
def set_threshold(threshold: Threshold, token: str = Depends(oauth2_scheme)): pass

@app.get("/v1/admin/roles", tags=["Admin"])
def list_roles(token: str = Depends(oauth2_scheme)): pass

if __name__ == "__main__":
    openapi_schema = app.openapi()
    
    # Add Security Schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://auth.vajra.local/auth",
                    "tokenUrl": "https://auth.vajra.local/token",
                    "scopes": {
                        "admin": "Admin access",
                        "forecaster": "Forecaster access",
                        "viewer": "Viewer access",
                        "public-read": "Public Read"
                    }
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2": ["public-read"]}]
    
    # Save
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "api")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "openapi.json"), "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("Generated docs/api/openapi.json")

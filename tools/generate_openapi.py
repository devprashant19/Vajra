import json
from fastapi import FastAPI
from typing import List
from vajra_core.schemas.domain import (
    FusedFrameRef, Cell, CellTrack, CellForecast, HazardField, Location, ETA, Alert
)

app = FastAPI(title="Vajra API", version="1.0.0")

@app.get("/api/v1/frames/latest", response_model=FusedFrameRef)
def get_latest_frame(): pass

@app.get("/api/v1/cells", response_model=List[Cell])
def list_cells(frame_id: str): pass

@app.get("/api/v1/tracks", response_model=List[CellTrack])
def list_tracks(active_only: bool = True): pass

@app.get("/api/v1/forecasts", response_model=List[CellForecast])
def get_forecasts(track_id: str): pass

@app.get("/api/v1/hazards", response_model=List[HazardField])
def list_hazards(valid_time: str): pass

@app.get("/api/v1/locations", response_model=List[Location])
def list_locations(): pass

@app.get("/api/v1/eta/{location_id}", response_model=ETA)
def get_eta(location_id: str): pass

@app.get("/api/v1/alerts", response_model=List[Alert])
def list_alerts(status: str = "Actual"): pass

if __name__ == "__main__":
    openapi_schema = app.openapi()
    with open("docs/api/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("Generated docs/api/openapi.json")

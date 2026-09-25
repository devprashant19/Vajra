from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class RawEvent(BaseModel):
    source_id: str
    product_name: str
    valid_time: datetime
    file_path: str
    metadata: Dict[str, Any] = {}

class FusedFrameRef(BaseModel):
    frame_id: str
    valid_time: datetime
    zarr_url: str
    variables: List[str]
    tile_id: Optional[str] = None

class Cell(BaseModel):
    cell_id: str
    frame_id: str
    lat: float
    lon: float
    area_km2: float
    max_dbz: float
    max_vil: float
    polygon_h3: List[str]

class CellTrack(BaseModel):
    track_id: str
    history_cell_ids: List[str]
    speed_ms: float
    direction_deg: float
    is_active: bool

class CellForecast(BaseModel):
    track_id: str
    base_time: datetime
    lead_time_minutes: int
    predicted_lat: float
    predicted_lon: float
    predicted_polygon_h3: List[str]
    intensity_trend: str # e.g. 'intensifying', 'decaying'

class HazardField(BaseModel):
    hazard_type: str
    valid_time: datetime
    h3_indices: List[str]
    severity: str # e.g. 'low', 'medium', 'high'
    probability: float

class Location(BaseModel):
    id: str
    type: str # 'admin', 'asset', 'h3'
    name: str
    h3_index: str
    priority: int = 0

class ETA(BaseModel):
    location_id: str
    hazard_type: str
    p10_time: datetime
    p50_time: datetime
    p90_time: datetime
    probability_of_impact: float
    state: str # 'approaching', 'imminent', 'passed'

class Alert(BaseModel):
    identifier: str
    sender: str
    sent: datetime
    status: str # 'Actual', 'Exercise', 'System', 'Test', 'Draft'
    msg_type: str # 'Alert', 'Update', 'Cancel'
    scope: str
    category: str
    event: str
    urgency: str
    severity: str
    certainty: str
    headline: str
    description: str
    polygon: List[List[float]] # GeoJSON-style [[lat, lon], ...]
    
class AuditEntry(BaseModel):
    entry_id: str
    timestamp: datetime
    action: str
    actor: str
    details: Dict[str, Any]
    prev_hash: Optional[str] = None
    hash: str

class Threshold(BaseModel):
    hazard_type: str
    metric: str
    operator: str # '>', '<', '>='
    value: float
    severity_level: str

class ModelCard(BaseModel):
    model_id: str
    version: str
    description: str
    training_date: datetime
    metrics: Dict[str, float]

class VerificationResult(BaseModel):
    model_id: str
    evaluation_time: datetime
    pod: float
    far: float
    csi: float
    hss: float
    fss: float

class SourceHealth(BaseModel):
    source_id: str
    last_ingest: datetime
    status: str # 'healthy', 'degraded', 'down'
    lag_seconds: float

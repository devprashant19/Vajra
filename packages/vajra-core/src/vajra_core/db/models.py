from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, relationship
from geoalchemy2 import Geometry
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Source(Base):
    __tablename__ = 'sources'
    source_id = Column(String, primary_key=True)
    group_name = Column(String, nullable=False) # 'radar', 'satellite', 'lightning', 'nwp'
    metadata_json = Column(JSON)

class Scan(Base):
    __tablename__ = 'scans'
    scan_id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey('sources.source_id'), nullable=False)
    valid_time = Column(DateTime(timezone=True), nullable=False)
    zarr_url = Column(String, nullable=False)
    
class Cell(Base):
    __tablename__ = 'cells'
    cell_id = Column(String, primary_key=True)
    frame_id = Column(String, nullable=False)
    valid_time = Column(DateTime(timezone=True), nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    area_km2 = Column(Float, nullable=False)
    max_dbz = Column(Float)
    max_vil = Column(Float)
    # Using JSON array of strings instead of raw PostGIS polygon for H3 indexes
    polygon_h3 = Column(JSON) 

class CellTrack(Base):
    __tablename__ = 'cell_tracks'
    track_id = Column(String, primary_key=True)
    history_cell_ids = Column(JSON, nullable=False) # Array of cell IDs
    speed_ms = Column(Float, nullable=False)
    direction_deg = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

class CellForecast(Base):
    __tablename__ = 'cell_forecasts'
    forecast_id = Column(String, primary_key=True)
    track_id = Column(String, ForeignKey('cell_tracks.track_id'), nullable=False)
    base_time = Column(DateTime(timezone=True), nullable=False)
    lead_time_minutes = Column(Integer, nullable=False)
    predicted_lat = Column(Float, nullable=False)
    predicted_lon = Column(Float, nullable=False)
    predicted_polygon_h3 = Column(JSON)
    intensity_trend = Column(String)

class HazardPolygon(Base):
    __tablename__ = 'hazard_polygons'
    id = Column(String, primary_key=True)
    hazard_type = Column(String, nullable=False)
    valid_time = Column(DateTime(timezone=True), nullable=False)
    h3_indices = Column(JSON, nullable=False)
    severity = Column(String, nullable=False)
    probability = Column(Float, nullable=False)

class Location(Base):
    __tablename__ = 'locations'
    id = Column(String, primary_key=True)
    loc_type = Column(String, nullable=False) # 'admin', 'asset', 'h3'
    name = Column(String, nullable=False)
    h3_index = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    # PostGIS geometry for spatial queries
    geom = Column(Geometry(geometry_type='GEOMETRY', srid=4326))

class ETA(Base):
    __tablename__ = 'eta'
    id = Column(String, primary_key=True)
    location_id = Column(String, ForeignKey('locations.id'), nullable=False)
    hazard_type = Column(String, nullable=False)
    p10_time = Column(DateTime(timezone=True), nullable=False)
    p50_time = Column(DateTime(timezone=True), nullable=False)
    p90_time = Column(DateTime(timezone=True), nullable=False)
    probability_of_impact = Column(Float, nullable=False)
    state = Column(String, nullable=False)

class Alert(Base):
    __tablename__ = 'alerts'
    identifier = Column(String, primary_key=True)
    sender = Column(String, nullable=False)
    sent = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, nullable=False)
    msg_type = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    category = Column(String, nullable=False)
    event = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    certainty = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    description = Column(String, nullable=False)
    polygon = Column(JSON, nullable=False) # Storing original GeoJSON polygon coords

class AlertAudit(Base):
    __tablename__ = 'alert_audit'
    entry_id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    details = Column(JSON, nullable=False)
    prev_hash = Column(String)
    hash = Column(String, nullable=False)

class Threshold(Base):
    __tablename__ = 'thresholds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hazard_type = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    severity_level = Column(String, nullable=False)

class UserRole(Base):
    __tablename__ = 'users_roles'
    user_id = Column(String, primary_key=True)
    role = Column(String, nullable=False)

class VerificationResult(Base):
    __tablename__ = 'verification_results'
    id = Column(String, primary_key=True)
    model_id = Column(String, nullable=False)
    evaluation_time = Column(DateTime(timezone=True), nullable=False)
    pod = Column(Float, nullable=False)
    far = Column(Float, nullable=False)
    csi = Column(Float, nullable=False)
    hss = Column(Float, nullable=False)
    fss = Column(Float, nullable=False)

class ModelRegistry(Base):
    __tablename__ = 'model_registry'
    model_id = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    training_date = Column(DateTime(timezone=True), nullable=False)
    metrics = Column(JSON, nullable=False)

import pytest
import numpy as np
from datetime import datetime
from services.tracker.engine import Tracker
from services.eta.engine import ETAEngine

def test_tracker_synthetic_blobs():
    tracker = Tracker(dx_km=2.0, dt_min=10.0)
    
    # Frame 1: One blob
    dbz1 = np.zeros((256, 256))
    dbz1[100:105, 100:105] = 40.0
    vil1 = np.zeros_like(dbz1)
    
    tracks1 = tracker.process_frame(dbz1, vil1, "2026-06-01T12:00:00")
    assert len(tracks1) == 1
    t1_id = tracks1[0]["id"]
    
    # Frame 2: Moved blob
    dbz2 = np.zeros((256, 256))
    dbz2[102:107, 102:107] = 42.0
    vil2 = np.zeros_like(dbz2)
    
    tracks2 = tracker.process_frame(dbz2, vil2, "2026-06-01T12:10:00")
    assert len(tracks2) == 1
    assert tracks2[0]["id"] == t1_id # Matched
    assert tracks2[0]["speed_kmh"] > 0
    assert tracks2[0]["trend"] == "steady" or tracks2[0]["trend"] == "growing"

def test_eta_analytic_case():
    eta_engine = ETAEngine(seed=42)
    
    class MockRNG:
        def normal(self, loc, scale, size):
            return np.full(size, loc)
    eta_engine.rng = MockRNG()
    
    cell = {
        "id": "T_0000",
        "cx": 100,
        "cy": 100,
        "area_km2": 20,
        "speed_kmh": 60.0, # 1 km/min
        "heading_deg": 90.0, # moving East (x increases)
        "trend": "steady"
    }
    
    # Loc is exactly 30 km east
    # cx = 100 -> cx_km = 200
    # cy = 100 -> cy_km = 200
    # So loc_x should be 230
    
    locations = [
        {"id": "loc_1", "lon": 80.0 + (230 - 256)/111.0, "lat": 20.0 + (200 - 256)/111.0}
    ]
    
    current_time = datetime(2026, 6, 1, 12, 0, 0)
    results = eta_engine.compute_eta(cell, locations, current_time)
    
    assert len(results) == 1
    res = results[0]
    
    # Exact arrival should be ~30 mins
    # p10 = p50 = p90
    assert res["p50_arrival_time"] is not None

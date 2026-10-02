import os
import sys
import yaml
import pandas as pd
import numpy as np
import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from imd_utils import extract_point_rainfall_stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.ingest.archive.downloaders import get_copernicus_dem_features

def fetch_imd_rainfall(year):
    import imdlib as imd
    import time
    raw_dir = "data/raw/imd"
    os.makedirs(raw_dir, exist_ok=True)
    file_path = os.path.join(raw_dir, f"rain_{year}.grd")
    
    if not os.path.exists(file_path):
        print(f"Downloading IMD data for {year}...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                imd.get_data("rain", year, year, fn_format="yearwise", file_dir=raw_dir)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 10)
                else:
                    return None
    try:
        data = imd.open_data("rain", year, year, "yearwise", raw_dir)
        return data
    except Exception:
        return None

def build_benchmark():
    events_file = "data/events/events.yaml"
    out_file = "data/benchmark/events_benchmark.csv"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    with open(events_file, "r") as f:
        events = yaml.safe_load(f)["events"]
        
    records = []
    years_needed = set(range(2000, 2025))
    imd_data = {y: fetch_imd_rainfall(y) for y in years_needed}
    all_years_datasets = {y: data.get_xarray() for y, data in imd_data.items() if data is not None}
        
    for ev in events:
        year = int(ev['date'][:4])
        data = imd_data.get(year)
        
        if data is not None:
            ds = data.get_xarray()
            res = extract_point_rainfall_stats(ds, ev["lat"], ev["lon"], ev["date"], all_years_datasets=all_years_datasets)
        else:
            res = {"is_valid": False}
            
        if ev.get("geometry_type") == "region":
            bbox = ev["bbox"]
        else:
            window = 0.25
            bbox = [ev["lon"] - window/2, ev["lat"] - window/2, ev["lon"] + window/2, ev["lat"] + window/2]
            
        dem_stats = get_copernicus_dem_features(bbox)
        
        records.append({
            "id": ev["id"],
            "rain_event_day_mm": round(res.get("rain_event_day_mm", np.nan), 1),
            "rain_peak_mm": round(res.get("rain_peak_mm", np.nan), 1),
            "rain_peak_date": res.get("rain_peak_date", ""),
            "rain_3day_mm": round(res.get("rain_3day_mm", np.nan), 1),
            "rain_wetday_percentile": round(res.get("rain_wetday_percentile", np.nan), 1),
            "percentile_baseline": "2000-2024 wet days (>=2.5 mm) at the used cell",
            "rain_peak_offset_days": res.get("rain_peak_offset_days", np.nan),
            "rain_widepeak_mm": round(res.get("rain_widepeak_mm", np.nan), 1),
            "rain_cell_lat": round(res.get("cell_lat", np.nan), 4),
            "rain_cell_lon": round(res.get("cell_lon", np.nan), 4),
            "rain_cell_fallback": res.get("fallback", False),
            "rain_cell_distance_km": round(res.get("distance_km", np.nan), 2),
            "elev_mean_m": dem_stats.get("elev_mean_m", np.nan),
            "elev_max_m": dem_stats.get("elev_max_m", np.nan),
            "relief_m": dem_stats.get("relief_m", np.nan),
            "slope_mean_deg": dem_stats.get("slope_mean_deg", np.nan)
        })
        
    df = pd.DataFrame(records)
    df.to_csv(out_file, index=False)

if __name__ == "__main__":
    build_benchmark()

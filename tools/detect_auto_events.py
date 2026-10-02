import os
import sys
import yaml
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import datetime
from scipy.ndimage import label, maximum_position

# Ensure services is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.ingest.archive.downloaders import get_copernicus_dem_features
import imdlib as imd

# IMD Rainfall Categories:
# Light: 2.5 - 15.5 mm
# Moderate: 15.6 - 64.4 mm
# Heavy: 64.5 - 115.5 mm
# Very Heavy: 115.6 - 204.4 mm
# Extremely Heavy: >= 204.5 mm
# Source: https://mausam.imd.gov.in/imd_latest/contents/pdf/glossary.pdf
VERY_HEAVY_THRESHOLD = 115.6

def load_gold_events():
    events_file = "data/events/events.yaml"
    with open(events_file, "r") as f:
        events = yaml.safe_load(f)["events"]
    return events

def detect_auto_events():
    raw_dir = "data/raw/imd"
    out_file = "data/benchmark/events_auto.csv"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    gold_events = load_gold_events()
    gold_event_dates = []
    for ev in gold_events:
        dt = datetime.datetime.strptime(ev["date"], "%Y-%m-%d")
        lat, lon = ev["lat"], ev["lon"]
        gold_event_dates.append({"date": dt, "lat": lat, "lon": lon})
        
    auto_events = []
    
    # Process all available years in data/raw/imd/rain/
    rain_dir = os.path.join(raw_dir, "rain")
    years = []
    if not os.path.exists(rain_dir):
        print(f"Directory {rain_dir} does not exist.")
        return
        
    for file in os.listdir(rain_dir):
        if file.endswith(".grd"):
            try:
                year = int(file.replace(".grd", ""))
                years.append(year)
            except ValueError:
                pass
            
    for year in sorted(years):
        print(f"Scanning year {year} for auto-events...")
        try:
            data = imd.open_data("rain", year, year, "yearwise", raw_dir)
            ds = data.get_xarray()
            
            rain_array = ds.rain.values
            rain_array[rain_array == -999.0] = 0
            
            mask = rain_array >= VERY_HEAVY_THRESHOLD
            labeled, num_features = label(mask)
            
            if num_features == 0:
                continue
                
            max_positions = maximum_position(rain_array, labeled, index=np.arange(1, num_features + 1))
            
            for i, pos in enumerate(max_positions):
                t_idx, lat_idx, lon_idx = pos
                max_rain = rain_array[t_idx, lat_idx, lon_idx]
                n_cells = np.sum(labeled == (i + 1))
                
                event_date = pd.to_datetime(ds.time.values[t_idx]).to_pydatetime()
                event_lat = float(ds.lat.values[lat_idx])
                event_lon = float(ds.lon.values[lon_idx])
                
                is_duplicate = False
                for g in gold_event_dates:
                    dt_diff = abs((event_date - g["date"]).days)
                    dist = np.sqrt((event_lat - g["lat"])**2 + (event_lon - g["lon"])**2)
                    if dt_diff <= 2 and dist <= 0.5:
                        is_duplicate = True
                        break
                        
                if not is_duplicate:
                    auto_events.append({
                        "date": event_date.strftime("%Y-%m-%d"),
                        "lat": event_lat,
                        "lon": event_lon,
                        "max_rain_mm": float(max_rain),
                        "n_cells": int(n_cells),
                        "label_quality": "auto_detected",
                        "source": "imd_top_n"
                    })
                    
        except Exception as e:
            print(f"Failed to scan year {year}: {e}")
            
    auto_events = sorted(auto_events, key=lambda x: x["max_rain_mm"], reverse=True)
    
    cell_counts = {}
    capped_events = []
    dropped = 0
    for ev in auto_events:
        cell = f"{int(np.floor(ev['lat']))}_{int(np.floor(ev['lon']))}"
        if cell_counts.get(cell, 0) < 3:
            capped_events.append(ev)
            cell_counts[cell] = cell_counts.get(cell, 0) + 1
        else:
            dropped += 1
            
    print(f"Dropped {dropped} events due to 3-per-cell cap.")
    auto_events = capped_events[:200]
    
    print(f"Computing DEM features for {len(auto_events)} events...")
    
    # Pre-load existing dem stats
    existing_dem = {}
    try:
        old_df = pd.read_csv(out_file)
        for _, r in old_df.iterrows():
            k = f"{r['lat']}_{r['lon']}"
            existing_dem[k] = {
                "elev_mean_m": r.get("elev_mean_m", np.nan),
                "elev_max_m": r.get("elev_max_m", np.nan),
                "relief_m": r.get("relief_m", np.nan),
                "slope_mean_deg": r.get("slope_mean_deg", np.nan)
            }
    except:
        pass
        
    for idx, ev in enumerate(auto_events):
        ev["auto_id"] = f"auto-{idx+1:03d}"
        k = f"{ev['lat']}_{ev['lon']}"
        if k in existing_dem and not np.isnan(existing_dem[k].get("elev_mean_m", np.nan)):
            ev.update(existing_dem[k])
        else:
            window = 0.25
            bbox = [ev["lon"] - window/2, ev["lat"] - window/2, ev["lon"] + window/2, ev["lat"] + window/2]
            dem_stats = get_copernicus_dem_features(bbox)
            ev.update(dem_stats)
            print(f"Fetched DEM for new event at {ev['lat']}, {ev['lon']}")
        
    df = pd.DataFrame(auto_events)
    cols = ["auto_id", "date", "lat", "lon", "max_rain_mm", "n_cells", "label_quality", "source", 
            "elev_mean_m", "elev_max_m", "relief_m", "slope_mean_deg"]
    if not df.empty:
        df = df[cols]
    else:
        df = pd.DataFrame(columns=cols)
    df.to_csv(out_file, index=False)
    print(f"Saved {len(df)} auto-detected events to {out_file}")

if __name__ == "__main__":
    detect_auto_events()

import os
import sys
import yaml
import pandas as pd
import numpy as np
import datetime
import random

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from imd_utils import extract_point_rainfall_stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.ingest.archive.downloaders import get_copernicus_dem_features

def fetch_imd_rainfall(year):
    import imdlib as imd
    raw_dir = "data/raw/imd"
    try:
        return imd.open_data("rain", year, year, "yearwise", raw_dir)
    except:
        return None

def load_all_events():
    with open("data/events/events.yaml", "r") as f:
        gold = yaml.safe_load(f)["events"]
    try:
        auto_df = pd.read_csv("data/benchmark/events_auto.csv")
        all_events = [{"lat": r["lat"], "lon": r["lon"], "date": r["date"]} for _, r in auto_df.iterrows()]
    except:
        all_events = []
    for g in gold:
        all_events.append({"lat": g["lat"], "lon": g["lon"], "date": g["date"]})
    return gold, all_events

def is_too_close(date_str, all_events):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    for ev in all_events:
        edt = datetime.datetime.strptime(ev["date"], "%Y-%m-%d")
        if abs((dt - edt).days) <= 3:
            return True
    return False

def sample_controls():
    random.seed(42)
    gold_events, all_events = load_all_events()
    
    raw_dir = "data/raw/imd"
    rain_dir = os.path.join(raw_dir, "rain")
    available_years = []
    if os.path.exists(rain_dir):
        for file in os.listdir(rain_dir):
            if file.endswith(".grd"):
                try: available_years.append(int(file.replace(".grd", "")))
                except: pass
    
    controls = []
    imd_ds = {}
    for y in available_years:
        data = fetch_imd_rainfall(y)
        if data is not None: imd_ds[y] = data.get_xarray()
        
    all_years_datasets = imd_ds
    
    target_N = 5
    valid_candidates_count = {}
    
    for ev in gold_events:
        dt = datetime.datetime.strptime(ev["date"], "%Y-%m-%d")
        
        def get_all_candidates(window_days):
            cands = []
            for y in sorted(available_years):
                if y == dt.year: continue
                try: base_dt = datetime.datetime(y, dt.month, dt.day)
                except ValueError:
                    if dt.month == 2 and dt.day == 29: base_dt = datetime.datetime(y, 2, 28)
                    else: continue
                for offset in range(-window_days, window_days + 1):
                    cand_dt = base_dt + datetime.timedelta(days=offset)
                    if cand_dt.year == y: cands.append(cand_dt)
            random.shuffle(cands)
            return cands
        
        def filter_and_evaluate(cands):
            valid_res = []
            for cand_dt in cands:
                day_str = cand_dt.strftime("%Y-%m-%d")
                if is_too_close(day_str, all_events): continue
                y = cand_dt.year
                ds = imd_ds.get(y)
                if ds is None: continue
                res = extract_point_rainfall_stats(ds, ev["lat"], ev["lon"], day_str)
                if not res.get("is_valid"): continue
                if np.isnan(res["rain_3day_max"]) or res["rain_3day_max"] >= 2.5: continue
                
                clean = res.get("rain_widepeak_mm", np.nan) < 2.5
                valid_res.append((cand_dt, res, clean))
            return valid_res

        def pick_controls(valid_cands):
            valid_cands.sort(key=lambda x: not x[2])
            picked = []
            picked_years = set()
            picked_dts = []
            for cand_dt, res, clean in valid_cands:
                if len(picked) >= target_N: break
                if cand_dt.year in picked_years: continue
                
                too_close_to_picked = False
                for p_dt in picked_dts:
                    if abs((cand_dt - p_dt).days) < 7:
                        too_close_to_picked = True
                        break
                if too_close_to_picked: continue
                
                picked.append((cand_dt, res, clean))
                picked_years.add(cand_dt.year)
                picked_dts.append(cand_dt)
            return picked
            
        cands_15 = get_all_candidates(15)
        valid_15 = filter_and_evaluate(cands_15)
        valid_candidates_count[ev["id"]] = len(valid_15)
        
        picked_controls = pick_controls(valid_15)
        window_used = 15
        
        if len(picked_controls) < 3:
            cands_30 = get_all_candidates(30)
            valid_30 = filter_and_evaluate(cands_30)
            picked_controls = pick_controls(valid_30)
            window_used = 30
            
        for i, (cand_dt, _, clean) in enumerate(picked_controls):
            day_str = cand_dt.strftime("%Y-%m-%d")
            ds = imd_ds[cand_dt.year]
            res = extract_point_rainfall_stats(ds, ev["lat"], ev["lon"], day_str, all_years_datasets=all_years_datasets)
            
            if ev.get("geometry_type") == "region": bbox = ev["bbox"]
            else:
                w = 0.25
                bbox = [ev["lon"] - w/2, ev["lat"] - w/2, ev["lon"] + w/2, ev["lat"] + w/2]
            dem_stats = get_copernicus_dem_features(bbox)
            
            controls.append({
                "control_id": f"{ev['id']}-ctrl-{i+1}",
                "parent_event_id": ev["id"],
                "date": day_str,
                "lat": ev["lat"],
                "lon": ev["lon"],
                "label": "no_event",
                "rain_event_day_mm": round(res["rain_event_day_mm"], 1),
                "rain_peak_mm": round(res["rain_peak_mm"], 1),
                "rain_peak_date": res["rain_peak_date"],
                "rain_3day_mm": round(res["rain_3day_mm"], 1),
                "rain_wetday_percentile": round(res.get("rain_wetday_percentile", np.nan), 1),
                "percentile_baseline": "2000-2024 wet days (>=2.5 mm) at the used cell",
                "rain_peak_offset_days": res.get("rain_peak_offset_days", np.nan),
                "rain_widepeak_mm": round(res.get("rain_widepeak_mm", np.nan), 1),
                "control_clean": clean,
                "season_window_days": window_used,
                "offset_days": (cand_dt - (datetime.datetime(cand_dt.year, dt.month, dt.day) if not (dt.month == 2 and dt.day == 29) else datetime.datetime(cand_dt.year, 2, 28))).days,
                "rain_cell_lat": round(res["cell_lat"], 4),
                "rain_cell_lon": round(res["cell_lon"], 4),
                "rain_cell_fallback": res["fallback"],
                "rain_cell_distance_km": round(res["distance_km"], 2),
                "elev_mean_m": dem_stats.get("elev_mean_m", np.nan),
                "elev_max_m": dem_stats.get("elev_max_m", np.nan),
                "relief_m": dem_stats.get("relief_m", np.nan),
                "slope_mean_deg": dem_stats.get("slope_mean_deg", np.nan)
            })
            
    df = pd.DataFrame(controls)
    df.to_csv("data/benchmark/controls.csv", index=False)
    
    print("\n--- VALID CANDIDATE COUNTS (+/- 15 DAYS) ---")
    sorted_counts = sorted(valid_candidates_count.items(), key=lambda x: x[1])
    for k, v in sorted_counts:
        print(f"{k}: {v}")

if __name__ == "__main__":
    sample_controls()
